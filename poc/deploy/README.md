CloudBase 部署说明

前提：
- 将 PoC 的 Python Docker 镜像推送到 DockerHub（或其他 registry）。
- 在 GitHub 仓库中设置 secrets：DOCKERHUB_USERNAME、DOCKERHUB_TOKEN、CLOUDBASE_SECRET（视 CloudBase 接入方式而定）。

手动部署概览：
1. 构建并推送镜像：
   docker build -t <user>/langtian-nats-python-poc:latest poc/sqlflow_source/python_impl
   docker push <user>/langtian-nats-python-poc:latest
2. 在 CloudBase 控制台创建应用，填写镜像地址并配置环境变量。
3. 启动应用并检查日志。若需要更多自动化，可使用 CloudBase CLI/API 并把步骤写入 GitHub Actions。 
