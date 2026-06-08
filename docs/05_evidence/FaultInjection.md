# Fault Injection Report - IoT 智能仓储监控与告警平台

本文档记录当前原型中的故障注入场景。目标是验证 ADR-002 和 ADR-006 中关于边云协同、边缘缓存和恢复补传的关键假设。

## 场景 FI-001：inventory-service 不可用时 gateway 缓存消息

### 故障注入方式

只启动 `device-gateway`，并将 `INVENTORY_URL` 指向不可用地址：

```powershell
$env:INVENTORY_URL='http://localhost:8999'
.\.venv\Scripts\python.exe -m uvicorn main:app --app-dir apps/device-gateway --port 8001
.\.venv\Scripts\python.exe scripts/data-gen/send_sample.py --abnormal
```

### 系统表现

本地验证结果：

```json
{
  "CacheCount": 1,
  "GatewayHealth": "ok"
}
```

### 恢复时间

该场景只验证缓存，不验证恢复时间。

### 是否满足可用性目标

Partial。gateway 在云端不可用时仍保持健康并缓存消息，但需要 FI-002 验证恢复补传。

## 场景 FI-002：云端恢复后缓存消息补传

### 故障注入方式

运行本地故障注入脚本：

```powershell
.\.venv\Scripts\python.exe scripts/fault-injection/cloud_outage_demo.py
```

### 系统表现

```json
{
  "cachedBeforeReplay": 2,
  "cacheRowsVisible": 0,
  "replayAccepted": 2,
  "eventsCreated": 2
}
```

### 恢复时间

脚本级恢复在单次运行内完成，未模拟真实网络恢复耗时。

### 是否满足可用性目标

Pass for prototype。补传后缓存清空，消息被云端处理并生成事件。

## 场景 FI-003：alert-service 延迟启动后消费已有异常事件

### 故障注入方式

先启动 `inventory-service` 并写入异常温度事件，不启动 `alert-service`。随后启动 `alert-service`，观察其后台任务是否消费已有事件。

### 系统表现

本地验证结果：

```json
{
  "AlertCount": 1,
  "FirstType": "HIGH_TEMPERATURE"
}
```

### 恢复时间

`alert-service` 启动后约 2 秒内可查询到告警。

### 是否满足可用性目标

Pass for prototype。事件驱动设计允许告警服务恢复后继续处理积压事件。

## 结论

| 场景 | 结论 | 关联QAS | 关联ADR |
| --- | --- | --- | --- |
| FI-001 | Partial | QAS-003 | ADR-002, ADR-006 |
| FI-002 | Pass | QAS-003 | ADR-006 |
| FI-003 | Pass | QAS-001 | ADR-005 |

当前故障注入证明最小原型具备边缘缓存、恢复补传和事件恢复消费能力。生产环境仍需补充真实服务宕机、数据库切换、网络分区和 Broker 故障演练。

