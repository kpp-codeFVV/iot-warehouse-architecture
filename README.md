# IoT 智能仓储监控与告警平台

## 项目目标

项目聚焦物流仓储场景，通过模拟温湿度传感器、重量传感器、RFID 扫码设备和 AGV 状态设备，验证 IoT 设备接入、边云协同、设备影子、时序数据存储、事件驱动告警和边缘缓存补传等关键架构决策。

## 项目结构

- `apps/device-gateway/`：边缘设备网关，负责设备消息接入、校验、缓存和转发。
- `apps/inventory-service/`：库存与设备影子服务，负责设备状态、库存状态和补货事件。
- `apps/alert-service/`：告警服务，负责消费异常事件并生成告警记录。
- `libs/iot_core.py`：共享领域模型和核心处理逻辑。
- `contracts/`：OpenAPI 与事件 JSON Schema。
- `scripts/`：样本数据、负载测试和故障注入脚本。
- `docs/`：架构驱动因素、视图、ADR、评估、验证证据、演进和最终报告。

## 本地运行

安装并打开 Docker Desktop，可以直接双击项目根目录下的 `start.bat`，或在 PowerShell / cmd 里运行：

```powershell
.\start.bat
```

脚本会启动 Mosquitto、TimescaleDB、`device-gateway`、`inventory-service` 和 `alert-service`，并自动检查三个 HTTP 服务的 `/health` 接口。

也可以手动使用 Docker Compose。由于项目目录包含中文，Docker Compose 建议显式指定项目名：

```powershell
docker compose -p iot-warehouse up -d
```

健康检查：

```powershell
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health
```

主流程验证：

```powershell
.\demo.bat
```

停止环境：

```powershell
.\stop.bat
```

更完整的步骤见 `docs/07_runbook/Local_Setup.md` 和 `docs/07_runbook/Demo_Steps.md`。
