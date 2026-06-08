# Load Test Report - IoT 智能仓储监控与告警平台

本文档记录当前原型的本地负载测试设计、执行结果和适用边界。由于当前机器未安装 Docker，本报告只记录 `.venv` 本地 HTTP 串行测试结果，不声称满足生产级 50,000 msg/s。

## 1. 测试工具与脚本路径

- 脚本：`scripts/load-test/local_load.py`
- 运行方式：通过 HTTP POST 向 `device-gateway /ingest` 连续发送模拟遥测数据。
- 服务：`device-gateway`、`inventory-service`、`alert-service`

## 2. 测试场景

| 场景 | 描述 | 目标 |
| --- | --- | --- |
| 正常负载 | 发送少量正常和异常设备消息 | 验证脚本和服务链路可运行 |
| 峰值负载 | 后续在 Docker 或更稳定环境中扩大消息数量 | 观察 gateway 和 inventory 写入边界 |
| 持续压测 | 当前未执行 | 留待 Phase 4 后续补充 |

## 3. 本地执行结果

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

## 4. 与质量属性目标对比

| 指标 | 题目目标 | 当前原型结果 | 结论 |
| --- | --- | --- | --- |
| 设备接入规模 | 10,000+ 设备 | 未在当前机器验证 | Partial |
| 消息吞吐 | 50,000 msg/s | 本地串行 HTTP 约 0.24 msg/s | Fail for production target |
| 错误率 | 应尽量接近 0 | 10 条消息错误数 0 | Pass for smoke test |
| 告警链路 | 异常告警 ≤ 5s | PoC-001 约 4.16s | Pass for PoC |

## 5. 瓶颈定位

当前测试结果不能代表架构上限，原因如下：

- 本地测试使用 HTTP 串行请求，不是真实 MQTT 并发上报。
- 本地存储使用 JSON/JSONL 文件，不是 TimescaleDB。
- 当前机器未安装 Docker，无法运行 Mosquitto、Redis、TimescaleDB 的组合环境。
- FastAPI 服务以开发方式启动，没有多 worker 或异步批量写入。

## 6. 优化建议

- 使用 Docker Compose 启动 Mosquitto、Redis 和 TimescaleDB 后重新压测。
- 将 `local_load.py` 改造为并发请求或使用 k6/Locust。
- gateway 到 inventory 的转发改为批量或异步队列。
- TimescaleDB 写入改为批量插入，并增加时间字段索引。
- 在报告中只把本地结果作为 smoke test，不夸大为生产吞吐。

## 7. 结论

当前负载测试证明脚本和服务链路可运行，但不满足生产吞吐目标，也不能替代正式压测。QAS-002 当前验证结论为 **Partial**：架构设计支撑扩展论证，原型仅完成本地可运行和无错误 smoke test。

