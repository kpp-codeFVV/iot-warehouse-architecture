# IoT 智能仓储监控与告警平台团队报告

## 封面信息

| 项目 | 内容 |
| --- | --- |
| 课程 | 软件体系结构 |
| 题目编号 | 题目二：物联网智能仓储管理系统 |
| 项目名称 | IoT 智能仓储监控与告警平台 |
| 团队名称与成员 | 最终版填写真实姓名、学号、分工和贡献率 |
| 仓库地址 | 最终版填写课程平台或 Git 仓库地址 |
| 提交日期 | 以实际提交日期为准 |

报告正文把 `docs/` 目录中的阶段性材料串成一份统一说明，集中呈现项目背景、架构决策、评估结果、验证证据和后续演进。细节表格、脚本路径和完整证据仍保留在各阶段源文档中，避免正文过长。

## 摘要

本项目围绕物流仓储场景设计一个 IoT 驱动的智能仓储监控与告警平台。系统面向温湿度传感器、重量传感器、RFID 扫码设备和 AGV 状态设备，重点处理设备接入、设备状态、库存变化、异常告警、补货事件和边缘补传这几类架构问题。

整体方案采用边云协同：边缘侧负责 MQTT 设备接入、基础校验、短期缓存和恢复补传；云端服务负责设备影子、库存事件、告警记录、长期存储和查询 API。我们实现了 3 个可运行 FastAPI 服务，配合 MQTT Broker、Redis 和 TimescaleDB，通过 Docker Compose 一键启动，并用 PoC、压测、故障注入和追溯矩阵记录关键决策的验证情况。

## 1. 项目背景与目标

物流公司希望对多个仓库中的货架传感器、AGV 机器人和 RFID 设备进行统一接入与管理，实现库存实时可视化、异常预警、自动补货触发和出入库流程自动化。题目要求系统能够应对 10,000+ 设备接入、50,000 msg/s 消息吞吐、设备离线缓存、异常告警 5 秒内触发、设备双向认证和 OTA 批量升级等质量挑战。

### 1.1 系统范围

范围内能力：

- 模拟 IoT 设备上报温湿度、重量、RFID 和 AGV 状态数据。
- 边缘网关接收设备消息，完成基础校验、缓存和转发。
- 云端服务维护设备影子、库存状态和告警记录。
- 异常温度触发 `HIGH_TEMPERATURE` 告警。
- 库存低于阈值触发 `REPLENISHMENT_REQUIRED` 事件。
- 使用 Docker Compose 启动完整本地验证环境。
- 提供 OpenAPI 和 JSON Schema 契约。

范围外能力：

- 不接入真实硬件设备。
- 不实现真实 AGV 路径规划。
- 不对接完整 ERP、WMS 或第三方物流系统。
- 不开发复杂前端管理后台。
- 不实现短信、电话、企业微信等外部通知通道。
- 不实现完整 OTA 固件升级流程，只在架构文档中设计其演进路径。

## 2. 架构驱动因素

Phase 1 的完整材料位于：

- `docs/01_adf/ADF_Brief.md`
- `docs/01_adf/Quality_Scenarios.md`

### 2.1 核心用户角色

| 角色 | 关注点 | 对应质量属性 |
| --- | --- | --- |
| 仓库运维人员 | 快速发现超温、设备离线、缓存积压等异常 | 实时性、可观测性、可靠性 |
| 仓储业务人员 | 及时看到库存变化和补货事件 | 业务及时性、可用性 |
| IoT 平台开发人员 | 能扩展设备类型、事件规则和服务边界 | 可修改性、可维护性 |
| 安全与运维人员 | 防止伪造设备接入，保证服务可部署和可恢复 | 安全性、可运维性 |

### 2.2 关键质量场景

项目定义了 9 个质量属性场景，覆盖实时性、可靠性、可伸缩性、安全性、可观测性、可修改性和可维护性。

