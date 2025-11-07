from flask import Flask, request, jsonify, g
from flask_cors import CORS
import sqlite3
from functools import wraps
import hashlib
from db import get_db_connection

app = Flask(__name__)

# 跨域配置（适配前端地址）
CORS(
    app,
    resources={r"/api/*": {
        "origins": "http://localhost:63342",
        "allow_headers": ["Content-Type", "X-User-Id"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    }}
)


# 处理OPTIONS预检请求
@app.before_request
def handle_preflight():
    if request.method == 'OPTIONS':
        return jsonify({"status": "ok"}), 200


# 密码加密
def encrypt_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# 登录验证装饰器
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user_id = request.headers.get('X-User-Id')
        if not user_id:
            return jsonify({"error": "请先登录"}), 401

        conn = get_db_connection()
        user = conn.execute('SELECT id FROM users WHERE id = ?', (user_id,)).fetchone()
        conn.close()
        if not user:
            return jsonify({"error": "用户不存在"}), 401

        g.user_id = user_id
        return f(*args, **kwargs)

    return decorated


# 1. 注册接口
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    email = data.get('email', '').strip()

    if not username or not password:
        return jsonify({"error": "用户名和密码不能为空"}), 400

    conn = get_db_connection()
    try:
        # 检查用户名是否存在
        if conn.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone():
            return jsonify({"error": "用户名已存在"}), 400

        # 插入新用户
        cursor = conn.execute(
            'INSERT INTO users (username, password, email) VALUES (?, ?, ?)',
            (username, encrypt_password(password), email)
        )
        user_id = cursor.lastrowid

        # 添加默认分组
        conn.execute(
            'INSERT INTO groups (group_name, user_id) VALUES (?, ?)',
            ('未分组', user_id)
        )
        conn.commit()
        return jsonify({"message": "注册成功", "user_id": user_id}), 201
    except sqlite3.Error as e:
        conn.rollback()
        return jsonify({"error": f"注册失败：{str(e)}"}), 500
    finally:
        conn.close()


# 2. 登录接口
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    conn = get_db_connection()
    user = conn.execute(
        'SELECT id, username, password FROM users WHERE username = ?',
        (username,)
    ).fetchone()
    conn.close()

    if not user or user['password'] != encrypt_password(password):
        return jsonify({"error": "用户名或密码错误"}), 401

    return jsonify({
        "message": "登录成功",
        "user_id": user['id'],
        "username": user['username']
    }), 200


# 3. 分组接口（获取）
@app.route('/api/groups', methods=['GET'])
@login_required
def get_groups():
    conn = get_db_connection()
    groups = conn.execute(
        'SELECT id, group_name FROM groups WHERE user_id = ?',
        (g.user_id,)
    ).fetchall()
    conn.close()
    return jsonify([dict(g) for g in groups])


# 4. 分组接口（添加）
@app.route('/api/groups', methods=['POST'])
@login_required
def add_group():
    data = request.get_json()
    group_name = data.get('group_name', '').strip()
    if not group_name:
        return jsonify({"error": "分组名称不能为空"}), 400

    conn = get_db_connection()
    try:
        conn.execute(
            'INSERT INTO groups (group_name, user_id) VALUES (?, ?)',
            (group_name, g.user_id)
        )
        conn.commit()
        return jsonify({"message": "分组添加成功"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "分组已存在"}), 400
    finally:
        conn.close()


# 5. 联系人接口（获取）
@app.route('/api/contacts', methods=['GET'])
@login_required
def get_contacts():
    keyword = request.args.get('keyword', '')
    group_id = request.args.get('group_id', '')

    conn = get_db_connection()
    query = 'SELECT name, phone, group_id FROM contacts WHERE user_id = ?'
    params = [g.user_id]

    if keyword:
        query += ' AND (name LIKE ? OR phone LIKE ?)'
        params.extend([f'%{keyword}%', f'%{keyword}%'])
    if group_id and group_id != '0':
        query += ' AND group_id = ?'
        params.append(group_id)

    contacts = conn.execute(query, params).fetchall()
    conn.close()
    return jsonify([dict(c) for c in contacts])


# 6. 联系人接口（添加）
@app.route('/api/contacts', methods=['POST'])
@login_required
def add_contact():
    data = request.get_json()
    name = data.get('name', '').strip()
    phone = data.get('phone', '').strip()
    group_id = data.get('group_id', '').strip()

    if not name:
        return jsonify({"error": "姓名不能为空"}), 400
    if not phone or not phone.isdigit() or len(phone) != 11:
        return jsonify({"error": "请输入11位手机号"}), 400

    conn = get_db_connection()
    try:
        conn.execute(
            'INSERT INTO contacts (name, phone, group_id, user_id) VALUES (?, ?, ?, ?)',
            (name, phone, group_id, g.user_id)
        )
        conn.commit()
        return jsonify({"message": "添加成功"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "手机号已存在"}), 400
    finally:
        conn.close()


# 7. 联系人接口（修改）
@app.route('/api/contacts', methods=['PUT'])
@login_required
def update_contact():
    data = request.get_json()
    old_phone = data.get('old_phone', '').strip()
    new_name = data.get('new_name', '').strip()
    new_phone = data.get('new_phone', '').strip()
    new_group_id = data.get('new_group_id', '').strip()

    if not old_phone or not new_name or not new_phone:
        return jsonify({"error": "信息不完整"}), 400
    if not new_phone.isdigit() or len(new_phone) != 11:
        return jsonify({"error": "请输入11位手机号"}), 400

    conn = get_db_connection()
    try:
        conn.execute(
            'UPDATE contacts SET name=?, phone=?, group_id=? WHERE phone=? AND user_id=?',
            (new_name, new_phone, new_group_id, old_phone, g.user_id)
        )
        if conn.total_changes == 0:
            return jsonify({"error": "联系人不存在"}), 404
        conn.commit()
        return jsonify({"message": "修改成功"}), 200
    except sqlite3.IntegrityError:
        return jsonify({"error": "新手机号已存在"}), 400
    finally:
        conn.close()


# 8. 联系人接口（删除）
@app.route('/api/contacts', methods=['DELETE'])
@login_required
def delete_contact():
    data = request.get_json()
    phone = data.get('phone', '').strip()
    if not phone:
        return jsonify({"error": "手机号不能为空"}), 400

    conn = get_db_connection()
    conn.execute(
        'DELETE FROM contacts WHERE phone=? AND user_id=?',
        (phone, g.user_id)
    )
    if conn.total_changes == 0:
        conn.close()
        return jsonify({"error": "联系人不存在"}), 404
    conn.commit()
    conn.close()
    return jsonify({"message": "删除成功"}), 200


if __name__ == '__main__':
    app.run(debug=True)