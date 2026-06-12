# Local Setup - IoT 智能仓储监控与告警平台

本文档说明如何在本地运行当前验证环境。

## 1. 环境要求

- Python 3.12
- Windows PowerShell
- Docker Desktop

本项目支持 Python `.venv` 方式和 Docker Desktop + WSL2 方式。Docker Compose 启动时需要显式指定项目名，因为项目目录包含中文，直接 `docker compose up` 可能报 `project name must not be empty`。

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
docker compose -p iot-warehouse up
```

后台启动：

```powershell
docker compose -p iot-warehouse up -d
```

该命令会启动 Mosquitto、Redis、TimescaleDB 和三个 FastAPI 服务。

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

当前已验证容器：

- `iot-warehouse-device-gateway-1`
- `iot-warehouse-inventory-service-1`
- `iot-warehouse-alert-service-1`
- `iot-warehouse-mosquitto-1`
- `iot-warehouse-redis-1`
- `iot-warehouse-timescaledb-1`

停止 Docker 环境：

```powershell
docker compose -p iot-warehouse down
```

## 7. 清理运行数据

```powershell
Remove-Item -Recurse -Force runtime -ErrorAction SilentlyContinue
```
