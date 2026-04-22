# 企业级插装阀资料管理平台

一个面向企业内部的中文化平台，用于管理插装阀产品资料（PDF），并提供角色权限与客户管理能力。

## 核心能力

- **插装阀目录导航**：提供产品目录首页、分面筛选、型号明细页、SUN 型号替代查询和解决方案入口。
- **中文界面**：系统页面、提示语全部中文。
- **型号 PDF 管理**：管理员可在插装阀明细页上传/删除 PDF，全部登录用户可在明细页下载和在线预览。
- **权限区分**：
  - 管理员：资料上传/删除、客户新增/编辑/删除。
  - 普通用户：资料查看/预览/下载、客户查看。
- **客户管理**：含基础客户档案（可后续扩展更多字段和业务流程）。
- **PostgreSQL 数据库**：生产部署使用 PostgreSQL，目录、附件、客户和询价扩展均由数据库承载。
- **可云端部署**：提供 Docker + PostgreSQL 部署方式，可直接在云服务器运行。

## 快速启动（本地）

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
docker compose -f docker-compose.prod.yml up -d --build
```

如果只想本地用 Python 启动应用，则先启动 PostgreSQL，并把 `.env` 中的 `DATABASE_URL` 改为 `localhost`：

```bash
docker compose -f docker-compose.prod.yml up -d db
# DATABASE_URL=postgresql+psycopg2://valve:valve-password@localhost:5432/valve
python run.py
```

访问：`http://localhost:8000`

默认管理员账号来自 `.env`：
- 用户名：`admin`
- 密码：`Admin@123`

运行测试：

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

## Docker 启动

```bash
cp .env.example .env
docker compose -f docker-compose.prod.yml up -d --build
```

## 试用上线建议

如果你想先给企业同事试用，建议直接走 Docker 部署：

```bash
cp .env.example .env
```

至少修改这些配置：

- `SECRET_KEY`
- `ADMIN_PASSWORD`
- `SHOW_DEMO_CREDENTIALS=false`

然后用编排方式启动：

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

默认会把容器 `8000` 端口绑定到服务器本机 `127.0.0.1:8000`，推荐再用 Nginx 对外代理：

```text
http://<你的域名或服务器IP>
```

健康检查地址：

```text
http://127.0.0.1:8000/healthz
```

如果你有自己的域名，推荐这样部署：

1. 用 `docker compose -f docker-compose.prod.yml up -d --build` 启动应用。
2. 应用会监听服务器本机 `127.0.0.1:8000`。
3. 用 Nginx 反向代理域名到 `127.0.0.1:8000`。
4. 再用 Certbot 给域名申请 HTTPS 证书。

项目里已经提供了 Nginx 示例配置：

```text
deploy/nginx/yinyu990201.com.conf.example
```

## 文档

- 需求分析文档：`docs/01-需求分析文档.md`
- 体系架构设计文档：`docs/02-体系架构设计文档.md`
- 应用部署文档：`docs/03-应用部署文档.md`
- 重构更新日志：`docs/04-重构更新日志.md`
- 数据结构设计文档：`docs/05-数据结构设计文档.md`
- 数据库切换说明：`docs/06-数据库切换说明.md`

## 更新日志

### 2026-04-21 - 产品目录与前端交互重构

- 新增插装阀目录导航页：支持关键词、功能分类、控制问题、通口数、流量范围、压力等级、插孔型号和结构特征筛选。
- 目录筛选栏支持折叠展开，产品结果支持分页浏览，筛选操作按钮调整到更方便的位置。
- 新增型号明细页：展示液压符号示意、关键规格、SUN 参考型号、典型应用和询价入口。
- 新增 SUN 型号替代页、解决方案页、联系询价页。
- 重做全站顶部导航和视觉系统，页面结构调整为更接近工业产品目录的导航页/结果区/明细页模式。
- PDF 上传、预览、下载和删除整合到插装阀型号明细页；旧资料路由保留为跳转兼容。
- 保留客户档案、登录权限、Docker、Nginx 和健康检查能力。
- 新增 `tests/test_app.py`，覆盖目录、明细、解决方案、替代查询、询价预填、PDF 上传和普通用户权限。

### 2026-04-22 - PostgreSQL 与后端数据层重构

- 将生产数据库切换为 PostgreSQL，并在 `docker-compose.prod.yml` 中新增 `db` 服务。
- 将插装阀目录从静态常量迁移为数据库表驱动，应用启动时自动种子化默认目录数据。
- 扩展数据模型，覆盖用户、产品分类、控制功能、型号、标签、特性、应用、替代关系、型号 PDF、客户、联系人和询价。
- 新增 `docs/05-数据结构设计文档.md` 和 `docs/06-数据库切换说明.md`。