| QAS 编号 | 场景 | 重要性 | 关联决策 |
| --- | --- | --- | --- |
| QAS-001 | 异常温度 5 秒内告警 | Must Have | ADR-005 |
| QAS-002 | 设备消息高吞吐接入 | Must Have | ADR-001, ADR-002 |
| QAS-003 | 云端短暂不可用后的边缘补传 | Must Have | ADR-002, ADR-006 |
| QAS-004 | 设备离线后仍可查询最后状态 | Must Have | ADR-004 |
| QAS-005 | 传感器历史数据按时间查询 | Should Have | ADR-003 |
| QAS-006 | 伪造设备接入被拒绝 | Should Have | ADR-001 |
| QAS-007 | 告警规则变更不影响设备接入 | Should Have | ADR-005 |
| QAS-008 | 批量设备升级不影响在线采集 | Should Have | ADR-002, ADR-004 |
| QAS-009 | 库存低于阈值触发补货事件 | Should Have | ADR-005 |

## 3. 架构设计

Phase 2 的架构视图位于：

- `docs/02_views/Context_View.md`
- `docs/02_views/Container_View.md`
- `docs/02_views/Component_View.md`
- `docs/02_views/Dynamic_Views.md`
- `docs/02_views/Deployment_View.md`
- `docs/02_views/View_Consistency_Check.md`

### 3.1 总体方案

系统采用边云协同架构。设备消息先进入仓库现场边缘层，边缘层负责 MQTT 接入、基础校验、短期缓存和恢复补传；云端层负责库存状态、设备影子、告警记录、时序数据存储和统一 API。

核心链路如下：

```text
模拟设备
  -> MQTT Broker
  -> device-gateway
  -> inventory-service
  -> abnormal_event / replenishment_event
  -> alert-service
  -> 查询 API
```

采用这个方案的原因比较直接：如果所有处理都放在云端，仓库网络中断时设备数据容易丢失；如果一开始就做成复杂的大规模微服务平台，首期范围会失控。边云协同能同时解释设备离线缓存、断点续传和低延迟告警。

### 3.2 容器与职责

| 容器 | 技术 | 职责 | 主要接口/通信 |
| --- | --- | --- | --- |
| MQTT Broker | Eclipse Mosquitto | 接收设备发布消息，支撑 Topic 订阅 | MQTT |
| device-gateway | Python + FastAPI | 设备消息接入、校验、缓存、转发、健康检查 | REST, MQTT |
| inventory-service | Python + FastAPI | 设备影子、库存状态、补货事件、异常事件生成 | REST, Event |
| alert-service | Python + FastAPI | 消费异常事件，生成告警记录，提供告警查询 | REST, Event |
| Redis | Redis | 原型中的缓存与轻量事件支撑 | TCP |
| TimescaleDB | PostgreSQL/TimescaleDB | 时序数据和长期存储策略载体 | SQL |

### 3.3 关键动态场景

项目动态视图覆盖 3 个核心流程：

| 场景 | 说明 | 关联质量属性 |
| --- | --- | --- |
| 异常温度告警 | 设备上报高温，系统生成 `HIGH_TEMPERATURE` 告警 | QAS-001 |
| 云端不可用后的边缘补传 | 网关缓存失败转发消息，云端恢复后补传 | QAS-003 |
| 库存低于阈值触发补货 | 重量或库存低于阈值，生成补货事件 | QAS-009 |

### 3.4 部署视角

本地环境使用 Docker Compose。部署视图中另外给出生产环境的云原生拓扑，用来说明边缘节点、云端服务、存储层、网络分区和高可用策略。Compose 只能说明服务边界和通信链路可以跑通，不能直接等同于生产部署。

## 4. 架构决策记录

Phase 2 的 ADR 位于 `docs/03_adrs/`，索引文件为 `docs/03_adrs/ADR_Index.md`。

