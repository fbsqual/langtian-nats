# EDA 平台(基于 NATS 的实时事件驱动架构) - PRD 草稿

## 目标
构建一个以 NATS 为中心的事件驱动平台（EDA），包含：
- Windows 客户端(WebView2 + React)、nats.js、TanStack Table
- 后端边缘采集服务：.NET Core UDP 采集器（带任务栏托盘管理）
- 中心消息总线：NATS + JetStream
- 持久化与分析：sql-flow -> DuckDB/Parquet (Duck Lake)

...（已合并到 PRD_v2）
