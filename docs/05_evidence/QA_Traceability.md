# QA Traceability Matrix - IoT 智能仓储监控与告警平台



| QAS编号 | 质量场景 | 相关ADR | 相关视图 | 验证证据 | 验证结论 |
| --- | --- | --- | --- | --- | --- |
| QAS-001 | 异常温度 5 秒内告警 | ADR-005 | Dynamic_Views DV-001, Container_View | PoC-001, FI-003 | Pass |
| QAS-002 | 设备消息高吞吐接入 | ADR-001, ADR-002 | Context_View, Container_View, Deployment_View | LoadTest_Report | Partial：10,000 设备接入已验证，50,000 msg/s 未达到 |
| QAS-003 | 云端短暂不可用后的边缘补传 | ADR-002, ADR-006 | Dynamic_Views DV-002, Component_View | PoC-002, FI-001, FI-002 | Pass for prototype |
| QAS-004 | 设备离线后仍可查询最后状态 | ADR-004 | Component_View | PoC-003, unit test | Pass |
| QAS-005 | 传感器历史数据按时间查询 | ADR-003 | Container_View, Deployment_View | LoadTest_Report | Pass for prototype |
| QAS-006 | 伪造设备接入被拒绝 | ADR-001 | Context_View, Component_View | Security design in ADR-001 and Risk_List | Partial |
| QAS-007 | 告警规则变更不影响设备接入 | ADR-005 | Component_View | Tech_Debt DEBT-008, Evolution_Roadmap v1.1 | Partial |
| QAS-008 | 批量设备升级不影响在线采集 | ADR-002, ADR-004 | Deployment_View, Component_View | Tech_Debt DEBT-009, Evolution_Roadmap v2.0 | Partial |
| QAS-009 | 库存低于阈值触发补货事件 | ADR-005 | Dynamic_Views DV-003 | PoC-001 low-stock event | Pass for prototype |
