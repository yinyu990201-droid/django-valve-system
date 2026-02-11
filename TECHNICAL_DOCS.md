# 插装阀系统 (Valve System) 技术运维文档

## 1. 项目概况

### 1.1 项目简介
本项目是一个基于 Django 框架开发的插装阀产品与技术文档管理系统。主要用于企业内部管理插装阀产品的详细信息、技术参数以及关联的 PDF 技术文档。系统支持产品的分类展示、详情查看以及文档的上传与下载。

### 1.2 技术栈
- **编程语言**: Python 3.8+
- **Web 框架**: Django 4.2
- **数据库**: SQLite (默认开发库，可切换为 MySQL/PostgreSQL)
- **前端技术**: Django Templates + Bootstrap 5
- **依赖管理**: pip + requirements.txt

---

## 2. 环境搭建与部署

### 2.1 基础环境准备
部署服务器需安装以下软件：
- Python 3.8 或更高版本
- Git (用于代码拉取)
- pip (Python 包管理工具)

### 2.2 安装步骤

1.  **获取代码**
    ```bash
    git clone <repository_url>
    cd django-valve-system
    ```

2.  **创建虚拟环境 (推荐)**
    为了避免依赖冲突，建议创建独立的 Python 虚拟环境。
    ```bash
    # Windows
    python -m venv venv
    .\venv\Scripts\activate

    # Linux/MacOS
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **安装依赖**
    ```bash
    pip install -r requirements.txt
    ```
    *注：`requirements.txt` 包含了 Django, django-bootstrap-v5, django-filter 等核心依赖。*

4.  **初始化数据库**
    ```bash
    cd valve_system
    python manage.py migrate
    ```

5.  **创建管理员账号**
    用于登录后台管理数据。
    ```bash
    python manage.py createsuperuser
    # 按提示输入用户名、邮箱和密码
    ```

6.  **收集静态文件 (生产环境)**
    ```bash
    python manage.py collectstatic
    ```

---

## 3. 项目配置说明

核心配置文件位于 `valve_system/valve_system/settings.py`。

### 3.1 关键配置项

| 配置变量 | 说明 | 运维建议 |
| :--- | :--- | :--- |
| `DEBUG` | 调试模式开关 | **生产环境务必设置为 `False`** |
| `SECRET_KEY` | 加密密钥 | 生产环境请修改为随机生成的复杂字符串，并保密 |
| `ALLOWED_HOSTS` | 允许访问的域名/IP | 生产环境需填入服务器 IP 或域名，如 `['192.168.1.100', 'example.com']` |
| `DATABASES` | 数据库配置 | 默认使用 SQLite。如需切换 MySQL，需安装 `mysqlclient` 并修改此段配置 |
| `STATIC_ROOT` | 静态文件收集目录 | 执行 `collectstatic` 后文件会存放于此，Nginx 需指向此目录 |
| `MEDIA_ROOT` | 用户上传文件目录 | 存放 PDF 文档和图片，需确保操作系统对此目录有读写权限 |

### 3.2 环境变量 (.env)
项目支持使用 `.env` 文件管理敏感信息（需确认代码中是否启用了 `python-dotenv`）。
建议在项目根目录下创建 `.env` 文件：
```env
DEBUG=False
SECRET_KEY=your-production-secret-key
```

---

## 4. 启动与运行

### 4.1 开发模式启动
用于本地测试或临时调试。
```bash
python manage.py runserver 0.0.0.0:8000
```
访问地址: `http://localhost:8000`

### 4.2 生产环境建议 (Linux)
建议使用 **Gunicorn** 作为应用服务器，**Nginx** 作为反向代理。

1.  **安装 Gunicorn**
    ```bash
    pip install gunicorn
    ```

2.  **启动 Gunicorn**
    ```bash
    gunicorn valve_system.wsgi:application --bind 0.0.0.0:8000 --workers 3
    ```

3.  **Nginx 配置示例**
    ```nginx
    server {
        listen 80;
        server_name your_domain.com;

        location = /favicon.ico { access_log off; log_not_found off; }

        # 静态文件
        location /static/ {
            alias /path/to/django-valve-system/valve_system/staticfiles/;
        }

        # 上传的媒体文件 (PDF/图片)
        location /media/ {
            alias /path/to/django-valve-system/valve_system/media/;
        }

        # 代理到 Gunicorn
        location / {
            proxy_pass http://127.0.0.1:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
    ```

---

## 5. 运维管理操作

### 5.1 数据备份
- **SQLite**: 直接复制 `valve_system/db.sqlite3` 文件即可。
- **媒体文件**: 定期备份 `valve_system/media/` 目录，其中包含了所有上传的 PDF 和图片。

### 5.2 数据库迁移
当代码更新涉及数据模型变更时，需执行：
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5.3 后台管理
访问 `/admin/` 进入 Django 管理后台。
- **Products**: 管理插装阀与产品信息。
- **Categories**: 管理产品分类。
- **Valve Documents**: 上传和管理技术文档 (PDF)。
- **Users**: 管理系统用户。

---

## 6. 常见故障排查

### Q1: 静态文件丢失 (样式失效)
- **现象**: 页面排版混乱，CSS 未加载。
- **解决**: 
    1. 确保 `DEBUG = False` 时已正确配置 Nginx 处理 `/static/`。
    2. 执行 `python manage.py collectstatic` 重新收集静态文件。

### Q2: 无法上传大文件
- **现象**: 上传大型 PDF 时报错或超时。
- **解决**: 检查 Nginx 配置中的 `client_max_body_size`，建议设置为 50M 或更大。

### Q3: 端口被占用
- **现象**: `Error: That port is already in use.`
- **解决**: 使用 `netstat -ano | grep 8000` (Windows) 或 `lsof -i :8000` (Linux) 查找占用进程并终止，或更换端口启动。

### Q4: 数据库锁定 (SQLite)
- **现象**: `OperationalError: database is locked`
- **解决**: SQLite 对并发写入支持有限。如果遇到频繁锁定，建议迁移至 MySQL 或 PostgreSQL。

---
**文档维护人**: 运维组
**最后更新日期**: 2026-02-11
