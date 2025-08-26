# SQL-Flow 原生 NATS Source 设计

目标：在 sql-flow 中实现一个原生 NATS JetStream Source 插件，支持 pull-based 批处理、ack-after-sink 的 commit 流程以及 DLQ 处理。

设计要点：

- 使用 durable pull consumer 来拉取批次消息，批次大小与等待超时可配置。
- 将批次封装并调用 sql-flow 的 pipeline API；在 sink 成功后对消息进行 ack/确认。
- 失败策略：重试若干次后写入 DLQ；并暴露指标和日志以便 SRE 排查。