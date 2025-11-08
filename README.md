# contact-backend
通讯录系统后端

## 项目介绍
通讯录管理系统后端，基于 Flask 开发 RESTful API，负责业务逻辑处理与 SQLite 数据存储，支持前端请求响应。

## 技术栈
- 开发框架：Python Flask
- ORM 工具：Flask-SQLAlchemy
- 数据库：SQLite（轻量本地数据库，无需额外部署）
- 跨域处理：Flask-CORS
- 生产部署：Gunicorn（Python WSGI 服务器）

## 核心接口
| 接口路径         | HTTP 方法 | 功能描述                |
|------------------|-----------|-------------------------|
| `/api/login`     | POST      | 用户登录（账号密码校验）|
| `/api/register`  | POST      | 用户注册（账号唯一性校验）|
| `/api/contacts`  | GET       | 获取联系人（支持筛选/搜索）|
| `/api/contacts`  | POST      | 添加联系人              |
| `/api/contacts`  | PUT       | 修改联系人              |
| `/api/contacts`  | DELETE    | 删除联系人              |
| `/api/groups`    | GET       | 获取用户分组            |
| `/api/groups`    | POST      | 添加分组                |


## 本地运行步骤
1. 克隆仓库到本地
2. 安装依赖：`pip install -r requirements.txt`
3. 初始化数据库：运行 `src/models/__init__.py`（自动创建 SQLite 数据库文件）
4. 启动服务：`python src/app.py`（默认端口 5000，API 根地址：`http://localhost:5000/api`）

## 部署说明
1. 服务器安装依赖：`pip install -r requirements.txt` 和 `pip install gunicorn`
2. 初始化数据库：`python src/models/__init__.py`
3. 后台启动服务：`nohup gunicorn -w 4 -b 0.0.0.0:5000 src.app:app &`
4. 查看服务状态：`ps -ef | grep gunicorn`，停止服务：`kill -9 进程ID`
