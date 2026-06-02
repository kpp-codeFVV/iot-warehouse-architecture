# IoT 智能仓储监控与告警平台设计文档

日期：2026-06-02

## 1. 项目定位

本项目选择《软件体系结构》课程期末大作业的题目二：物联网智能仓储管理系统。项目名称定为 **IoT 智能仓储监控与告警平台**。

系统面向物流仓储场景，目标是统一接入仓库中的温湿度传感器、重量传感器、RFID 扫码设备和 AGV 状态设备，支持设备数据采集、设备状态管理、库存状态更新、异常告警和自动补货事件触发。

本项目不是完整的 WMS 或 ERP 系统，而是一个用于课程作业的架构原型。原型重点证明关键架构决策可行，包括 IoT 接入协议、边云协同、设备影子、时序数据存储、事件驱动告警和边缘缓存补传。

## 2. 系统范围

### 2.1 范围内

- 模拟 IoT 设备上报温湿度、重量、RFID 和 AGV 状态数据。
- 边缘网关接收设备消息，完成基础校验、缓存和转发。
- 云端服务维护设备影子、库存状态和告警记录。
- 异常温度、异常重量等事件触发告警。
- 库存低于阈值时触发自动补货事件。
- 使用 Docker Compose 一键启动本地演示环境。
- 提供 OpenAPI 文档和事件 JSON Schema，支撑课程交付要求。

### 2.2 范围外

- 不接入真实硬件设备。
- 不实现真实 AGV 路径规划。
- 不对接完整 ERP、WMS 或第三方物流系统。
- 不开发复杂前端管理后台。
- 不实现真实短信、电话、企业微信等外部告警通道。
- 不实现完整 OTA 固件升级流程，只在架构文档中设计 OTA 策略。

## 3. 架构目标

项目采用稳妥高分型策略：文档覆盖课程评分点，原型保持小而完整，重点展示关键架构行为。

质量属性优先级如下：

1. **实时性**：异常告警从设备数据上报到告警生成不超过 5 秒。
2. **可靠性**：设备或网络短暂离线时，边缘侧能够缓存数据，并在恢复后补传。
3. **可伸缩性**：架构能够解释如何支撑 10,000+ 设备接入和 50,000 msg/s 消息吞吐。
4. **安全性**：文档中设计设备身份认证、Topic 权限和传输加密策略，原型做简化验证。
5. **可维护性**：服务边界清晰，支持未来扩展 OTA、通知服务、报表服务和多仓库管理。

## 4. 推荐架构方案

采用 **边云协同架构**。

设备数据先进入仓库现场的边缘接入层，边缘侧负责设备接入、协议适配、基础校验、短期缓存和快速异常识别。云端负责设备影子、库存状态、告警记录、长期存储、API 查询和统一治理。

该方案相较于全云端集中式架构更能体现设备离线缓存、断点续传和低延迟告警；相较于完整微服务事件驱动架构，服务数量更少，原型工作量更可控。

核心链路如下：

```text
模拟设备
  -> MQTT Broker
  -> device-gateway
  -> inventory-service
  -> abnormal_event
  -> alert-service
  -> 告警查询 API
```

## 5. 核心组成

### 5.1 设备模拟层

设备模拟层使用脚本生成测试数据，模拟温湿度传感器、重量传感器、RFID 扫码设备和 AGV 状态设备。

模拟设备定时通过 MQTT 发布消息。消息包含设备 ID、仓库 ID、设备类型、传感器值和时间戳。该层用于 Demo、压测和故障注入，不代表真实硬件接入。

### 5.2 边缘接入层

边缘接入层包含 MQTT Broker 和 `device-gateway` 服务。

MQTT Broker 采用 Eclipse Mosquitto，用于支撑设备发布消息和服务订阅消息。`device-gateway` 使用 Python + FastAPI 实现，负责消费设备消息、校验格式、记录接入状态、缓存暂时无法转发的数据，并在云端恢复后补传。

该层对应课程要求中的 IoT 接入协议选型、Broker 部署策略、Edge 与 Cloud 职责划分，以及设备离线缓存和恢复补传。

### 5.3 云端业务层

云端业务层包含 `inventory-service` 和 `alert-service`。

`inventory-service` 负责维护设备影子、库存状态和补货事件。设备影子保存设备最后一次已知状态、最近上报时间和期望配置状态。库存状态根据重量传感器和 RFID 事件进行简化更新。

`alert-service` 负责消费异常事件并生成告警记录。告警记录包含设备 ID、仓库 ID、告警类型、触发值、阈值、发生时间和处理状态。该服务提供查询 API，方便答辩 Demo 展示。

### 5.4 存储与事件层

时序数据存储推荐使用 TimescaleDB。它基于 PostgreSQL，适合本地 Docker 原型，同时可以解释传感器历史数据按时间查询和聚合分析的需求。

普通业务数据也可以放在 PostgreSQL / TimescaleDB 中，包括设备影子、库存状态和告警记录。事件通道在原型中可使用 Redis Stream 或数据库事件表实现；正式架构文档中说明可演进到 Kafka、RabbitMQ 或云消息服务。

