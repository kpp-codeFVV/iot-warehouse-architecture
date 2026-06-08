# Prototype and Phase 4 Evidence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a minimal runnable FastAPI prototype and generate Phase 4 validation evidence documents for the IoT smart warehouse project.

**Architecture:** The prototype keeps the approved three-service architecture: `device-gateway`, `inventory-service`, and `alert-service`. MQTT and TimescaleDB are represented in Docker Compose and contracts, while local validation uses HTTP and file-backed storage so evidence can be generated without Docker on the current machine.

**Tech Stack:** Python, FastAPI, Uvicorn, pytest, HTTP JSON contracts, JSONL event files, Docker Compose specification, Markdown evidence reports.

---

## File Structure

- Modify: `.gitignore` - ignore `.venv/`, `runtime/`, and Python caches.
- Create: `requirements.txt` - runtime and test dependencies.
- Create: `libs/iot_core.py` - shared telemetry validation, device shadow, alert, cache replay, and file store helpers.
- Create: `apps/device-gateway/main.py` - FastAPI edge gateway API.
- Create: `apps/inventory-service/main.py` - FastAPI inventory and device shadow API.
- Create: `apps/alert-service/main.py` - FastAPI alert API.
- Create: `tests/test_iot_core.py` - focused unit tests for the core validation behaviors.
- Create: `contracts/events/*.json` - JSON Schema for telemetry, abnormal alert, and replenishment events.
- Create: `contracts/openapi/*.yaml` - concise OpenAPI contract summaries for the three services.
- Create: `scripts/data-gen/send_sample.py` - sends normal or abnormal sample telemetry to the gateway.
- Create: `scripts/load-test/local_load.py` - local HTTP load test script.
- Create: `scripts/fault-injection/cloud_outage_demo.py` - simulates inventory outage and replay behavior.
- Create: `docker-compose.yml` - course deliverable one-command topology.
- Create: `Makefile` - common commands.
- Create: `docs/05_evidence/PoC_Report.md` - PoC design and local validation result summary.
- Create: `docs/05_evidence/LoadTest_Report.md` - load test design and local execution boundary.
- Create: `docs/05_evidence/FaultInjection.md` - fault injection design and local execution boundary.
- Create: `docs/05_evidence/QA_Traceability.md` - QAS-to-ADR-to-view-to-evidence matrix.
- Create: `docs/07_runbook/Local_Setup.md` - local setup guide.
- Create: `docs/07_runbook/Demo_Steps.md` - demo script.

## Task 1: Prototype Core and Services

**Files:**
- Modify: `.gitignore`
- Create: `requirements.txt`
- Create: `libs/iot_core.py`
- Create: `apps/device-gateway/main.py`
- Create: `apps/inventory-service/main.py`
- Create: `apps/alert-service/main.py`
- Create: `tests/test_iot_core.py`

- [ ] **Step 1: Add dependency and ignore files**

Add Python dependencies and ignore generated runtime files.

- [ ] **Step 2: Implement shared core**

Create `libs/iot_core.py` with dataclass-free standard Python helpers for telemetry validation, shadow updates, alert generation, JSONL persistence, edge cache append/replay, and idempotency by `messageId`.

- [ ] **Step 3: Implement FastAPI services**

Create one `main.py` per service. Each service must expose `/health`; gateway exposes `/ingest`, `/cache`, `/replay`; inventory exposes `/telemetry`, `/shadows`, `/inventory`, `/events`; alert exposes `/process-events`, `/alerts`.

- [ ] **Step 4: Add unit tests**

Create tests covering abnormal temperature alert generation, stale device shadow rejection, edge cache replay idempotency, and low-stock replenishment event generation.

