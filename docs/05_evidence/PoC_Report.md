# PoC Report - IoT 智能仓储监控与告警平台

本文档记录用于验证关键架构假设的概念验证。PoC 目标不是证明生产级容量，而是证明 ADR 中的关键行为在最小原型中可运行、可观察、可追溯。

## PoC-001：异常温度事件 5 秒内生成告警

### 验证的架构假设

- ADR-005：事件驱动告警流水线可以支撑 QAS-001 的 5 秒告警目标。
- ADR-004：`inventory-service` 能更新设备影子并发布异常事件。

### 实验设计

- 环境：Windows 本地 `.venv`，三个 FastAPI 服务分别运行在 8001、8002、8003。
- 方法：启动 `device-gateway`、`inventory-service`、`alert-service`，使用 `scripts/data-gen/send_sample.py --abnormal --low-stock` 发送异常温度和低库存样本。
- 验证标准：生成 `HIGH_TEMPERATURE` 告警，且告警创建时间与样本时间差不超过 5 秒。

### 实验过程

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --app-dir apps/inventory-service --port 8002
.\.venv\Scripts\python.exe -m uvicorn main:app --app-dir apps/alert-service --port 8003
$env:INVENTORY_URL='http://localhost:8002'
.\.venv\Scripts\python.exe -m uvicorn main:app --app-dir apps/device-gateway --port 8001
.\.venv\Scripts\python.exe scripts/data-gen/send_sample.py --abnormal --low-stock
```

### 结果数据

本地执行结果：

| 指标 | 结果 |
| --- | --- |
| 输入温度 | 39.8 |
| 告警阈值 | 38.0 |
| 生成事件数 | 2 |
| 生成告警数 | 1 |
| 告警类型 | HIGH_TEMPERATURE |
| 告警创建时间差 | 约 4.16 秒 |
| 结论 | Pass |

同时生成 `REPLENISHMENT_REQUIRED` 事件，证明库存低于阈值时可以触发补货事件。

### 结论

- 假设是否成立：成立。
- 对架构决策的影响：支持 ADR-005，事件驱动告警链路可以作为 Demo 主线。
- 后续行动：正式答辩前应重新运行脚本并保存终端截图或日志摘要。

## PoC-002：云端不可用后的边缘缓存与恢复补传

### 验证的架构假设

- ADR-006：`device-gateway` 可以在云端不可用时缓存消息，并在恢复后补传。
- ADR-002：边云协同架构能提升现场可靠性。

### 实验设计

- 环境：本地 `.venv`，使用 `scripts/fault-injection/cloud_outage_demo.py` 模拟云端不可用和恢复。
- 方法：将两条设备消息写入 Edge Cache，再调用 `process_telemetry` 模拟云端恢复后的补传处理。
- 验证标准：缓存消息被接受处理，生成事件，补传后缓存清空。

### 实验过程

```powershell
Remove-Item -Recurse -Force runtime -ErrorAction SilentlyContinue
.\.venv\Scripts\python.exe scripts/fault-injection/cloud_outage_demo.py
```

### 结果数据

```json
{
  "cachedBeforeReplay": 2,
  "cacheRowsVisible": 0,
  "replayAccepted": 2,
  "eventsCreated": 2
}
```

### 结论

- 假设是否成立：在最小原型中成立。
- 对架构决策的影响：支持 ADR-006，但生产环境仍需补充缓存容量、补传限速和幂等键监控。
- 后续行动：在 `FaultInjection.md` 中继续记录 gateway 级别的 inventory 不可用场景。

## PoC-003：设备影子拒绝旧消息覆盖

### 验证的架构假设

- ADR-004：设备影子需要使用时间戳或版本号防止旧消息覆盖新状态。

### 实验设计

- 环境：pytest 单元测试。
- 方法：先写入较新的设备状态，再尝试用 5 分钟前的旧状态更新同一设备。
- 验证标准：旧状态不覆盖新状态。

### 实验过程

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_iot_core.py::test_stale_shadow_update_is_rejected -q
```

测试用例先构造同一设备的较新遥测消息并更新设备影子，再构造时间更早的遥测消息进行更新。预期结果是旧消息被识别为 `stale_message`，设备影子仍保留较新的 `lastSeenAt` 和 `reported` 状态。

### 结果数据

```text
tests/test_iot_core.py::test_stale_shadow_update_is_rejected passed
```

### 结论

- 假设是否成立：成立。
- 对架构决策的影响：支持 ADR-004，但生产环境仍需引入状态版本号和 desired/reported 确认机制。
- 后续行动：在 v1.1 演进中补充设备影子版本号、期望状态确认和乱序消息处理策略。
