# Local Setup - IoT 智能仓储监控与告警平台

本文档说明如何在本地运行当前原型。

## 1. 环境要求

- Python 3.12
- Windows PowerShell
- 可选：Docker Desktop

当前开发机器已验证 Python `.venv` 方式。当前机器未安装 Docker，因此 `docker compose up` 尚未在本机验证。

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

该命令会启动 Mosquitto、Redis、TimescaleDB 和三个 FastAPI 服务。当前机器未安装 Docker，因此此命令需要在安装 Docker 后补充验证。

## 7. 清理运行数据

```powershell
Remove-Item -Recurse -Force runtime -ErrorAction SilentlyContinue
```

