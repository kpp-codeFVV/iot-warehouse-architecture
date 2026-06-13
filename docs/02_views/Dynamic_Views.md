# Dynamic Views - IoT 智能仓储监控与告警平台

本文档描述关键运行时场景。每个序列图都对应质量属性场景和后续验证证据。

## DV-001：异常温度上报到告警生成

```mermaid
sequenceDiagram
    participant Device as 温湿度传感器
    participant Broker as MQTT Broker
    participant Gateway as device-gateway
    participant Inventory as inventory-service
    participant Events as Event Channel
    participant Alert as alert-service
    participant DB as TimescaleDB

    Device->>Broker: publish telemetry JSON
    Broker-->>Gateway: deliver subscribed message
    Gateway->>Gateway: validate device and schema
    Gateway->>Inventory: POST /telemetry
    Inventory->>DB: write telemetry and device shadow
    Inventory->>Inventory: evaluate temperature threshold
    Inventory->>Events: write HIGH_TEMPERATURE event
    Events-->>Alert: consume event row
    Alert->>DB: create alert record
```

质量属性响应分析：该流程对应 QAS-001。关键响应度量是设备消息时间戳到告警记录创建时间不超过 5 秒。事件通道解耦了告警生成与设备接入，避免设备接入链路直接依赖告警服务。

## DV-002：云端不可用后的边缘缓存与恢复补传

```mermaid
sequenceDiagram
    participant Device as IoT 设备
    participant Broker as MQTT Broker
    participant Gateway as device-gateway
    participant Cache as Edge Cache
    participant Inventory as inventory-service
    participant DB as TimescaleDB

    Device->>Broker: publish telemetry JSON
    Broker-->>Gateway: deliver message
    Gateway->>Inventory: POST /telemetry
    Inventory--xGateway: unavailable or timeout
    Gateway->>Cache: persist pending message
    Note over Gateway,Cache: cloud unavailable, edge keeps accepting device messages
    Inventory-->>Gateway: health check recovered
    Gateway->>Cache: read pending messages in timestamp order
    Gateway->>Inventory: replay telemetry
    Inventory->>DB: persist telemetry and device shadow
    Gateway->>Cache: mark replayed message
```

质量属性响应分析：该流程对应 QAS-003 和 ADR-006。边缘侧在云端不可用时不丢弃关键消息，云端恢复后按顺序补传。补传任务需要幂等键避免重复处理。

## DV-003：库存低于阈值触发补货事件

```mermaid
sequenceDiagram
    participant RFID as RFID/重量设备
    participant Broker as MQTT Broker
    participant Gateway as device-gateway
    participant Inventory as inventory-service
    participant Events as Event Channel
    participant WMS as 外部 WMS/ERP

    RFID->>Broker: publish stock or weight event
    Broker-->>Gateway: deliver message
    Gateway->>Inventory: POST /telemetry
    Inventory->>Inventory: update shelf inventory state
    Inventory->>Inventory: compare current quantity with threshold
    Inventory->>Events: write REPLENISHMENT_REQUIRED event
    Events-->>WMS: replenishment integration event
```

质量属性响应分析：该流程对应 QAS-009。库存状态更新与补货事件发布由 `inventory-service` 负责，外部可通过 replenishment-service 或 WMS 集成消费者接入，而不改变设备接入链路。