- [ ] **Step 5: Verify tests**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests -q
```

Expected: all tests pass.

- [ ] **Step 6: Commit prototype core**

Run:

```powershell
git add .gitignore requirements.txt libs/iot_core.py apps/device-gateway/main.py apps/inventory-service/main.py apps/alert-service/main.py tests/test_iot_core.py
git commit -m "feat: add minimal IoT prototype services"
```

## Task 2: Contracts, Scripts, and Runtime Topology

**Files:**
- Create: `contracts/events/telemetry.schema.json`
- Create: `contracts/events/abnormal_event.schema.json`
- Create: `contracts/events/replenishment_event.schema.json`
- Create: `contracts/openapi/device-gateway.yaml`
- Create: `contracts/openapi/inventory-service.yaml`
- Create: `contracts/openapi/alert-service.yaml`
- Create: `scripts/data-gen/send_sample.py`
- Create: `scripts/load-test/local_load.py`
- Create: `scripts/fault-injection/cloud_outage_demo.py`
- Create: `docker-compose.yml`
- Create: `Makefile`

- [ ] **Step 1: Write event schemas and OpenAPI summaries**

Contracts must match the payload fields used by `libs/iot_core.py`.

- [ ] **Step 2: Write validation scripts**

Scripts must be runnable with `.venv\Scripts\python.exe` and use only Python standard library HTTP clients.

- [ ] **Step 3: Write Docker Compose and Makefile**

Docker Compose must define `device-gateway`, `inventory-service`, `alert-service`, `mosquitto`, `redis`, and `timescaledb`, while documenting whether Docker daemon verification is available in the current environment.

- [ ] **Step 4: Verify scripts compile**

Run:

```powershell
.\.venv\Scripts\python.exe -m py_compile scripts/data-gen/send_sample.py scripts/load-test/local_load.py scripts/fault-injection/cloud_outage_demo.py
```

Expected: command exits with code 0.

- [ ] **Step 5: Commit contracts and scripts**

Run:

```powershell
git add contracts/events contracts/openapi scripts/data-gen scripts/load-test scripts/fault-injection docker-compose.yml Makefile
git commit -m "feat: add prototype contracts and validation scripts"
```

## Task 3: Phase 4 Evidence and Runbooks

**Files:**
- Create: `docs/05_evidence/PoC_Report.md`
- Create: `docs/05_evidence/LoadTest_Report.md`
- Create: `docs/05_evidence/FaultInjection.md`
- Create: `docs/05_evidence/QA_Traceability.md`
- Create: `docs/07_runbook/Local_Setup.md`
- Create: `docs/07_runbook/Demo_Steps.md`

- [ ] **Step 1: Write evidence documents**

Evidence documents must distinguish verified local results from Docker-dependent steps that could not be run because Docker daemon is unavailable.

- [ ] **Step 2: Write runbooks**

Runbooks must include local `.venv` commands, service startup commands, script examples, Docker Compose commands, and the current environment limitation.

- [ ] **Step 3: Verify Phase 4 files**

Run:

```powershell
$files = @(
  'docs/05_evidence/PoC_Report.md',
  'docs/05_evidence/LoadTest_Report.md',
  'docs/05_evidence/FaultInjection.md',
  'docs/05_evidence/QA_Traceability.md',
  'docs/07_runbook/Local_Setup.md',
  'docs/07_runbook/Demo_Steps.md'
)
foreach ($file in $files) {
  if (-not (Test-Path $file)) {
    "$file missing"
    exit 1
  }
}
'phase 4 docs ok'
```

Expected: prints `phase 4 docs ok`.

- [ ] **Step 4: Commit evidence and runbooks**

Run:

```powershell
git add docs/05_evidence docs/07_runbook
git commit -m "docs: add phase 4 evidence and runbooks"
```

## Task 4: Final Verification

**Files:**
- Review all files created in this plan.

- [ ] **Step 1: Run unit tests**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests -q
```

Expected: all tests pass.

- [ ] **Step 2: Run compile checks**

Run:

```powershell
.\.venv\Scripts\python.exe -m py_compile libs/iot_core.py apps/device-gateway/main.py apps/inventory-service/main.py apps/alert-service/main.py scripts/data-gen/send_sample.py scripts/load-test/local_load.py scripts/fault-injection/cloud_outage_demo.py
```

Expected: command exits with code 0.

- [ ] **Step 3: Verify traceability keywords**

Run:

```powershell
$content = (Get-ChildItem docs/05_evidence,docs/07_runbook -Filter '*.md' -Recurse | ForEach-Object { Get-Content $_.FullName -Raw -Encoding utf8 }) -join "`n"
$terms = @('QAS-001','QAS-002','QAS-003','ADR-001','ADR-005','ADR-006','PoC-001','PoC-002','LoadTest','FaultInjection')
foreach ($term in $terms) {
  if ($content -notlike "*$term*") {
    "missing $term"
    exit 1
  }
}
'evidence traceability ok'
```

Expected: prints `evidence traceability ok`.

## Self-Review Notes

- Spec coverage: The plan covers the required runnable services, REST API contracts, event schemas, validation scripts, Docker Compose topology, Phase 4 evidence documents, and runbooks.
- Placeholder scan: The plan contains no unresolved placeholder instructions.
- Environment note: Docker CLI may be installed while Docker daemon remains unavailable; Docker Compose can be written even when not locally executable here.
