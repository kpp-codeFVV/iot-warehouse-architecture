# View Consistency Check - IoT 智能仓储监控与告警平台

本文档检查 Phase 2 架构视图之间的一致性，并确认视图、ADR 和质量属性场景之间存在可追溯关系。

## 1. 服务与容器命名一致性

| 检查项 | Context View | Container View | Component View | Dynamic Views | Deployment View | 是否一致 | 说明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 系统名称 | IoT 智能仓储监控与告警平台 | IoT 智能仓储监控与告警平台 | IoT 智能仓储监控与告警平台 | IoT 智能仓储监控与告警平台 | IoT 智能仓储监控与告警平台 | 是 | 系统边界一致 |
| 设备接入 | IoT 设备群 | device-simulator, MQTT Broker | MQTT Subscriber | 温湿度传感器, RFID/重量设备 | IoT 设备群 | 是 | Level 1 到 Level 3 逐步细化 |
| 边缘网关 | 平台内部能力 | device-gateway | device-gateway 组件 | device-gateway | Edge Node 中的 device-gateway | 是 | 负责校验、缓存和补传 |
| 设备影子与库存 | 平台内部能力 | inventory-service | Device Shadow Manager, Inventory Updater | inventory-service | inventory-service replica | 是 | 设备状态和库存状态职责一致 |
| 告警服务 | 平台内部能力 | alert-service | alert-service 说明 | alert-service | alert-service replica | 是 | 异常事件消费和告警记录职责一致 |
| 时序数据存储 | 平台内部能力 | TimescaleDB | Repository 依赖 TimescaleDB | TimescaleDB | TimescaleDB Primary + Replica | 是 | 统一作为遥测和业务数据存储 |
| 事件通道 | 平台内部能力 | Event Channel | Event Publisher | Event Channel | TimescaleDB Event Table / Managed MQ | 是 | 本地验证与生产扩展命名存在映射关系 |

## 2. ADR 到视图追溯

| ADR | 决策主题 | Context View | Container View | Component View | Dynamic Views | Deployment View |
| --- | --- | --- | --- | --- | --- | --- |
| ADR-001 | MQTT 接入协议 | IoT 设备通过 MQTT 上报 | MQTT Broker 容器 | MQTT Subscriber | 设备 publish telemetry | 设备网络访问边缘 Broker |
| ADR-002 | 边云协同 | 系统边界包含边缘与云端职责 | EdgeLayer / CloudLayer | gateway 与 inventory 分层 | 云端不可用时边缘缓存 | Warehouse / Cloud 分区 |
| ADR-003 | TimescaleDB | 平台长期存储能力 | TimescaleDB 容器 | Repository 依赖 | 写入遥测与告警 | TimescaleDB Primary + Replica |
| ADR-004 | 设备影子 | 管理员查询设备状态 | inventory-service | Device Shadow Manager | 更新 device shadow | 云端服务持久化设备状态 |
| ADR-005 | 事件驱动告警 | 平台生成告警 | Event Channel + alert-service | Event Publisher | HIGH_TEMPERATURE 事件流 | 事件通道可扩展消费 |
| ADR-006 | 边缘缓存补传 | 平台支持恢复补传 | Edge Cache | Edge Cache Writer, Replay Worker | DV-002 补传流程 | Edge Cache 降级模式 |

## 3. QAS 到视图和 ADR 追溯

| QAS | 质量场景 | 相关 ADR | 相关视图 | 说明 |
| --- | --- | --- | --- | --- |
| QAS-001 | 异常温度 5 秒内告警 | ADR-005 | Dynamic DV-001, Container View | 事件驱动告警流水线支撑实时告警 |
| QAS-002 | 设备消息高吞吐接入 | ADR-001, ADR-002 | Context View, Container View, Deployment View | MQTT 和边云分层支撑大量设备接入 |
| QAS-003 | 云端短暂不可用后的边缘补传 | ADR-002, ADR-006 | Component View, Dynamic DV-002, Deployment View | Edge Cache 和 Replay Worker 支撑恢复补传 |
| QAS-004 | 设备离线后仍可查询最后状态 | ADR-004 | Component View, Dynamic DV-001 | Device Shadow Manager 保存最后状态 |
| QAS-005 | 传感器历史数据按时间查询 | ADR-003 | Container View, Deployment View | TimescaleDB 存储遥测历史 |
| QAS-006 | 伪造设备接入被拒绝 | ADR-001 | Context View, Component View | MQTT 接入需要设备校验和 Topic 权限 |
| QAS-007 | 告警规则变更不影响设备接入 | ADR-005 | Component View, Dynamic DV-001 | 告警规则与接入链路解耦 |
| QAS-008 | 批量设备升级不影响在线采集 | ADR-002, ADR-004 | Deployment View, Component View | 设备影子支持期望状态，边云协同支持批次化策略 |
| QAS-009 | 库存低于阈值触发补货事件 | ADR-005 | Dynamic DV-003, Component View | Inventory Updater 发布补货事件 |

## 4. 通信一致性检查

| 通信路径 | Container View | Dynamic Views | Deployment View | 是否一致 | 说明 |
| --- | --- | --- | --- | --- | --- |
| 设备到 Broker | MQTT / JSON / 异步 | Device publish telemetry | 设备网络到 Edge Node | 是 | 设备只访问边缘 Broker |
| Broker 到 gateway | MQTT subscribe / JSON / 异步 | Broker deliver message | Edge Node 内部通信 | 是 | 网关订阅设备 Topic |
| gateway 到 inventory | HTTP REST / JSON / 同步 | POST /telemetry | Edge 到 Cloud 经私有网络 | 是 | 同步转发失败时进入边缘缓存 |
| inventory 到 Event Channel | SQL event row / JSONB / 异步 | publish HIGH_TEMPERATURE | 云端服务网络 | 是 | 事件驱动告警和补货 |
| alert 到数据库 | SQL / Rows / 同步 | create alert record | 数据网络 | 是 | 告警记录持久化 |

## 5. 原型阶段接受的限制

- Docker Compose 原型使用单实例服务，生产视图中的多副本和多可用区属于架构目标，不在本地环境中完整实现。
- 原型阶段安全策略采用简化设备凭证校验，生产环境需要补充双向 TLS、证书轮换和 Topic ACL。
- 本地验证环境使用 TimescaleDB/PostgreSQL 事件表承载事件通道，生产环境需要结合吞吐目标评估 Kafka、RabbitMQ 或云消息服务。
- TimescaleDB 原型使用单节点部署，生产环境需要补充备份、保留策略、压缩策略和容量规划。
