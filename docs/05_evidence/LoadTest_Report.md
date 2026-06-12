# Load Test Report - IoT 智能仓储监控与告警平台

本文件记录本地负载测试的做法、结果和边界。当前机器已完成 Docker Desktop + WSL2 初始化，并能通过 Docker Compose 启动完整原型环境。本地测试只反映当前笔记本和当前原型实现的表现，不声称满足题目中的 50,000 msg/s。

## 1. 测试工具与脚本路径

- 脚本：`scripts/load-test/local_load.py`
- 运行方式：通过 HTTP POST 向 `device-gateway /ingest` 连续发送模拟遥测数据。
- 服务：`device-gateway`、`inventory-service`、`alert-service`

## 2. 测试场景

| 场景 | 描述 | 目标 |
| --- | --- | --- |
| 正常负载 | 发送少量正常和异常设备消息 | 验证脚本和服务链路可运行 |
| 串行负载 | 使用 `local_load.py` 一条一条发送 HTTP 请求 | 记录最基础吞吐和错误率 |
| 临时并发负载 | 使用临时并发脚本向 `/ingest` 发起多线程请求 | 观察 gateway 和 inventory 的写入边界 |
| 持续压测 | 当前未执行 | 留待后续生产化验证 |

## 3. 本地执行结果

### 3.1 早期 `.venv` 串行测试

执行命令：

```powershell
.\.venv\Scripts\python.exe scripts/load-test/local_load.py --count 10 --abnormal-every 5
```

结果：

```json
{
  "count": 10,
  "errors": 0,
  "elapsedSeconds": 41.291,
  "messagesPerSecond": 0.24
}
```

### 3.2 Docker Compose 串行测试

```powershell
docker compose -p iot-warehouse up -d
.\.venv\Scripts\python.exe scripts/load-test/local_load.py --count 10 --abnormal-every 5
```

结果：

```json
{
  "count": 10,
  "errors": 0,
  "elapsedSeconds": 0.351,
  "messagesPerSecond": 28.47
}
```

后续扩大消息数量后，串行 HTTP 测试结果如下。当前脚本只统计总耗时和错误数，没有逐请求记录延迟，因此 P50/P95/P99 标记为未采集。

| 命令 | 消息数 | 错误数 | 耗时 | TPS/msg/s | P50 延迟 | P95 延迟 | P99 延迟 |
| --- | ---: | ---: | ---: | ---: | --- | --- | --- |
| `local_load.py --count 100 --abnormal-every 10` | 100 | 0 | 3.202s | 31.23 | 未采集 | 未采集 | 未采集 |
| `local_load.py --count 1000 --abnormal-every 50` | 1000 | 0 | 26.127s | 38.27 | 未采集 | 未采集 | 未采集 |

### 3.3 临时并发 HTTP 测试

为了观察并发请求下的瓶颈，又使用临时 Python 并发脚本发起多线程 HTTP 请求。该脚本没有纳入正式代码，只作为本次测试记录。

| 测试 | 消息数 | 并发线程 | HTTP 请求错误数 | 耗时 | TPS/msg/s | P50 延迟 | P95 延迟 | P99 延迟 |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |
| 并发 HTTP | 1000 | 50 | 0 | 4.430s | 225.74 | 未采集 | 未采集 | 未采集 |
| 并发 HTTP | 5000 | 100 | 0 | 21.012s | 237.96 | 未采集 | 未采集 | 未采集 |

并发测试后，`device-gateway /health` 显示 `cachedMessages: 7010`。继续检查发现 `inventory-service` 对大量 `/telemetry` 请求返回 `400 Bad Request`，错误详情为：

```text
Extra data: line 17 column 2
```

该错误来自本地 JSON 状态文件被并发写入打乱。清理 `runtime/` 后重启 Compose，服务恢复为：

```json
{"service":"device-gateway","status":"ok","cachedMessages":0}
{"service":"inventory-service","status":"ok"}
{"service":"alert-service","status":"ok"}
```

恢复后重新执行主流程验证：`send_sample.py --abnormal --low-stock` 成功，单元测试 `pytest tests -q` 为 `4 passed`。

## 4. 与质量属性目标对比

| 指标 | 题目目标 | 当前原型结果 | 结论 |
| --- | --- | --- | --- |
| 设备接入规模 | 10,000+ 设备 | 未在当前机器验证 | Partial |
| 消息吞吐 | 50,000 msg/s | 串行 HTTP 约 31-38 msg/s；临时并发 HTTP 表面约 238 msg/s，但后端文件存储出现并发写入错误 | Partial |
| 错误率 | 应尽量接近 0 | HTTP 请求层面可做到 0 错误；业务落库层面暴露 JSON 文件并发写入问题 | Partial |
| 告警链路 | 异常告警 ≤ 5s | PoC-001 约 4.16s | Pass for PoC |

## 5. 瓶颈定位

当前测试结果不能代表架构上限，原因如下：

- 主要脚本使用 HTTP 请求，不是真实 MQTT 设备并发上报。
- 当前应用层仍使用 JSON/JSONL 文件保存运行数据，不是数据库并发写入。
- 临时并发测试证明请求可以打到 gateway，但 inventory 文件写入会出错。
- FastAPI 服务以开发方式启动，没有多 worker 或异步批量写入。
- TimescaleDB 容器已在 Compose 中提供，但应用代码尚未迁移到数据库存储。

## 6. 优化建议

- 将 `local_load.py` 改造为正式并发压测脚本，或使用 k6/Locust。
- 在正式压测脚本中记录逐请求耗时，补齐 P50/P95/P99 延迟。
- 使用真实 MQTT 并发发布方式模拟设备接入，而不是只走 HTTP。
- 将 inventory 和 alert 的存储从 JSON/JSONL 迁移到 TimescaleDB/PostgreSQL。
- gateway 到 inventory 的转发改为批量或异步队列。
- 数据库写入使用批量插入，并增加时间字段索引。
- 报告中只把本地结果作为原型验证，不夸大为生产吞吐。

## 7. 结论

当前负载测试说明两件事：第一，Docker Compose 环境和主链路可以运行；第二，当前 JSON/JSONL 文件存储不适合并发写入。QAS-002 继续标记为 **Partial**：架构设计已经考虑高吞吐扩展，但当前原型只完成本地验证，并暴露了需要在 Phase 5 偿还的存储和压测债务。
