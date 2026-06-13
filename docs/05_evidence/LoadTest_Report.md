# Load Test Report - IoT 智能仓储监控与告警平台

本文件记录本地负载测试的做法、结果和边界。测试目标是验证当前架构在本地 Docker Compose 环境下的设备接入、数据库落库和告警链路表现，不把本地结果等同于生产容量。

## 1. 测试工具与脚本路径

- 脚本：`scripts/load-test/local_load.py`
- 运行方式：通过 HTTP POST 向 `device-gateway /ingest` 连续发送模拟遥测数据。
- 服务：`device-gateway`、`inventory-service`、`alert-service`
- 存储：TimescaleDB/PostgreSQL
- 统计指标：总消息数、并发数、错误数、耗时、msg/s、P50/P95/P99 延迟

## 2. 测试场景

| 场景 | 描述 | 目标 |
| --- | --- | --- |
| 主链路负载 | 发送正常、异常温度和低库存消息 | 验证入口、规则判断、事件和告警链路 |
| 数据库写入负载 | 通过 TimescaleDB/PostgreSQL 写入消息、设备影子、库存、事件和告警 | 验证并发落库稳定性 |
| 多设备接入负载 | 使用 `--unique-devices` 生成不同 `deviceId` | 验证 10,000+ 设备状态落库 |
| 本地边界测试 | 在 Docker Desktop 单机环境运行 | 记录本机可达到的吞吐和延迟 |

## 3. 本地执行结果

### 3.1 小规模链路检查

执行命令：

```powershell
docker compose -p iot-warehouse up -d
.\.venv\Scripts\python.exe scripts\load-test\local_load.py --count 10 --concurrency 2 --unique-devices
```

结果：

```json
{
  "count": 10,
  "concurrency": 2,
  "uniqueDevices": true,
  "errors": 0,
  "elapsedSeconds": 0.121,
  "messagesPerSecond": 82.56,
  "p50Ms": 12.63,
  "p95Ms": 65.56,
  "p99Ms": 65.56
}
```

### 3.2 数据库并发写入测试

执行命令：

```powershell
.\.venv\Scripts\python.exe scripts\load-test\local_load.py --count 5000 --abnormal-every 10 --concurrency 100
```

结果：

```json
{
  "count": 5000,
  "concurrency": 100,
  "uniqueDevices": false,
  "errors": 0,
  "elapsedSeconds": 15.637,
  "messagesPerSecond": 319.75,
  "p50Ms": 180.82,
  "p95Ms": 731.0,
  "p99Ms": 1023.5
}
```

数据库记录数：

| 表 | 记录数 |
| --- | ---: |
| `iot_messages` | 5000 |
| `iot_events` | 834 |
| `iot_alerts` | 500 |
| `device_shadows` | 1 |
| `inventory_items` | 1 |

### 3.3 10,000 设备接入测试

执行命令：

```powershell
.\.venv\Scripts\python.exe scripts\load-test\local_load.py --count 10000 --abnormal-every 20 --concurrency 200 --unique-devices
```

结果：

```json
{
  "count": 10000,
  "concurrency": 200,
  "uniqueDevices": true,
  "errors": 0,
  "elapsedSeconds": 19.018,
  "messagesPerSecond": 525.81,
  "p50Ms": 366.19,
  "p95Ms": 560.18,
  "p99Ms": 652.06
}
```

数据库记录数：

| 表 | 记录数 |
| --- | ---: |
| `iot_messages` | 10000 |
| `iot_events` | 1167 |
| `iot_alerts` | 500 |
| `device_shadows` | 10000 |
| `inventory_items` | 100 |
| orphan alerts | 0 |

## 4. 与质量属性目标对比

| 指标 | 目标 | 本地验证结果 | 结论 |
| --- | --- | --- | --- |
| 设备接入规模 | 10,000+ 设备 | 10,000 个不同 `deviceId` 成功写入设备影子表 | Pass for local validation |
| 消息吞吐 | 50,000 msg/s | 本地 Docker Compose 最高约 525.81 msg/s | Partial |
| 错误率 | 应尽量接近 0 | 10,000 消息、200 并发下请求错误数为 0，数据库记录数一致 | Pass for local validation |
| 告警链路 | 异常告警 ≤ 5s | PoC-001 已验证，压测中告警记录可持续生成 | Pass for PoC |
| 数据落库 | 遥测、状态、事件和告警可持久化 | TimescaleDB/PostgreSQL 表记录完整 | Pass for local validation |

## 5. 瓶颈定位

当前结果不能直接代表生产吞吐，主要原因如下：

- 压测入口使用 HTTP 请求模拟设备上报，不是真实 MQTT 设备并发发布。
- `device-gateway` 到 `inventory-service` 仍是同步 HTTP 转发，每条消息至少经过两次 HTTP 处理。
- 每条消息需要写入消息表、设备影子表、库存表和事件表，异常消息还会触发告警表写入。
- 当前写入是一条消息一个事务，没有使用批量写入。
- Docker Desktop + WSL2 是单机验证环境，不等同于生产集群。
- TimescaleDB 当前为单节点部署，没有启用分区、压缩、保留策略和读写分离。

## 6. 后续优化建议

- 使用 MQTT benchmark 或 Locust/k6 模拟更接近真实设备侧的接入压力。
- 将 gateway 到 inventory 的同步 HTTP 转发改为消息队列或批量写入通道。
- 对遥测写入使用批量 insert，减少每条消息的事务开销。
- 将告警消费改成独立可水平扩展 worker，并增加积压长度监控。
- 对 TimescaleDB 引入 hypertable、索引、压缩、保留策略和备份恢复演练。
- 在生产候选阶段使用多实例服务、生产级 MQTT Broker 和独立消息中间件验证更高吞吐。