## 6. 关键业务流程

### 6.1 主 Demo：异常告警

1. 使用 `docker-compose up` 启动 MQTT Broker、数据库和 3 个 FastAPI 服务。
2. 启动模拟设备脚本，持续上报正常温湿度和重量数据。
3. 系统显示设备影子和库存状态正常更新。
4. 模拟设备发送异常温度数据，例如 `temperature = 39.8`。
5. `device-gateway` 接收消息并转发。
6. `inventory-service` 更新设备影子，并发布异常事件。
7. `alert-service` 消费异常事件，生成 `HIGH_TEMPERATURE` 告警。
8. 通过 API 查询告警记录，并验证从数据上报到告警生成不超过 5 秒。

### 6.2 PoC：边缘缓存与恢复补传

1. 模拟云端服务暂时不可用。
2. `device-gateway` 将设备消息写入边缘缓存。
3. 云端服务恢复。
4. `device-gateway` 按顺序补传缓存消息。
5. 云端最终收到完整数据，并在 PoC 报告中说明可靠性假设是否成立。

## 7. 架构决策记录计划

课程要求至少 6 条 ADR，并覆盖题目二必须覆盖的架构决策点。本项目计划编写以下 ADR：

| ADR | 决策主题 | 覆盖要求 | 推荐决策 |
| --- | --- | --- | --- |
| ADR-001 | IoT 接入协议选型 | MQTT / CoAP / AMQP | 选择 MQTT |
| ADR-002 | 边云协同职责划分 | Edge 与 Cloud 职责 | 边缘接入与缓存，云端治理与分析 |
| ADR-003 | 时序数据存储选型 | InfluxDB / TimescaleDB / TDengine | 选择 TimescaleDB |
| ADR-004 | 设备影子模式 | Device Shadow | 云端维护设备最后状态和期望状态 |
| ADR-005 | 告警流水线设计 | 事件驱动告警 | 使用异常事件解耦告警服务 |
| ADR-006 | 离线缓存与恢复补传 | 可靠性 | 边缘网关缓存并补传 |

每条 ADR 都需要包含背景、决策驱动因素、可选方案、决策结果、后果和验证方式，并关联质量属性场景和验证证据。

## 8. 文档交付结构

正式课程作业目录遵循 PDF 要求：

```text
docs/
  01_adf/
    ADF_Brief.md
    Quality_Scenarios.md
  02_views/
    Context_View.md
    Container_View.md
    Component_View.md
    Dynamic_Views.md
    Deployment_View.md
    View_Consistency_Check.md
  03_adrs/
    ADR_Index.md
    ADR-001_mqtt_protocol.md
    ADR-002_edge_cloud_architecture.md
    ADR-003_timescaledb.md
    ADR-004_device_shadow.md
    ADR-005_event_driven_alerting.md
    ADR-006_edge_cache_replay.md
  04_evaluation/
    ATAM_Record.md
    Sensitivity_Tradeoff.md
    Risk_List.md
    Tech_Debt.md
  05_evidence/
    PoC_Report.md
    LoadTest_Report.md
    FaultInjection.md
    QA_Traceability.md
  06_evolution/
    Evolution_Roadmap.md
    Breaking_Change_Log.md
  07_runbook/
    Local_Setup.md
    Demo_Steps.md
```

代码与验证目录如下：

```text
apps/
  device-gateway/
  inventory-service/
  alert-service/
contracts/
  openapi/
  events/
scripts/
  data-gen/
  load-test/
  fault-injection/
docker-compose.yml
Makefile
README.md
```

## 9. 验证策略

验证工作围绕质量属性闭环展开。

实时性通过主 Demo 和轻量压测验证，目标是异常消息进入系统后 5 秒内生成告警。可靠性通过边缘缓存和恢复补传 PoC 验证。可伸缩性通过模拟设备批量上报和压测报告论证，说明本地测试规模与题目目标规模之间的适用边界。安全性通过文档设计设备身份、Topic 权限和 TLS 策略，原型保留简化认证。可维护性通过服务拆分、接口规范、事件 Schema 和 ADR 追溯体现。

最终 `QA_Traceability.md` 需要把质量属性场景、ADR、视图和验证证据连起来，形成课程要求的闭环。

## 10. 后续实施顺序

1. 生成 Phase 1 文档：`ADF_Brief.md` 和 `Quality_Scenarios.md`。
2. 生成 Phase 2 文档：C4 视图和 6 条 ADR。
3. 生成 Phase 3 文档：ATAM、敏感点、权衡点、风险和技术债务。
4. 实现最小可运行原型：3 个 FastAPI 服务、MQTT Broker、TimescaleDB、Docker Compose。
5. 编写验证脚本和报告：PoC、压测、故障注入、追溯矩阵。
6. 编写运行手册、Demo 步骤和 README。

该实施顺序优先保证文档结构和架构推理完整，再实现用于验证关键决策的最小原型。
