# PRD v2 — Langtian NATS EDA (精简与收敛)

版本：2.0
日期：2025-08-26

## 目标（收敛后）

提供一个在 Windows 单机/多机环境下可原生部署的 NATS 中心化 EDA 平台，优先保障：

- 端到端可靠性与最小部署复杂度（MVP 路径）
- 明确的 schema 合约与轻量演化策略（proto 优先）
- 可观测与自动恢复能力，支持 HA 的简化方案

## 被废弃/延后路径

- 废弃：在初期同时实现 sql-flow 原生 NATS Source（该路径后续再评估）

- 废弃：容器化优先部署（Windows 场景下，优先本机原生服务）

## 决策要点（收敛后的核心方案）

1. MVP 消息流：物理设备/采集器 → NATS/JetStream → nats-kafka 桥 → Kafka topic → sql-flow (Kafka Source) → Duck Lake (Parquet on S3/MinIO) → 前端 (WebView2 React + TanStack UI)。

2. 部署形态：所有后端组件（nats-kafka 桥、sql-flow、.NET UDP 采集器）以 Windows Service / .NET Worker 形式在单机或多机上原生部署；NATS JetStream 作为集群服务（可跨机器部署）。

3. Schema 与合约：使用 protobuf 作为消息 schema（轻量 proto），所有 proto 放在专门的 Git 仓库并通过 CI 做兼容性检查与 artifacts 生成；每条事件携带 `schema_version`。

4. 事件 envelope：必须包含 event_id, event_type, event_timestamp, schema_version, source_system, 可选 partition_key, payload。

5. 数据一致性策略：MVP 使用桥接 ACK-on-Kafka-success 策略（至少一次）；长期目标是在 sql-flow 内实现 commit-after-sink 的近似 exactly-once 模型并减小对桥的依赖。

## Windows 原生部署下的简化 HA 方案（兼顾可用与简运维）

- NATS/JetStream：部署为独立 Windows 节点（至少 3 节点），启用 JetStream replication (replicas >=2)，并保证时间同步与磁盘监控。

- nats-kafka 桥：以 Windows Service 部署在多台机器上（至少 2 台），配置共享的 connector 存储并通过轮询或配置管理工具分发配置；使用 durable consumer group / queue 实现负载均衡。

- sql-flow (处理层)：以 Windows Service 形式部署多个实例，使用 Kafka consumer group 或 JetStream durable consumers 保证负载与容错；实例升级前使用 drain+commit 策略。

- 对象存储（MinIO/S3）：可选择独立服务或企业 S3；Parquet 写入采用临时文件 + 原子 rename 或 Iceberg 表实现事务性写入。

## Protobuf 极简 schema 流程（设计与演化）

- 管理：所有 proto 文件放入 `proto/` 仓库，PR 必须通过 CI 的兼容性检查（例如 buf 或自定义脚本）。

- 版本：每次不兼容变更 bump major 版本并在 envelope 中写入 `schema_version`（例如 1.0 → 2.0）。

- 生成：CI 生成语言绑定与编译产物（JS/TS, Python, C#）并发布为内部 artifact 供部署使用。

## 最小 PoC 与验证计划（短期 2 周目标）

1. 在两台 Windows 机器上部署 NATS (JetStream) + nats-kafka 桥（Windows Service）并验证 ACK-on-Kafka-success 的写入成功率与端到端延迟。

2. 实现 proto 仓库与 CI 流水线，提交一次非破坏性 schema 变更并验证兼容性检查。

3. 在 WebView2 上实现 IndexedDB 的压测（100k 条），记录持久化与响应指标。

## 路线图与未来方向

- 序列化：短期优先桥接到 Kafka；中期评估在 sql-flow 内实现 JetStream Source（commit-after-sink）。

- 存储：评估 Iceberg 作为长期对象存储层支持事务性写入与回滚。

- 可观测：Prometheus 指标 + Alert 规则（source_read_latency P99、sink_flush_latency P99、error rate 等）。

---

(文件生成时间：2025-08-26)
