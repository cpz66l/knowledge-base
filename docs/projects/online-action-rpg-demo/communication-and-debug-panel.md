# 项目骨架、通信验证与 Unity 调试面板

> 所属项目：[Online Action RPG Demo](index.md)
>
> 覆盖迭代：00 / 00B
>
> 学习状态：项目中使用
>
> 证据归属：用户项目实践与运行记录；本次整理未重新运行 Unity、服务端或 smoke test
>
> 下一步：复用网络入口进入账号、Lobby 和战斗同步

## 学习目标

- 先跑通 Unity 客户端与本地 .NET 服务端的最小通信闭环。
- 用 Ping / Pong 验证端口监听、WebSocket 握手、JSON 协议结构、请求响应匹配和 RTT 显示。
- 建立可视化网络调试面板，让后续账号、房间和战斗同步不靠盲调。

## 完成内容

### 服务端骨架

- 使用 `global.json` 固定 .NET SDK 到 9.0.315。
- 创建 `Server/OnlineRpgServer/OnlineRpgServer.csproj`，目标框架为 `net9.0`。
- 建立 WebSocket 入口：`ws://localhost:5050/ws`。
- 建立健康检查：`GET http://localhost:5050/health`。
- 建立基础协议信封：`msgId / type / requestId / token / clientTime / serverTime / code / message / payload`。
- 建立调试消息：`PingReq = 9001`、`PingRes = 9002`、`ErrorRes = 9999`。
- 新增 `Tools/SmokeTests/Test-ServerPing.ps1`，用于不依赖 Unity 的服务端通信 smoke test。

### Unity 客户端调试入口

- 建立 `INetworkTransport`，让业务层不直接依赖具体 WebSocket API。
- 建立 `WebSocketTransport`，只负责连接、发送、接收和关闭。
- 建立 `NetworkClient`，负责构造 Ping、计算 RTT、缓存最近协议日志和连接状态。
- 建立 `ProtocolEnvelope` 和 `NetworkMessageIds`，对齐服务端协议结构和消息编号。
- 建立 `NetworkDebugPanel`，负责按钮绑定和 UI 文本刷新。

推荐分层：

```text
NetworkDebugPanel
  -> NetworkClient
  -> INetworkTransport
  -> WebSocketTransport
  -> OnlineRpgServer /ws
```

## 关键设计取舍

### 为什么先做 Ping / Pong

Ping / Pong 不引入账号、房间、战斗状态和 UI 跳转，因此可以最早验证通信基础。如果直接从登录开始，连接失败、协议失败和业务失败会混在一起，排查成本更高。

### 为什么先用 WebSocket + JSON

MVP 阶段优先可读、可调试、可截图。JSON 能直接出现在服务端控制台、客户端日志面板和 PowerShell smoke test 中，适合学习与作品集解释。

对战斗同步来说，WebSocket / TCP 存在队头阻塞等限制。当前策略是先跑通可靠低频业务链路，后续再通过 `INetworkTransport` 评估 UDP / KCP 或二进制协议替换，不把未来方案写成当前完成。

### 为什么使用 `lock + Snapshot`

网络异步回调会修改连接状态、最近收发包、错误信息和 RTT，Unity 主线程每帧会读取这些字段刷新 UI。`NetworkClient` 使用轻量 `lock` 一次性复制 `NetworkClientSnapshot`，让 UI 读到一致状态。

这只适合低频调试状态。后续进入高频战斗同步后，更适合升级为：

```text
ConcurrentQueue<NetworkEvent>
  -> 网络回调入队
  -> Unity Update 每帧消费事件
  -> 表现层刷新
```

## 验证记录

用户原始记录中保留的验证：

- `dotnet build Server\OnlineRpgServer\OnlineRpgServer.csproj` 成功，0 warning / 0 error。
- `GET http://localhost:5050/health` 返回 `OK`。
- `Tools\SmokeTests\Test-ServerPing.ps1` 返回 `ok:true`、`responseType:"PingRes"`、`code:0` 并输出 RTT。
- 服务端日志能看到客户端连接、接收 `PingReq`、发送 `PingRes` 和客户端断开。
- Unity Editor 日志出现 `Tundra build success`。
- 用户在 Unity Play Mode 中完成客户端连接和 Ping / Pong 手动验证。

本次整理未重新运行这些命令，也未启动 Unity Editor。

## 当前边界

已完成：

- 服务端最小 WebSocket 通信。
- Unity 客户端最小网络调试面板。
- Ping / Pong、RTT、协议日志和断线状态的基础验证。

未完成：

- 账号登录、大厅房间和战斗同步在本迭代之外。
- UDP / KCP、MessagePack / Protobuf、客户端预测和回滚只是后续方向。
- 截图 / 录屏证据仍可继续补强。

## 面试表达

可以说：

> 项目启动阶段先搭建 Unity 客户端与 .NET 服务端的最小 WebSocket 通信链路，使用 JSON 协议信封完成 `PingReq / PingRes`、RTT 统计、协议日志和网络调试面板，为后续账号、大厅和战斗同步预留了传输层抽象。

不要说：

- 已完成网络同步。
- 已实现 UDP / KCP 战斗通信。
- 已完成商业级网络框架。

