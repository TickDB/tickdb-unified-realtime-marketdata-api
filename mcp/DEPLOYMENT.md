# TickDB MCP — 自部署指南

**语言：** **简体中文** · [繁體中文](docs/tw/DEPLOYMENT.md) · [English](docs/en/DEPLOYMENT.md)

本仓库的 `mcp/` 是可独立运行的开源 Python MCP 服务。v0.2.3 提供 43 个工具（13 行情 + 29 公司财务与事件 + 1 API Key 订阅），支持外汇、贵金属、指数、美股、港股、A 股、中港期货与加密货币。

要求 Python 3.11+，或 Docker；以下说明以 Linux / Bash 为基准。行情查询与 OAuth Key 验证均需访问 `api.tickdb.ai`。HTTP 默认监听 8000 端口；公网 OAuth 需要 HTTPS 域名。

## 本地 / VPS：首次安装

以下命令从本仓库根目录开始执行。若已在 `mcp/` 内，省略 `cd mcp`。首次安装复制模板；升级时保留原 `.env`。

```bash
cd mcp
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
cp .env.example .env
```

### 配置 API Key 与服务

在 `.env` 中按需设置：`X-TickDB-Key` 请求头优先，`TICKDB_API_KEY` 是服务器备用 Key。若不设置服务器 Key，客户端必须自带 Key。公网 Header 服务可设置 `MCP_ACCESS_TOKEN`，客户端同时传 `Authorization: Bearer <token>`。

```dotenv
TICKDB_API_KEY=
MCP_ACCESS_TOKEN=
MCP_TRANSPORT=streamable-http
MCP_HOST=0.0.0.0
MCP_PORT=8000
MCP_STATELESS_HTTP=true
MCP_SESSION_LOG_TTL_SECONDS=3600
MCP_SESSION_LOG_MAX_ENTRIES=1000
LOG_LEVEL=INFO
LOG_RETAIN_DAYS=7
LOG_DIR=logs
OAUTH_ENABLED=false
```

### 启动与验证

从 `mcp/` 目录启动服务，在已激活的虚拟环境中执行 `python main.py`；新开终端时先进入 `mcp/` 并运行 `source .venv/bin/activate`。HTTP 工具地址为 `http://localhost:8000/mcp`。在另一个终端执行以下初始化，仅验证 MCP 协议，不会调用真实行情 API。

```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}'
```

若配置了 `MCP_ACCESS_TOKEN`，加 `-H "Authorization: Bearer YOUR_MCP_ACCESS_TOKEN"`。响应包含 `serverInfo.name` 为 `tickdb-market-data` 即表示初始化成功。日志写入 stderr，目录可写时也保存到 `LOG_DIR`；日志目录不可写时继续使用 stderr。

本地 stdio：在客户端环境中设置 `MCP_TRANSPORT=stdio` 和 `TICKDB_API_KEY`，由客户端启动 Python。stdio 不启动 HTTP 或加载 OAuth 数据库；完整客户端配置见 [接入指南](MCP_CLIENT_SETUP.md)。

## Docker：从公开源码构建

在 `mcp/` 目录构建。首次安装先复制 `.env.example` 为 `.env` 并按上节配置；构建上下文已排除 `.env`、虚拟环境、数据和日志。执行以下命令：

```bash
docker build -t tickdb-mcp:0.2.3 .
docker volume create tickdb-mcp-data
docker run -d --restart unless-stopped -p 127.0.0.1:8000:8000 --env-file .env -v tickdb-mcp-data:/app/data --name tickdb-mcp tickdb-mcp:0.2.3
docker logs -f tickdb-mcp
```

`127.0.0.1` 绑定适合本机客户端或同机反向代理。若需其他机器直接接入，按自己的网络与访问控制配置监听地址。容器工作目录为 `/app`，`data/oauth.sqlite3` 存入 `/app/data` 持久卷。依赖和源码在镜像中，配置通过 `.env` 注入。修改 `--env-file` 的内容后需重新创建容器；普通 `docker restart` 不会更新已注入的环境变量。

## 可选：启用网页版 OAuth

默认 `OAUTH_ENABLED=false`。GPT / Claude 网页版使用独立 `/oauth` 工具入口；`/mcp` Header 和 stdio 为独立接入方式。OAuth 只使用用户授权绑定的 Key。

仅首次安装、尚无数据库和加密密钥时生成一次 Fernet 密钥（虚拟环境已激活，Python 已安装项目依赖）。执行以下命令：

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

将输出固定保存到 `.env` 的 `OAUTH_ENCRYPTION_KEY`，并加入以下配置。示例域名和密钥占位符必须替换：

```dotenv
OAUTH_ENABLED=true
OAUTH_PUBLIC_URL=https://mcp.example.com
OAUTH_DATABASE_PATH=data/oauth.sqlite3
OAUTH_ENCRYPTION_KEY=REPLACE_WITH_THE_GENERATED_FERNET_KEY
OAUTH_REDIRECT_URIS=["https://chatgpt.com/connector_platform_oauth_redirect","https://claude.ai/api/mcp/auth_callback"]
```

- `OAUTH_PUBLIC_URL` 是 HTTPS origin，不带路径、查询参数或 fragment；当前不支持反向代理子路径挂载。
- 回调地址必须完整且精确匹配，不使用通配符。模板默认仅包含 ChatGPT；使用 Claude 时按上面的配置加入其回调并保留其他既有地址。
- 本地 SQLite 适合单实例持久磁盘。服务账户须能写入数据库目录；容器必须保留同一 `/app/data` 数据卷。新数据库文件权限为 0600，父目录为 0700（平台支持时）。
- 加密密钥、数据库、公开 origin 与回调配置须跨重启和升级保留。分别安全备份密钥与数据库，不将它们提交到 Git 或打入镜像。
- 不要多实例共享网络文件系统上的 SQLite；多节点服务需要另行实现共享事务存储。

