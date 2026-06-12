# PDF Structure Fixes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Align the course deliverable documents with the structure required by `《软件体系结构》课程期末大作业 (2).pdf`.

**Architecture:** Documentation-only correction. Keep existing technical decisions and evidence, but adjust heading levels and required fields so the documents match the PDF template more closely.

**Tech Stack:** Markdown, PDF requirement text, existing test suite.

---

### Task 1: Fix ADF_Brief Heading Hierarchy

**Files:**
- Modify: `docs/01_adf/ADF_Brief.md`

- [ ] Reorganize ADF into exactly five top-level sections:
  - `## 1. 项目概述`
  - `## 2. 功能性需求摘要`
  - `## 3. 质量属性优先级排序`
  - `## 4. 约束条件`
  - `## 5. 关键干系人及其关注点`
- [ ] Move core user roles and system boundary under section 1.
- [ ] Move ASR under section 2.

### Task 2: Fix Phase 4 Required Fields

**Files:**
- Modify: `docs/05_evidence/PoC_Report.md`
- Modify: `docs/05_evidence/LoadTest_Report.md`

- [ ] Add missing PoC-003 `实验过程` and `后续行动`.
- [ ] Add P50/P95/P99 latency fields to load-test results, even where values are not measured.

### Task 3: Align Risk Table Header

**Files:**
- Modify: `docs/04_evaluation/Risk_List.md`

- [ ] Rename table headers from `负责角色`/`截止阶段` to `负责人`/`截止日期` to match the PDF wording.

### Task 4: Verify And Commit

**Files:**
- Verify all modified docs.

- [ ] Check headings and required terms with `rg`.
- [ ] Run `pytest tests -q`.
- [ ] Commit the documentation fixes.
