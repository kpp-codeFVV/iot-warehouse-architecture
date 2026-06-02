# ADR Index - IoT 智能仓储监控与告警平台

| ADR编号 | 标题 | 状态 | 关联QAS | 关联容器/组件 | 最后更新 |
| --- | --- | --- | --- | --- | --- |
| ADR-001 | 选择 MQTT 作为 IoT 设备接入协议 | Accepted | QAS-002, QAS-006 | MQTT Broker, device-gateway | 2026-06-02 |
| ADR-002 | 采用边云协同架构划分 Edge 与 Cloud 职责 | Accepted | QAS-002, QAS-003, QAS-008 | device-gateway, inventory-service | 2026-06-02 |
| ADR-003 | 选择 TimescaleDB 存储传感器时序数据 | Accepted | QAS-005 | TimescaleDB, Repository | 2026-06-02 |
| ADR-004 | 采用设备影子模式管理设备状态 | Accepted | QAS-004, QAS-008 | Device Shadow Manager | 2026-06-02 |
| ADR-005 | 采用事件驱动告警流水线 | Accepted | QAS-001, QAS-007, QAS-009 | Event Channel, alert-service | 2026-06-02 |
| ADR-006 | 采用边缘缓存与恢复补传机制 | Accepted | QAS-003 | Edge Cache, Replay Worker | 2026-06-02 |

