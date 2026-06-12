# Submission Polish Design

日期：2026-06-12

## 目标

对课程作业文档做提交前表达修订，让文档更接近团队自己整理后的工程报告。修订目标不是规避 AI 检测，而是降低模板腔、减少重复口号、补充真实验证边界，让团队成员能读懂、能解释、能承担文档内容。

## 修订范围

重点处理老师最可能阅读和评分的文件：

- `docs/00_final/Final_Report.md`
- `docs/01_adf/ADF_Brief.md`
- `docs/01_adf/Quality_Scenarios.md`
- `docs/03_adrs/*.md`
- `docs/05_evidence/LoadTest_Report.md`
- `docs/05_evidence/QA_Traceability.md`
- `docs/06_evolution/Evolution_Roadmap.md`
- `docs/06_evolution/Breaking_Change_Log.md`

不改代码，不改变架构结论，不把没有实测达标的质量属性写成达标。

## 表达原则

1. 保留课程要求的结构、编号、表格和追溯关系。
2. 把过于模板化的表达改成更自然的团队报告语气。
3. 减少“证明、闭环、生产级、课程原型”等词的高频堆叠，但保留必要概念。
4. 明确写出本地压测的真实结果和暴露的问题：JSON 文件存储不适合并发写入。
5. 对团队成员、学号、贡献率等真实信息，只提示需要填写，不编造。
6. 不加入虚假的人工讨论记录、虚假的会议过程或虚假的测试结果。

## 验证方式

- 使用 `rg` 检查明显占位词和过度模板词。
- 使用 `rg` 检查核心质量场景、ADR、Phase 5、Docker 命令仍然存在。
- 运行单元测试确认文档修订没有影响代码。
- 检查 git diff，确认只修改文档。
