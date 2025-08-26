# 观点与研究（意识流记录）

本文件记录在对设计/技术栈进行快速探索与专家询问时的原始想法、证据片段与临时假设（保留为意识流，供团队复核）。

- nats.js 在 WebView2 中可用，但浏览器 WebSocket 无法使用客户端 TLS 证书——需用 JWT/token 或本地 TLS 终结代理。

- sql-flow 当前支持 Kafka / WebSocket / S3/Parquet/Iceberg 等源/汇，不原生支持 NATS；两条路径：桥接（nats->kafka）或在 sql-flow 内实现 JetStream 源。

- nats-kafka 桥在配置为在 Kafka 成功写入后才 ACK JetStream 时可实现至少一次语义；Kafka producer acks=all，桥端同步写入更可靠但增加延迟。

- DuckDB 与 Arrow/Parquet 协作良好，但并发 append 同一 Parquet 文件会有风险，建议写分区化文件或使用 Iceberg 来保证事务性。

- TanStack DB 为前端提供强实时查询与事务语义，但处于 alpha 与预览阶段；IndexedDB 持久化能力需要额外实现或使用适配器来承载百万+行数据场景。

- Windows WebView2 打包注意：选择 Evergreen Runtime vs Fixed Runtime（Evergreen 自动更新，Fixed 可随应用一起发布）；MSIX/EXE 安装器、Squirrel/MSI 各有优劣。

- .NET 采集器（UDP）需要注意权限、服务化（IHost）、系统托盘/任务栏权限与自动化策略；Windows 服务与任务栏 UI 同步管理需设计心跳/IPC。


临时假设：

- MVP 采用桥接到 Kafka 是最短路径；长期若需减少运维组件可考虑向 sql-flow 提交原生 JetStream 源。


待验证点（行动项）：

1. 验证 TanStack DB 对 IndexedDB 的适配是否存在官方实现或社区插件；若无，评估实现成本。

2. 在 Windows/WebView2 环境下做内存与 IndexedDB 压力测试（10万/100万行）来衡量可行性。

3. 设计并测试 nats-kafka 的 ack-sync 配置与端到端延迟，记录典型延迟/吞吐/吞吐抖动。

4. 针对 schema evolution，准备 Kafka + Schema Registry 管理策略与 sql-flow 的解码器适配方案。


原始证据快照（参考）：

- nats-kafka README 与 docs

- sql-flow README 与 examples

- TanStack DB README 与 docs（alpha 状态）

- DuckDB + Parquet 推荐实践（写分区化文件，避免并发 append）


## 结束

（以上为意识流记录，未格式化或最终审校，供研发/评审参考）