| ADR | 决策 | 选择结果 | 主要服务的质量场景 |
| --- | --- | --- | --- |
| ADR-001 | IoT 接入协议选型 | 选择 MQTT | QAS-002, QAS-006 |
| ADR-002 | Edge 与 Cloud 职责划分 | 采用边云协同 | QAS-002, QAS-003, QAS-008 |
| ADR-003 | 时序数据存储选型 | 选择 TimescaleDB | QAS-005 |
| ADR-004 | 设备状态管理策略 | 采用设备影子 | QAS-004, QAS-008 |
| ADR-005 | 告警流水线设计 | 采用事件驱动告警 | QAS-001, QAS-007, QAS-009 |
| ADR-006 | 离线缓存与恢复补传 | 采用边缘缓存补传 | QAS-003 |

### 4.1 代表性决策：为什么选择 MQTT

设备接入场景需要低开销、发布订阅、适合弱网络和大量设备连接。MQTT 相比 HTTP 轮询更适合持续设备上报；相比 AMQP 更轻量；相比 CoAP 在通用 Broker、工具链和工程落地上更容易验证。因此 ADR-001 选择 MQTT，并在 Phase 5 中规划从单节点 Mosquitto 演进到高可用 Broker。

### 4.2 代表性决策：为什么采用事件驱动告警

异常告警不应直接耦合在设备接入服务中。ADR-005 将异常识别、事件发布和告警生成拆开，使设备接入链路不因告警逻辑变更而频繁修改。该决策服务 QAS-001、QAS-007 和 QAS-009，也让后续规则版本化、消息中间件替换和告警降噪有清晰演进空间。

## 5. 架构评估

Phase 3 的评估材料位于：

- `docs/04_evaluation/ATAM_Record.md`
- `docs/04_evaluation/Sensitivity_Tradeoff.md`
- `docs/04_evaluation/Risk_List.md`
- `docs/04_evaluation/Tech_Debt.md`

### 5.1 ATAM 评估结论

轻量 ATAM 评估围绕质量属性效用树展开，重点分析实时告警、设备接入扩展、边缘补传、设备影子、时序数据查询和安全接入。评估结果显示，当前设计对“实时告警”和“边缘补传”的主链路支撑较清楚，但在吞吐、安全认证、Broker 高可用、数据库治理和 OTA 上仍有明显债务。

### 5.2 敏感点与权衡点

主要敏感点包括：

- MQTT Broker 的部署方式会直接影响设备接入吞吐和可用性。
- Edge Cache 的容量、清理和补传策略会影响断网恢复后的数据完整性。
- 告警规则的位置和版本管理会影响可修改性和实时性。
- TimescaleDB 的表结构、索引、保留策略会影响历史查询性能。

主要权衡点包括：

- 边云协同提升断网可靠性，但增加边缘节点管理复杂度。
- 事件驱动降低服务耦合，但增加事件契约和最终一致性处理成本。
- 本地 Compose 容易验证主链路，但不能直接代表生产部署能力。
- 设备影子提升离线可查询能力，但需要处理状态版本、乱序和确认。

### 5.3 风险与技术债务

当前识别的高优先级债务集中在单实例部署、单节点 Broker、简化设备认证和 Edge Cache 生产化不足。中期债务包括 TimescaleDB 数据治理、设备影子版本机制、生产级消息通道和告警规则配置。低优先级但必须规划的是 OTA 批量升级执行链路。

这些债务不是后期才发现的问题，而是首期范围控制时接受的简化。Phase 5 已经为主要债务安排了偿还版本和触发条件。

## 6. 架构验证证据

Phase 4 的证据材料位于：

- `docs/05_evidence/PoC_Report.md`
- `docs/05_evidence/LoadTest_Report.md`
- `docs/05_evidence/FaultInjection.md`
- `docs/05_evidence/QA_Traceability.md`

### 6.1 PoC 验证

PoC 重点验证关键架构假设：

| PoC | 验证目标 | 结论 |
| --- | --- | --- |
| PoC-001 | 异常温度和低库存事件能通过原型链路触发 | 原型范围内成立 |
| PoC-002 | 云端不可用时边缘缓存能保留消息并恢复补传 | 原型范围内成立 |
| PoC-003 | 设备离线后仍能查询最后状态 | 原型范围内成立 |

