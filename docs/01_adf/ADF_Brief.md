# ADF Brief - IoT 智能仓储监控与告警平台

## 1. 项目概述

### 1.1 业务背景

某物流公司希望为仓储网络建设一套 IoT 驱动的智能仓储平台，统一接入仓库中的温湿度传感器、重量传感器、RFID 扫码设备和 AGV 状态设备。系统需要持续采集设备数据，维护设备与库存状态，并在温度、湿度、重量或设备状态异常时快速生成告警。

方案采用边云协同架构：边缘侧负责设备接入、基础校验、短期缓存和恢复补传；云端负责设备影子、库存状态、告警记录、长期存储和 API 查询。当前可运行原型不接入真实硬件，使用模拟设备数据跑通主要链路。

### 1.2 核心用户角色

| 用户角色 | 说明 | 主要关注点 |
| --- | --- | --- |
| 仓库管理员 | 负责查看仓库设备状态、库存状态和异常告警 | 告警及时、库存状态可信、操作简单 |
| 运维人员 | 负责设备接入、服务部署、故障排查和容量规划 | 可观测性、可靠性、可恢复性 |
| 物流运营人员 | 关注库存变化、补货事件和仓储运行效率 | 库存数据准确、补货事件可追踪 |
| IoT 设备 | 温湿度传感器、重量传感器、RFID 设备和 AGV 状态设备 | 低开销上报、网络异常时不丢关键数据 |
| 外部 WMS/ERP 系统 | 未来可对接库存和补货事件 | 接口清晰、数据一致、权限可控 |

### 1.3 系统边界声明

#### 范围内

- 模拟 IoT 设备上报温湿度、重量、RFID 和 AGV 状态数据。
- 使用 MQTT Broker 接收设备消息。
- 使用边缘网关完成消息校验、缓存和转发。
- 维护设备影子，保存设备最后一次已知状态。
- 维护简化库存状态，并在库存低于阈值时触发补货事件。
- 在传感器数据超过阈值时生成异常告警。
- 提供 REST API 查询设备状态、库存状态和告警记录。
- 提供 Docker Compose 本地演示环境。

#### 范围外

- 不接入真实硬件设备。
- 不实现真实 AGV 路径规划。
- 不实现完整 WMS、ERP 或财务系统。
- 不开发复杂前端管理后台。
- 不调用真实短信、电话、邮件或企业微信告警通道。
- 不实现完整 OTA 固件升级流程，OTA 只作为架构演进能力进行设计。

## 2. 功能性需求摘要

### 2.1 用户故事

#### FR-001 设备数据上报

As a IoT device, I want to publish telemetry data to the platform, so that warehouse status can be monitored continuously.

#### FR-002 设备消息接入

As an edge gateway, I want to receive and validate device messages, so that invalid or malformed data does not enter cloud services.

#### FR-003 设备影子维护

As a warehouse administrator, I want to view the latest known state of each device, so that I can understand device status even when a device is temporarily offline.

#### FR-004 库存状态更新

As a logistics operator, I want RFID and weight data to update simplified inventory state, so that replenishment decisions have a data basis.

#### FR-005 异常告警生成

As a warehouse administrator, I want abnormal temperature, humidity, weight, and device state changes to generate alerts, so that risks can be handled quickly.

#### FR-006 自动补货事件

As a logistics operator, I want low stock levels to trigger replenishment events, so that inventory shortages can be detected early.

#### FR-007 告警查询

As an operations engineer, I want to query alert records through REST APIs, so that demo, troubleshooting, and evidence collection are easy.

#### FR-008 边缘缓存与补传

As an operations engineer, I want the edge gateway to cache messages when cloud services are unavailable, so that short network failures do not cause critical data loss.

### 2.2 架构重要需求（ASR）

| ASR 编号 | 描述 | 关联质量属性 |
| --- | --- | --- |
| ASR-001 | 系统需要支持大量设备通过轻量协议持续上报数据 | 可伸缩性、性能 |
| ASR-002 | 异常数据从设备上报到告警生成不超过 5 秒 | 实时性 |
| ASR-003 | 云端短暂不可用时，边缘侧需要缓存并恢复补传关键数据 | 可靠性 |
| ASR-004 | 系统需要维护设备影子，支持设备离线后的状态查询 | 可靠性、可维护性 |
| ASR-005 | 传感器历史数据需要按时间查询和聚合分析 | 可观测性、可维护性 |
| ASR-006 | 告警处理链路需要与设备接入链路解耦 | 可伸缩性、可修改性 |
| ASR-007 | 设备接入需要具备身份认证和防伪造策略 | 安全性 |
| ASR-008 | 本地原型需要通过 Docker Compose 一键启动 | 可部署性、可演示性 |

## 3. 质量属性优先级排序

采用 MoSCoW 方法排序：

| 质量属性 | 优先级 | 理由 |
| --- | --- | --- |
| 实时性 | Must Have | 题目明确要求异常告警从感知到推送不超过 5 秒，且适合 Demo 验证 |
| 可靠性 | Must Have | IoT 网络不稳定，设备离线缓存和恢复补传是题目核心挑战 |
| 可伸缩性 | Must Have | 题目要求 10,000+ 设备接入和 50,000 msg/s 消息吞吐 |
| 安全性 | Should Have | 题目要求设备双向认证和防伪造接入，当前原型只做简化处理，正式方案需要完整设计 |
| 可维护性 | Should Have | OTA、服务边界和事件 Schema 影响后续演进能力 |
| 可观测性 | Should Have | 告警、压测和故障注入需要可观测数据支撑 |
| 用户体验 | Nice to Have | 本作业不开发复杂前端，通过 API 文档和 Demo 步骤满足展示需要 |

## 4. 约束条件

### 4.1 技术约束

- 原型使用 Python + FastAPI 实现核心服务。
- IoT 接入优先使用 MQTT，Broker 使用 Eclipse Mosquitto。
- 时序数据存储优先使用 TimescaleDB。
- 本地环境使用 Docker Compose 启动。
- 架构图使用 Mermaid 或 PlantUML 代码形式，避免截图。

### 4.2 业务约束

- 项目服务于课程期末大作业，重点是架构推理、文档追溯和可运行验证。
- 原型只实现关键行为，不按完整业务产品开发。
- 压测结论需要说明本地测试环境边界，不能夸大到真实生产规模。

### 4.3 组织约束

- 团队规模按课程要求为 3 到 4 人。
- 技术栈选择以开发效率、可运行性和可解释性为优先。
- 每位成员需要能解释自己负责的文档、ADR、视图或代码证据。

## 5. 关键干系人及其关注点

| 干系人角色 | 主要关注点 | 对应质量属性 |
| --- | --- | --- |
| 课程教师 | 架构决策是否可追溯、可验证、可演进 | 可维护性、可验证性 |
| 仓库管理员 | 告警是否及时，设备状态是否可信 | 实时性、可靠性 |
| 运维人员 | 故障是否可定位，服务是否容易恢复 | 可观测性、可靠性 |
| 物流运营人员 | 库存状态和补货事件是否可追踪 | 一致性、可审计性 |
| 安全负责人 | 是否能防止伪造设备接入 | 安全性 |
| 开发团队 | 服务边界是否清晰，原型是否可按时完成 | 可维护性、可部署性 |
