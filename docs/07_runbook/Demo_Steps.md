# Local Verification Steps - IoT 智能仓储监控与告警平台

本文档给出本地验证关键架构行为的最小流程。

## 验证目标

展示以下架构行为：

- QAS-001：异常温度 5 秒内生成告警。
- QAS-003：云端不可用时边缘缓存消息。
- QAS-009：库存低于阈值时生成补货事件。
- ADR-005：事件驱动告警流水线。
- ADR-006：边缘缓存与恢复补传。

## 验证 1：异常温度告警

1. 启动三个服务，见 `docs/07_runbook/Local_Setup.md`。
2. 发送异常温度和低库存样本：

```powershell
.\.venv\Scripts\python.exe scripts/data-gen/send_sample.py --abnormal --low-stock
```

3. 等待 1 到 2 秒，查询事件和告警：

```powershell
Invoke-RestMethod http://localhost:8002/events
Invoke-RestMethod http://localhost:8003/alerts
```

4. 预期结果：

- `inventory-service` 生成 `HIGH_TEMPERATURE` 事件。
- `inventory-service` 生成 `REPLENISHMENT_REQUIRED` 事件。
- `alert-service` 自动生成 1 条 `HIGH_TEMPERATURE` 告警。

## 验证 2：云端不可用时边缘缓存

1. 只启动 `device-gateway`，并设置错误的 inventory 地址：

```powershell
$env:INVENTORY_URL='http://localhost:8999'
.\.venv\Scripts\python.exe -m uvicorn main:app --app-dir apps/device-gateway --port 8001
```

2. 发送异常数据：

```powershell
.\.venv\Scripts\python.exe scripts/data-gen/send_sample.py --abnormal
```

3. 查询缓存：

```powershell
Invoke-RestMethod http://localhost:8001/cache
```

4. 预期结果：`count` 为 1，说明 gateway 没有丢弃消息。

## 验证 3：缓存补传脚本

运行：

```powershell
.\.venv\Scripts\python.exe scripts/fault-injection/cloud_outage_demo.py
```

预期输出：

```json
{
  "cachedBeforeReplay": 2,
  "cacheRowsVisible": 0,
  "replayAccepted": 2,
  "eventsCreated": 2
}
```

## 验证 4：本地负载 smoke test

```powershell
.\.venv\Scripts\python.exe scripts/load-test/local_load.py --count 10 --abnormal-every 5
```

该测试只证明脚本和服务链路可运行，不代表生产吞吐。系统报告中需要说明本地测试边界。

## 说明要点

可以这样说明：

```text
当前版本不是完整仓储系统，而是用最小验证环境证明关键架构决策。
异常温度上报后，inventory-service 产生异常事件，alert-service 自动消费事件并生成告警。
当云端不可用时，device-gateway 会把消息写入 Edge Cache，恢复后再补传。
这些行为分别对应 ADR-005 和 ADR-006，也对应 QAS-001 和 QAS-003。
```