### 6.2 压测与故障注入

本地压测主要用于观察脚本、服务链路和接口在压力下的表现，不代表生产吞吐上限。最新并发 HTTP 测试最高约 237.96 msg/s，同时暴露出 JSON/JSONL 文件存储在并发写入下会损坏状态文件，因此 QAS-002 仍然保持 Partial。故障注入覆盖核心服务不可用、云端恢复补传和告警链路恢复，用来说明架构对可靠性风险的处理方式。

### 6.3 质量属性追溯

`QA_Traceability.md` 汇总了 QAS、ADR、视图和证据之间的对应关系。当前结论包括：

| 结论 | 数量 | 说明 |
| --- | --- | --- |
| Pass | 2 | QAS-001、QAS-004 已通过本地验证或单元测试验证 |
| Pass for prototype | 2 | QAS-003、QAS-009 在最小原型中成立 |
| Partial | 5 | QAS-002、QAS-005、QAS-006、QAS-007、QAS-008 需要生产级环境或演进阶段继续验证 |
| Fail | 0 | 当前没有完全失败的质量场景 |

## 7. 架构演进

Phase 5 的材料位于 `docs/06_evolution/Evolution_Roadmap.md`。

### 7.1 v1.0 现状

v1.0 已能通过 Docker Compose 启动本地环境，并验证设备接入、设备影子、异常告警、库存事件和边缘补传。它的局限也比较明确：单机单实例、认证简化、Broker 未高可用、数据库写入能力有限、OTA 未实现。

### 7.2 演进路线

| 阶段 | 目标 | 关键变更 |
| --- | --- | --- |
| v1.0 -> v1.1 | 小规模试点 | 多仓库 Edge Registry、Edge Cache 水位控制、告警规则版本化、设备影子版本号、基础观测指标 |
| v1.1 -> v2.0 | 生产候选 | 生产级 MQTT Broker、生产消息通道、mTLS、TimescaleDB 数据治理、Kubernetes/云容器部署、OTA 任务服务 |
| v2.0 -> v3.0 | 长期平台化 | 多区域容灾、数字孪生仓库、预测性补货、智能告警降噪、自动化运维 |

### 7.3 演进风险控制

后续演进中重点控制事件契约、设备 ID、消息中间件、数据库 Schema、安全机制、REST API 版本、设备影子模型和 OTA 工作流。涉及接口或数据结构变化时，需要定义影响对象、迁移策略、回滚窗口和关联 ADR/QAS。

## 8. 可运行验证环境

代码和契约目录如下：

| 路径 | 说明 |
| --- | --- |
| `apps/device-gateway/` | 设备接入与边缘缓存服务 |
| `apps/inventory-service/` | 设备影子、库存状态和事件生成服务 |
| `apps/alert-service/` | 告警生成与查询服务 |
| `libs/iot_core.py` | 共享领域模型与核心逻辑 |
| `contracts/openapi/` | REST API OpenAPI 规范 |
| `contracts/events/` | 事件 JSON Schema |
| `scripts/data-gen/` | 示例数据生成脚本 |
| `scripts/load-test/` | 本地压测脚本 |
| `scripts/fault-injection/` | 故障注入脚本 |
| `docker-compose.yml` | 一键启动本地完整环境 |

### 8.1 本地启动

由于项目目录包含中文，Docker Compose 命令需要显式指定项目名：

```powershell
docker compose -p iot-warehouse up -d
docker compose -p iot-warehouse ps
```

服务健康检查：

```powershell
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health
```

主流程验证：

```powershell
.\.venv\Scripts\python.exe scripts\data-gen\send_sample.py --abnormal --low-stock
curl http://localhost:8003/alerts
```

详细步骤见 `docs/07_runbook/Demo_Steps.md` 和 `docs/07_runbook/Local_Setup.md`。

