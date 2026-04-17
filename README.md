# 企业级插装阀资料管理平台

一个面向企业内部的中文化平台，用于管理插装阀产品资料（PDF），并提供角色权限与客户管理能力。

## 核心能力

- **中文界面**：系统页面、提示语全部中文。
- **PDF 管理**：管理员可上传/删除，全部登录用户可下载和在线预览。
- **权限区分**：
  - 管理员：资料上传/删除、客户新增/编辑/删除。
  - 普通用户：资料查看/预览/下载、客户查看。
- **客户管理**：含基础客户档案（可后续扩展更多字段和业务流程）。
- **可云端部署**：提供 Docker 部署方式，可直接在云服务器运行。

## 快速启动（本地）

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python run.py
```

访问：`http://localhost:8000`

默认管理员账号来自 `.env`：
- 用户名：`admin`
- 密码：`Admin@123`

## Docker 启动

```bash
docker build -t valve-doc-platform .
docker run -d --name valve-doc-platform \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  --env-file .env \
  valve-doc-platform
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

默认会把容器 `8000` 端口映射到服务器 `80` 端口，对外访问地址就是：

```text
http://<你的服务器IP>
```

健康检查地址：

```text
http://<你的服务器IP>/healthz
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