重启本地服务，或用同一 `.env` 和数据卷重新创建 Docker 容器。客户端 URL 为 `https://mcp.example.com/oauth`，认证选 OAuth，客户端 ID/Secret 留空，通过授权页验证并确认自己的 Key。协议、发现及回调细节见 [OAuth 配置与升级说明](README.md#oauth-setup)。

## HTTPS / Nginx 反向代理

为自己的域名申请证书后，将整个 origin 的路径原样转发到应用，包括 `/mcp`、`/oauth`、授权元数据、注册、授权页面、令牌和撤销路径：

```nginx
server {
    listen 443 ssl;
    server_name mcp.example.com;

    ssl_certificate     /etc/letsencrypt/live/mcp.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/mcp.example.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Connection "";
        proxy_buffering off;
        proxy_read_timeout 300s;
    }
}
```

关闭代理缓冲并设置足够的读取超时，以支持 SSE。不要把所有 OAuth 路径重写到 `/mcp`，也不要只代理一个工具路径。

## Linux 后台运行

可将以下内容保存为 `/etc/systemd/system/tickdb-mcp.service`。先创建普通服务账户 `tickdb`，替换安装绝对路径，并授予该账户读取配置、写入数据与日志目录的权限。应用从工作目录读取 `.env`：

```ini
[Unit]
Description=TickDB MCP Server
After=network.target

[Service]
User=tickdb
WorkingDirectory=/absolute/path/to/repository/mcp
ExecStart=/absolute/path/to/repository/mcp/.venv/bin/python /absolute/path/to/repository/mcp/main.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now tickdb-mcp
sudo systemctl status tickdb-mcp
```

## Railway / Render 等云平台

可以使用公开源码的 `mcp/Dockerfile`，或将构建根目录设为 `mcp/`。在平台环境变量中配置 Key、监听端口及可选 OAuth 参数，并使用 HTTPS 域名。启用 OAuth 时，先配置持久化磁盘并将 `OAUTH_DATABASE_PATH` 指向挂载目录；无持久盘的临时实例不适合保存 OAuth 授权。平台部署不会代替回调白名单和加密密钥配置。

## 升级与持久化

1. 备份原 `.env`、OAuth 加密密钥与数据库。备份 SQLite 时使用 SQLite backup API，或停止服务后备份，确保备份一致。
2. 替换源码并在原虚拟环境运行 `python -m pip install -e .`；Docker 则构建新镜像，保留原配置和同一数据卷，仅替换容器与镜像。
3. 保留 `OAUTH_ENCRYPTION_KEY`、数据库文件与路径、`OAUTH_PUBLIC_URL`、回调白名单、注册客户端和有效授权；不要重新生成密钥、删除数据库或重置授权。
4. 重新启动后检查 MCP 初始化和客户端工具发现。保留原镜像与备份以便回滚；普通升级无需用户重新绑定 Key。

## 环境变量参考

| 变量 | 默认值 | 说明 |
|---|---|---|
| `TICKDB_API_KEY` | 空 | 备用服务器 Key；OAuth 不使用此 Key |
| `MCP_ACCESS_TOKEN` | 空 | 仅保护请求头接入 `/mcp` 的固定 Bearer Token |
| `MCP_TRANSPORT` | `streamable-http` | HTTP 或本地 stdio |
| `MCP_HOST` | `0.0.0.0` | 监听地址 |
| `MCP_PORT` | `8000` | 监听端口 |
| `MCP_STATELESS_HTTP` | `true` | 无状态 HTTP，避免积累遗留会话 |
| `MCP_SESSION_LOG_TTL_SECONDS` | `3600` | 会话 ID 日志缓存的保留秒数 |
| `MCP_SESSION_LOG_MAX_ENTRIES` | `1000` | 会话 ID 日志缓存条数上限 |
| `LOG_LEVEL` | `INFO` | stderr 和文件日志级别 |
| `LOG_RETAIN_DAYS` | `7` | 日志文件保留天数 |
| `LOG_DIR` | `logs` | 文件日志目录，相对工作目录或绝对路径 |
| `OAUTH_ENABLED` | `false` | 是否启用独立 OAuth HTTP 入口 |
| `OAUTH_PUBLIC_URL` | 空 | OAuth HTTPS origin |
| `OAUTH_DATABASE_PATH` | `data/oauth.sqlite3` | 持久 SQLite 路径 |
| `OAUTH_ENCRYPTION_KEY` | 空 | 首次生成并固定保存的 Fernet 密钥 |
| `OAUTH_REDIRECT_URIS` | `[]` | 精确回调 JSON 数组；模板含 ChatGPT 回调 |

## 常见问题

- `Address already in use`：调整 `.env` 中的 `MCP_PORT`，并同步客户端 URL 或代理目标。
- `No TickDB API key provided` / `1001`：检查客户端 `X-TickDB-Key` 或服务器 `TICKDB_API_KEY`。`1005` 表示 Key 已过期。
- OAuth 启动失败：检查 HTTPS origin、Fernet 密钥、回调 JSON 与数据库写权限；已有数据库须使用对应密钥和 origin。
- 重启后授权丢失：检查数据库是否在同一持久数据卷内，配置是否保留。
- Nginx 调用超时：检查代理路径、`proxy_buffering off` 和 `proxy_read_timeout`。
