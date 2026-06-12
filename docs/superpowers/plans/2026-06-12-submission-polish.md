# Submission Polish Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Revise the course deliverable documents into a more natural, accountable team-report style while preserving technical conclusions and evidence.

**Architecture:** This is a documentation-only pass. It keeps the existing Phase 1-5 structure, ADR decisions, prototype scope, and QAS conclusions unchanged, but updates wording and load-test evidence to reflect the latest observed concurrency bottleneck.

**Tech Stack:** Markdown, Git, existing Python test suite.

---

## File Structure

- Modify: `docs/00_final/Final_Report.md`
  - Make the final report read less like a generated template and more like a team synthesis.
- Modify: `docs/01_adf/ADF_Brief.md`
  - Smooth opening and scope language.
- Modify: `docs/01_adf/Quality_Scenarios.md`
  - Make introduction and scenario notes more concise.
- Modify: `docs/03_adrs/*.md`
  - Reduce repeated "课程原型" phrasing where it is not needed.
- Modify: `docs/05_evidence/LoadTest_Report.md`
  - Add the latest serial and concurrent HTTP test results, including the JSON storage bottleneck.
- Modify: `docs/05_evidence/QA_Traceability.md`
  - Make the conclusion wording clearer and less formulaic.
- Modify: `docs/06_evolution/Evolution_Roadmap.md`
  - Smooth roadmap language and keep version plan intact.
- Modify: `docs/06_evolution/Breaking_Change_Log.md`
  - Make breaking-change language more direct.

### Task 1: Polish Final Report

**Files:**
- Modify: `docs/00_final/Final_Report.md`

- [ ] **Step 1: Rewrite cover and summary wording**

Replace placeholder-like cover descriptions with neutral fill-in guidance and rewrite the summary in first-person plural where appropriate.

- [ ] **Step 2: Reduce repeated template phrases**

Search:

```powershell
rg -n "本项目|课程原型|证明|闭环|生产级" docs\00_final\Final_Report.md
```

Expected: remaining matches are necessary technical statements, not repeated filler.

### Task 2: Polish Phase 1 And ADR Language

**Files:**
- Modify: `docs/01_adf/ADF_Brief.md`
- Modify: `docs/01_adf/Quality_Scenarios.md`
- Modify: `docs/03_adrs/*.md`

- [ ] **Step 1: Update introductory paragraphs**

Make the opening paragraphs more direct and less template-like while preserving all QAS/ADR IDs and table contents.

- [ ] **Step 2: Verify structure remains**

Run:

```powershell
rg -n "QAS-001|QAS-009|ADR-001|ADR-006|六要素|MoSCoW" docs\01_adf docs\03_adrs
```

Expected: all key IDs and required terms still appear.

### Task 3: Update Evidence Wording And Load Test Results

**Files:**
- Modify: `docs/05_evidence/LoadTest_Report.md`
- Modify: `docs/05_evidence/QA_Traceability.md`

- [ ] **Step 1: Add latest load-test results**

Add the observed test results:

```text
100 serial HTTP messages: 31.23 msg/s, 0 errors
1000 serial HTTP messages: 38.27 msg/s, 0 errors
1000 concurrent HTTP messages, 50 workers: 225.74 msg/s, 0 request errors
5000 concurrent HTTP messages, 100 workers: 237.96 msg/s, 0 request errors
```

Also record that concurrent writes corrupted JSON state and caused `Extra data: line 17 column 2`, so QAS-002 remains Partial.

- [ ] **Step 2: Verify evidence mentions boundary**

Run:

```powershell
rg -n "237.96|Extra data|JSON|Partial|50,000 msg/s" docs\05_evidence\LoadTest_Report.md docs\05_evidence\QA_Traceability.md
```

Expected: output includes latest results and the storage bottleneck.

### Task 4: Polish Phase 5 Language

**Files:**
- Modify: `docs/06_evolution/Evolution_Roadmap.md`
- Modify: `docs/06_evolution/Breaking_Change_Log.md`

- [ ] **Step 1: Smooth opening and conclusion statements**

Keep all version, QAS, ADR, DEBT, and BC references. Make wording less like a generated checklist.

- [ ] **Step 2: Verify traceability terms remain**

Run:

```powershell
rg -n "v1.1|v2.0|v3.0|QAS-00|ADR-00|DEBT-00|BC-00" docs\06_evolution
```

Expected: version roadmap and breaking-change IDs remain intact.

### Task 5: Final Verification And Commit

**Files:**
- All modified docs.

- [ ] **Step 1: Scan for placeholders**

Run:

```powershell
rg -n "TBD|TODO|待补|占位|xxx|FIXME|AI生成|ChatGPT" docs\00_final docs\01_adf docs\03_adrs docs\05_evidence docs\06_evolution
```

Expected: no matches, except no output.

- [ ] **Step 2: Run tests**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests -q
```

Expected: `4 passed`.

- [ ] **Step 3: Review git diff**

Run:

```powershell
git diff -- docs\00_final docs\01_adf docs\03_adrs docs\05_evidence docs\06_evolution docs\superpowers\plans\2026-06-12-submission-polish.md
```

Expected: only wording/evidence updates, no code changes.

- [ ] **Step 4: Commit**

Run:

```powershell
git add docs\00_final docs\01_adf docs\03_adrs docs\05_evidence docs\06_evolution docs\superpowers\plans\2026-06-12-submission-polish.md
git commit -m "docs: polish submission wording and evidence"
```

Expected: commit succeeds.
