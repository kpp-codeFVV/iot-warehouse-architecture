# Local Setup - IoT 智能仓储监控与告警平台

本文档说明如何在本地运行当前原型。

## 1. 环境要求

- Python 3.12
- Windows PowerShell
- 可选：Docker Desktop

当前开发机器已验证 Python `.venv` 方式。Docker Desktop 和 Docker Compose CLI 已安装，但 Docker Desktop 后端服务尚未成功启动；当前阻塞点是 WSL/服务启动需要管理员权限。因此 `docker compose up` 尚未在本机完整验证。

## 2. 安装依赖

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 3. 设置环境变量

```powershell
$env:IOT_DATA_DIR = "$(Get-Location)\runtime"
$env:PYTHONPATH = "$(Get-Location)"
$env:INVENTORY_URL = "http://localhost:8002"
```

## 4. 启动三个服务

打开三个 PowerShell 窗口，分别运行：

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --app-dir apps/inventory-service --port 8002
```

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --app-dir apps/alert-service --port 8003
```

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --app-dir apps/device-gateway --port 8001
```

## 5. 健康检查

```powershell
Invoke-RestMethod http://localhost:8001/health
Invoke-RestMethod http://localhost:8002/health
Invoke-RestMethod http://localhost:8003/health
```

## 6. Docker Compose 启动

如果机器已安装 Docker Desktop：

```powershell
docker compose up
```

该命令会启动 Mosquitto、Redis、TimescaleDB 和三个 FastAPI 服务。当前机器已安装 Docker CLI，但 Docker daemon 尚未可用；需要先以管理员权限完成 WSL/Docker Desktop 初始化后再补充验证。

可先检查 Docker CLI：

```powershell
docker --version
docker compose version
```

当前已验证版本：

```text
Docker version 29.5.2
Docker Compose version v5.1.4
```

## 7. 清理运行数据

```powershell
Remove-Item -Recurse -Force runtime -ErrorAction SilentlyContinue
```
