# Phase 2 Views and ADRs Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create the Phase 2 C4 architecture view package and six architecture decision records for the IoT smart warehouse project.

**Architecture:** The views describe the approved edge-cloud collaborative architecture from multiple levels: system context, containers, high-risk components, runtime sequences, and deployment topology. ADRs record the major decisions that explain why this architecture uses MQTT, edge-cloud responsibilities, TimescaleDB, device shadow, event-driven alerting, and edge cache replay.

**Tech Stack:** Markdown, Mermaid diagrams, ADR markdown templates, Git, PowerShell verification commands.

---

## File Structure

- Create: `docs/02_views/Context_View.md` - C4 Level 1 system context view.
- Create: `docs/02_views/Container_View.md` - C4 Level 2 container view.
- Create: `docs/02_views/Component_View.md` - C4 Level 3 component views for `device-gateway` and `inventory-service`.
- Create: `docs/02_views/Dynamic_Views.md` - at least three sequence diagrams for key runtime scenarios.
- Create: `docs/02_views/Deployment_View.md` - production-style deployment topology and HA strategy.
- Create: `docs/02_views/View_Consistency_Check.md` - consistency matrix across views, ADRs, and quality scenarios.
- Create: `docs/03_adrs/ADR_Index.md` - ADR index table.
- Create: `docs/03_adrs/ADR-001_mqtt_protocol.md` - MQTT protocol decision.
- Create: `docs/03_adrs/ADR-002_edge_cloud_architecture.md` - edge-cloud responsibility decision.
- Create: `docs/03_adrs/ADR-003_timescaledb.md` - time-series storage decision.
- Create: `docs/03_adrs/ADR-004_device_shadow.md` - device shadow decision.
- Create: `docs/03_adrs/ADR-005_event_driven_alerting.md` - alert pipeline decision.
- Create: `docs/03_adrs/ADR-006_edge_cache_replay.md` - edge cache and replay decision.

## Task 1: Create C4 View Package

**Files:**
- Create: `docs/02_views/Context_View.md`
- Create: `docs/02_views/Container_View.md`
- Create: `docs/02_views/Component_View.md`
- Create: `docs/02_views/Dynamic_Views.md`
- Create: `docs/02_views/Deployment_View.md`

- [ ] **Step 1: Write context view**

Create `docs/02_views/Context_View.md` with these sections:

- Title: `# Context View - IoT 智能仓储监控与告警平台`
- Purpose: explain this is C4 Level 1.
- Mermaid diagram showing warehouse administrator, operations engineer, logistics operator, IoT devices, external WMS/ERP, and the IoT smart warehouse platform.
- Relationship table with protocol, data format, and sync/async nature for each external interaction.
- Traceability section linking QAS-001, QAS-002, QAS-003, QAS-004, QAS-006, and QAS-009.

- [ ] **Step 2: Write container view**

Create `docs/02_views/Container_View.md` with these sections:

- Title: `# Container View - IoT 智能仓储监控与告警平台`
- Mermaid container diagram showing simulated devices, Mosquitto MQTT Broker, `device-gateway`, `inventory-service`, `alert-service`, TimescaleDB, Redis Stream or event channel, and future external systems.
- Container responsibility table including technology choice, responsibility, and exposed interface.
- Communication table including REST, MQTT, event stream, SQL, sync/async, and data format.
- Traceability section linking all six ADRs.

- [ ] **Step 3: Write component view**

Create `docs/02_views/Component_View.md` with these sections:

- Title: `# Component View - IoT 智能仓储监控与告警平台`
- `device-gateway` component diagram and table: MQTT subscriber, device authenticator, message validator, edge cache, cloud forwarder, replay worker, health API.
- `inventory-service` component diagram and table: telemetry ingest API, device shadow manager, inventory updater, rule evaluator, event publisher, query API.
- Brief note that `alert-service` is expanded in dynamic views and ADR-005 because its behavior is centered on event consumption.
- Traceability to QAS-001, QAS-003, QAS-004, QAS-007, and QAS-009.

- [ ] **Step 4: Write dynamic views**

Create `docs/02_views/Dynamic_Views.md` with at least three Mermaid sequence diagrams:

- DV-001: normal telemetry to abnormal alert generation.
- DV-002: cloud unavailable, edge cache, restore, replay.
- DV-003: RFID or weight update triggers low-stock replenishment event.

Each sequence must include a short quality attribute response analysis.

- [ ] **Step 5: Write deployment view**

Create `docs/02_views/Deployment_View.md` with:

- Production-style Mermaid topology showing warehouse edge node, cloud region, availability zones, load balancer, services, TimescaleDB, event channel, monitoring.
- Network partitions: device network, edge network, private service network, data network.
- HA strategy: broker restart, service replicas, database backup, degraded local cache mode.
- Note that the course prototype maps this production topology to Docker Compose.

- [ ] **Step 6: Verify views**

Run:

```powershell
$files = @(
  'docs/02_views/Context_View.md',
  'docs/02_views/Container_View.md',
  'docs/02_views/Component_View.md',
  'docs/02_views/Dynamic_Views.md',
  'docs/02_views/Deployment_View.md'
)
foreach ($file in $files) {
  if (-not (Test-Path $file)) {
    "$file missing"
    exit 1
  }
  $content = Get-Content $file -Raw -Encoding utf8
  if ($content -notmatch '```mermaid') {
    "$file missing mermaid diagram"
    exit 1
  }
}
'views ok'
```

Expected: prints `views ok`.

- [ ] **Step 7: Commit views**

Run:

```powershell
git add docs/02_views/Context_View.md docs/02_views/Container_View.md docs/02_views/Component_View.md docs/02_views/Dynamic_Views.md docs/02_views/Deployment_View.md
git commit -m "docs: add phase 2 architecture views"
```

Expected: Git creates a commit named `docs: add phase 2 architecture views`.

## Task 2: Create ADR Package

**Files:**
- Create: `docs/03_adrs/ADR_Index.md`
- Create: `docs/03_adrs/ADR-001_mqtt_protocol.md`
- Create: `docs/03_adrs/ADR-002_edge_cloud_architecture.md`
- Create: `docs/03_adrs/ADR-003_timescaledb.md`
- Create: `docs/03_adrs/ADR-004_device_shadow.md`
- Create: `docs/03_adrs/ADR-005_event_driven_alerting.md`
- Create: `docs/03_adrs/ADR-006_edge_cache_replay.md`

- [ ] **Step 1: Write ADR index**

Create `docs/03_adrs/ADR_Index.md` with a table containing columns: ADR编号, 标题, 状态, 关联QAS, 关联容器/组件, 最后更新.

- [ ] **Step 2: Write six ADRs**

Each ADR must include these exact sections:

- `## 状态`
- `## 背景`
- `## 决策驱动因素`
- `## 可选方案`
- `## 决策结果`
- `## 后果`
- `## 验证方式`

ADR topics:

- ADR-001 chooses MQTT over CoAP and AMQP.
- ADR-002 chooses edge-cloud collaboration over cloud-only and edge-only.
- ADR-003 chooses TimescaleDB over InfluxDB and TDengine.
- ADR-004 chooses device shadow over real-time-only state and direct device queries.
- ADR-005 chooses event-driven alerting over synchronous alert calls and database polling.
- ADR-006 chooses edge gateway cache replay over dropping messages or relying only on device-side cache.

- [ ] **Step 3: Verify ADR count and sections**

Run:

```powershell
$adrFiles = Get-ChildItem 'docs/03_adrs' -Filter 'ADR-*.md'
if ($adrFiles.Count -ne 6) {
  "ADR count is $($adrFiles.Count), expected 6"
  exit 1
}
$sections = @('## 状态','## 背景','## 决策驱动因素','## 可选方案','## 决策结果','## 后果','## 验证方式')
foreach ($file in $adrFiles) {
  $content = Get-Content $file.FullName -Raw -Encoding utf8
  foreach ($section in $sections) {
    if (-not $content.Contains($section)) {
      "$($file.Name) missing $section"
      exit 1
    }
  }
}
'adrs ok'
```

Expected: prints `adrs ok`.

- [ ] **Step 4: Commit ADRs**

Run:

```powershell
git add docs/03_adrs/ADR_Index.md docs/03_adrs/ADR-*.md
git commit -m "docs: add architecture decision records"
```

Expected: Git creates a commit named `docs: add architecture decision records`.

## Task 3: Create View Consistency Check

**Files:**
- Create: `docs/02_views/View_Consistency_Check.md`

- [ ] **Step 1: Write consistency matrix**

Create `docs/02_views/View_Consistency_Check.md` with:

- A matrix checking that service names are consistent across context, container, component, dynamic, and deployment views.
- A matrix checking that each ADR appears in at least one view.
- A matrix checking that key QAS IDs have corresponding ADRs and view evidence.
- A short list of accepted limitations for the course prototype.

- [ ] **Step 2: Verify no unresolved placeholders**

Run:

```powershell
$files = Get-ChildItem 'docs/02_views','docs/03_adrs' -Filter '*.md' -Recurse
$patterns = @('TO' + 'DO', 'TB' + 'D', '待' + '定', '占' + '位', 'x' + 'x' + 'x', 'X' + 'X' + 'X')
foreach ($pattern in $patterns) {
  $matches = $files | Select-String -Pattern $pattern -CaseSensitive:$false -Encoding utf8
  if ($matches) {
    $matches
    exit 1
  }
}
'no placeholders ok'
```

Expected: prints `no placeholders ok`.

- [ ] **Step 3: Verify traceability keywords**

Run:

```powershell
$content = Get-ChildItem 'docs/02_views','docs/03_adrs' -Filter '*.md' -Recurse | Get-Content -Raw -Encoding utf8
$terms = @('MQTT','边云协同','TimescaleDB','设备影子','事件驱动','边缘缓存','QAS-001','ADR-001')
foreach ($term in $terms) {
  if ($content -notlike "*$term*") {
    "missing $term"
    exit 1
  }
}
'traceability keywords ok'
```

Expected: prints `traceability keywords ok`.

- [ ] **Step 4: Commit consistency check**

Run:

```powershell
git add docs/02_views/View_Consistency_Check.md
git commit -m "docs: add view consistency check"
```

Expected: Git creates a commit named `docs: add view consistency check`.

## Self-Review Notes

- Spec coverage: This plan covers Phase 2 required C4 views, three dynamic views, deployment view, consistency check, and six ADRs covering all required topic-two decision points.
- Placeholder scan: The plan contains no unresolved placeholder instructions.
- Type consistency: Service names are fixed as `device-gateway`, `inventory-service`, `alert-service`, MQTT Broker, TimescaleDB, and event channel across views and ADRs.
