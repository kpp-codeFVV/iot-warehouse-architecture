# QA Traceability Matrix - IoT 智能仓储监控与告警平台

此矩阵用于核对质量属性场景、ADR、视图和验证证据之间是否能对应起来。验证结论使用 Pass、Pass for prototype、Partial、Fail 表示。

| QAS编号 | 质量场景 | 相关ADR | 相关视图 | 验证证据 | 验证结论 |
| --- | --- | --- | --- | --- | --- |
| QAS-001 | 异常温度 5 秒内告警 | ADR-005 | Dynamic_Views DV-001, Container_View | PoC-001, FI-003 | Pass |
| QAS-002 | 设备消息高吞吐接入 | ADR-001, ADR-002 | Context_View, Container_View, Deployment_View | LoadTest_Report | Partial |
| QAS-003 | 云端短暂不可用后的边缘补传 | ADR-002, ADR-006 | Dynamic_Views DV-002, Component_View | PoC-002, FI-001, FI-002 | Pass for prototype |
| QAS-004 | 设备离线后仍可查询最后状态 | ADR-004 | Component_View | PoC-003, unit test | Pass |
| QAS-005 | 传感器历史数据按时间查询 | ADR-003 | Container_View, Deployment_View | LoadTest_Report | Partial |
| QAS-006 | 伪造设备接入被拒绝 | ADR-001 | Context_View, Component_View | Security design in ADR-001 and Risk_List | Partial |
| QAS-007 | 告警规则变更不影响设备接入 | ADR-005 | Component_View | Tech_Debt DEBT-008, Evolution_Roadmap v1.1, Breaking_Change_Log BC-001 | Partial |
| QAS-008 | 批量设备升级不影响在线采集 | ADR-002, ADR-004 | Deployment_View, Component_View | Tech_Debt DEBT-009, Evolution_Roadmap v2.0, Breaking_Change_Log BC-008 | Partial |
| QAS-009 | 库存低于阈值触发补货事件 | ADR-005 | Dynamic_Views DV-003 | PoC-001 low-stock event | Pass for prototype |

## 验证覆盖总结

| 结论 | 数量 | 说明 |
| --- | --- | --- |
| Pass | 2 | QAS-001、QAS-004 已通过本地原型或单元测试验证 |
| Pass for prototype | 2 | QAS-003、QAS-009 在最小原型中成立 |
| Partial | 5 | 已有设计或局部验证，但还需要真实中间件、生产安全、数据库存储或演进阶段继续验证 |
| Fail | 0 | 当前没有完全失败的质量场景，但 QAS-002 只完成 smoke test |

## 关键说明

- 本地机器已完成 Docker Desktop + WSL2 初始化，`docker compose -p iot-warehouse up -d` 已在本机验证。由于项目目录包含中文，Compose 命令需要显式指定 `-p iot-warehouse`。
- LoadTest 当前证明脚本和服务链路可运行，并暴露 JSON/JSONL 文件存储不适合并发写入；它不代表生产吞吐。
- 安全性、OTA、多仓库边缘节点属于文档设计和演进范围，不作为当前最小原型主线。
