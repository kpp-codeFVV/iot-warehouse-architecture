# IoT 智能仓储监控与告警平台

本项目是《软件体系结构》课程期末大作业选题二“物联网智能仓储管理系统”的架构原型与文档工程。

## 项目目标

项目聚焦物流仓储场景，通过模拟温湿度传感器、重量传感器、RFID 扫码设备和 AGV 状态设备，验证 IoT 设备接入、边云协同、设备影子、时序数据存储、事件驱动告警和边缘缓存补传等关键架构决策。

本项目不实现完整 WMS 或 ERP 系统。代码原型只用于证明架构决策可运行、可验证、可追溯。

## 当前阶段

当前正在完成 Phase 1：架构驱动因素。

- `docs/01_adf/ADF_Brief.md`：架构驱动因素简报
- `docs/01_adf/Quality_Scenarios.md`：质量属性场景清单
- `docs/superpowers/specs/2026-06-02-iot-smart-warehouse-design.md`：已确认的设计文档
- `docs/superpowers/plans/2026-06-02-phase-1-adf.md`：当前实施计划

## 计划中的原型服务

- `apps/device-gateway/`：边缘设备网关，负责 MQTT 消息接入、校验、缓存和转发。
- `apps/inventory-service/`：库存与设备影子服务，负责设备状态、库存状态和补货事件。
- `apps/alert-service/`：告警服务，负责消费异常事件并生成告警记录。

## 计划中的本地环境

后续原型将通过 `docker-compose up` 一键启动，包含 MQTT Broker、TimescaleDB 和三个 FastAPI 服务。
