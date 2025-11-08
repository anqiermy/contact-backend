一、总体原则
1. 遵循PEP 8 Python代码风格，保持代码格式统一。
2. 贴合项目技术栈（Python + Flask + SQLAlchemy + SQLite），不引入冗余功能。
3. 单一职责：每个函数/类只处理一类业务（如联系人管理、分组操作）。
4. 提交前用Black格式化、Flake8检查，确保格式正确。

 二、文件与命名规范
1. 文件名：小写+下划线（snake_case），如`app.py`、`contact_model.py`
2. 类名：首字母大写（PascalCase），对应模型，如`User`、`Contact`、`Group`
3. 函数/方法名：小写+下划线，动词开头，如`add_contact()`、`get_groups()`
4. 变量名：小写+下划线，如`user_id`、`contact_list`；常量全大写，如`DB_URI`
5. 数据库：表名、字段名小写+下划线，外键格式`<表名>_id`（如`group_id`）

三、代码风格
1. 缩进：4个空格，不使用Tab。
2. 行长度：≤79字符，超长时换行，如：
   ```python
   contacts = Contact.query.filter(
       Contact.user_id == user_id,
       Contact.group_id == group_id
   ).all()
   ```
3. 空行：函数/类间空2行，类内方法间空1行。
4. 导入顺序：标准库→第三方库→本地模块，不同类型间空1行。
5. 类型提示：标注参数和返回值类型

四、Flask实践
1. 路由：统一前缀`/api`，方法与功能对应（GET查、POST增等），如：
   - `/api/login`（POST）、`/api/contacts`（GET/POST）
2. 蓝图：按功能拆分（`auth_bp`、`contact_bp`），在`app.py`注册。
3. 请求响应：
   - 请求用`request.get_json()`解析，先校验非空。
   - 响应格式：
     - 成功：`{"success": True, "message": "...", "data": {...}}`
     - 失败：`{"success": False, "message": "..."}`
4. 装饰器：仅用`login_required`验证`X-User-Id`请求头。


 五、数据库规范
1. 模型设计：对应3张表，字段与实际一致
2. 操作：
   - 连接配置：`sqlite:///src/contacts.db`
   - 查询用模型方法（如`filter_by(user_id=user_id)`）。
   - 增删改需`commit()`，异常时`rollback()`。


 六、审查重点
1. 命名是否符合项目现有风格。
2. 函数是否单一职责，无冗余逻辑。
3. 数据库操作是否有事务处理（`commit`/`rollback`）。
4. 响应格式是否与前端约定一致。