## 9. 团队分工与个人贡献

最终 PDF 中需要写清楚每位成员的姓名、学号、负责模块和贡献率。可以按实际工作拆分为：

| 分工方向 | 主要内容 | 对应交付物 |
| --- | --- | --- |
| 架构驱动因素 | 背景、ASR、质量场景、优先级 | `docs/01_adf/` |
| 架构设计与 ADR | C4 视图、动态视图、部署视图、6 条 ADR | `docs/02_views/`, `docs/03_adrs/` |
| 架构评估 | ATAM、敏感点、权衡点、风险和技术债务 | `docs/04_evaluation/` |
| 原型与验证 | FastAPI 服务、契约、脚本、PoC、压测、故障注入 | `apps/`, `contracts/`, `scripts/`, `docs/05_evidence/` |
| 架构演进与报告 | Phase 5、运行手册、最终报告整合 | `docs/06_evolution/`, `docs/07_runbook/`, `docs/00_final/` |

每位成员还需要单独提交个人贡献声明，说明本人负责的主要模块、参与的架构讨论与决策过程、个人最重要的技术收获。

## 10. 结论

本项目覆盖了智能仓储场景的主要架构工作：先识别架构驱动因素和质量属性场景，再用 C4 视图和 ADR 给出设计，用轻量 ATAM 分析风险、敏感点、权衡点和技术债务，最后通过可运行验证环境、PoC、压测和故障注入记录验证证据。Phase 5 说明了当前方案如何从本地验证版本继续演进。

当前方案的优势是边界清晰、链路可运行、决策和证据能够对应起来。局限也不能回避：本地 Compose、单节点中间件、简化认证、JSON 文件存储和有限压测都不能代表生产能力。后续应按 Phase 5 路线逐步偿还技术债务，而不是一次性扩大到完整工业级 IoT 平台。

## 附录：文档索引

| 阶段 | 文档 | 作用 |
| --- | --- | --- |
| Phase 1 | `docs/01_adf/ADF_Brief.md` | 架构驱动因素简报 |
| Phase 1 | `docs/01_adf/Quality_Scenarios.md` | 质量属性场景清单 |
| Phase 2 | `docs/02_views/Context_View.md` | 系统上下文视图 |
| Phase 2 | `docs/02_views/Container_View.md` | 容器视图 |
| Phase 2 | `docs/02_views/Component_View.md` | 组件视图 |
| Phase 2 | `docs/02_views/Dynamic_Views.md` | 动态视图 |
| Phase 2 | `docs/02_views/Deployment_View.md` | 部署视图 |
| Phase 2 | `docs/02_views/View_Consistency_Check.md` | 视图一致性检查 |
| Phase 2 | `docs/03_adrs/ADR_Index.md` | ADR 索引 |
| Phase 3 | `docs/04_evaluation/ATAM_Record.md` | 轻量 ATAM 评估 |
| Phase 3 | `docs/04_evaluation/Sensitivity_Tradeoff.md` | 敏感点与权衡点 |
| Phase 3 | `docs/04_evaluation/Risk_List.md` | 风险清单 |
| Phase 3 | `docs/04_evaluation/Tech_Debt.md` | 技术债务登记册 |
| Phase 4 | `docs/05_evidence/PoC_Report.md` | PoC 验证报告 |
| Phase 4 | `docs/05_evidence/LoadTest_Report.md` | 负载测试报告 |
| Phase 4 | `docs/05_evidence/FaultInjection.md` | 故障注入报告 |
| Phase 4 | `docs/05_evidence/QA_Traceability.md` | 质量属性追溯矩阵 |
| Phase 5 | `docs/06_evolution/Evolution_Roadmap.md` | 架构演进路线图 |
| Runbook | `docs/07_runbook/Local_Setup.md` | 本地环境启动指南 |
| Runbook | `docs/07_runbook/Demo_Steps.md` | 本地验证步骤手册 |
