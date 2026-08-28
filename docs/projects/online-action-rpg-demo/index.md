# Online Action RPG Demo（线上动作 RPG Demo）

> 状态：项目中使用 / 早期联网 Demo
>
> 当前进度：迭代 00-01B 已形成 Unity 客户端与 .NET 服务端通信、账号登录闭环；迭代 02A 已完成服务端大厅 / 房间状态容器与 `RoomStateNtf` 广播；迭代 02B Unity Lobby 接入已启动但尚未完成
>
> 首次记录：2026-08-26
>
> Unity 版本：Unity 6000.3.20f1
>
> 技术栈：Unity / C#、.NET 9、WebSocket、JSON 协议、PowerShell smoke test
>
> 证据归属：用户项目实践记录、用户运行 / 手动验收记录；本次整理仅做文档归纳和静态边界判断，未重新运行 Unity、服务端或 smoke test

## 项目目标

用一个小规模线上动作 RPG Demo 验证游戏客户端联网链路，而不是只停留在单机玩法 Demo。当前阶段优先跑通：

- Unity 客户端与本地 .NET 服务端的长连接通信。
- JSON 协议信封、请求 / 响应匹配和协议日志。
- 注册 / 登录、token 会话和错误反馈。
- 大厅 / 房间的服务端权威状态、成员变化和广播通知。
- 后续战斗同步、弱网处理和作品集展示所需的调试入口。

当前项目的价值不在于“后端复杂”，而在于让客户端项目具备真实联机产品常见的进入链路：连接、登录、进入大厅、创建 / 加入房间、等待进入战斗。

## 已完成里程碑

### 迭代 00：项目骨架与通信验证

- 固定 .NET SDK 到 9.0.315，并创建 `Server/OnlineRpgServer/OnlineRpgServer.csproj`。
- 新增 WebSocket 入口：`ws://localhost:5050/ws`。
- 新增健康检查：`GET http://localhost:5050/health`。
- 新增基础协议信封和调试消息：`PingReq = 9001`、`PingRes = 9002`、`ErrorRes = 9999`。
- 新增 `Tools/SmokeTests/Test-ServerPing.ps1`，用于独立验证服务端 Ping / Pong 链路。
- 用户记录 `dotnet build`、`/health` 和 Ping smoke test 均通过。

### 迭代 00B：Unity 客户端网络接入与调试面板

- 在 Unity 工程中建立 `INetworkTransport`、`WebSocketTransport`、`NetworkClient`、`ProtocolEnvelope` 和 `NetworkDebugPanel`。
- 客户端调试面板支持 Connect、Disconnect、Ping、RTT、最近发送包、最近接收包和错误状态显示。
- `NetworkClient` 使用 `lock + Snapshot` 保护低频调试状态，让 Unity 主线程读取稳定快照。
- 用户记录 Unity Play Mode 已完成连接和 Ping / Pong 手动验证。

### 迭代 01：账号登录服务端闭环

- 新增服务端账号模型、账号服务和账号协议 payload。
- 服务端支持 `RegisterReq / RegisterRes`、`LoginReq / LoginRes` 和通用 `ErrorRes`。
- 账号数据使用服务端内存字典，token 用于本次会话识别。
- 新增 `Tools/SmokeTests/Test-ServerAccount.ps1`。
- 用户记录账号 smoke test 覆盖注册成功、重复注册、登录成功、错误密码，且 Ping 链路回归通过。

### 迭代 01B：Unity 客户端账号接入

- `NetworkClient` 从只支持 Ping 扩展为通用 JSON 网络入口，新增 `SendJsonAsync(string json)` 和 `TextMessageReceived`。
- 新增 `AccountMessages`、`ClientSession`、`AccountClient` 和 `LoginPanel`。
- 登录成功后保存 token、playerId、nickname，并切换到 Lobby 占位状态。
- 用户记录 Unity Play Mode 端到端手动测试通过：注册、重复注册错误、正确登录、错误密码、Session 写入、Lobby 占位切换和旧 Ping 面板回归。

### 迭代 02A：服务端大厅 / 房间状态容器

- 新增 `RoomModels`、`RoomService` 和 `RoomMessages`。
- 房间状态由服务端内存字典维护，`RoomService` 是唯一权威来源。
- 支持进入大厅、创建房间、加入房间、离开房间、房主转移和房间销毁。
- 新增 `ClientConnection` 与 `ConnectionRegistry`，把登录后的 playerId 绑定到 WebSocket 连接。
- 引入 `RoomStateNtf`，在房间成员变化后向相关在线成员广播服务端权威快照。
- 用户记录 `Test-ServerRoom.ps1` 通过，覆盖未登录、三账号注册登录、创建、查询、加入不存在房间、加入满员、非成员离开、房主转移、最后成员离开销毁，并校验 `notificationCount = 4`。

### 迭代 02B：Unity 客户端 Lobby / Room 接入

状态：已启动，尚未完成。

当前只记录计划边界：

- Unity 客户端需要接入 `EnterLobbyReq / CreateRoomReq / JoinRoomReq / LeaveRoomReq`。
- 客户端需要区分带 `requestId` 的 response 和无 `requestId` 的 `RoomStateNtf`。
- 至少需要双客户端 Play Mode 或多实例手动测试，证明一个玩家加入 / 离开后另一个玩家的房间成员显示会刷新。

## 实践记录

| 迭代 | 内容 | 状态 |
|---|---|---|
| 00 / 00B | [项目骨架、WebSocket Ping / Pong 与 Unity 调试面板](communication-and-debug-panel.md) | 用户记录服务端 smoke test 与 Unity Play Mode Ping 验证通过；本次整理未复测 |
| 01 / 01B | [账号注册 / 登录闭环](account-login-loop.md) | 用户记录服务端账号 smoke test 与 Unity Play Mode 账号接入通过；本次整理未复测 |
| 02 | [大厅 / 房间闭环](lobby-room-loop.md) | 02A 服务端房间容器与广播已由用户记录通过；02B Unity Lobby 接入尚未完成 |
| 项目评估 | [项目含金量分析](project-value-analysis.md) | 当前为中高潜力联网项目证据，完成战斗同步前不能包装成完整联机动作 RPG |

## 当前架构快照

```text
Unity UI / Debug Panel / Login Panel / Lobby Panel
        |
AccountClient / LobbyClient / NetworkClient
        |
INetworkTransport
        |
WebSocketTransport
        |
JSON ProtocolEnvelope over ws://localhost:5050/ws
        |
.NET Program.cs WebSocket Gateway
        |
AccountService / RoomService / ConnectionRegistry
```

当前最重要的分层边界：

- UI 只表达用户操作，不直接操作 `ClientWebSocket`。
- `NetworkClient` 提供通用收发和消息分发入口。
- `AccountService` 负责账号、token 和会话，不关心房间。
- `RoomService` 负责服务端权威房间状态，不关心 JSON 和 WebSocket。
- `ConnectionRegistry` 负责玩家身份与在线连接之间的映射，支撑广播。

## 当前验证证据

- 用户记录服务端 `dotnet build Server/OnlineRpgServer/OnlineRpgServer.csproj` 多次通过，0 warning / 0 error。
- 用户记录 `Test-ServerPing.ps1`、`Test-ServerAccount.ps1`、`Test-ServerRoom.ps1` 均通过。
- 用户记录 Unity Play Mode 已完成网络调试面板 Ping、账号注册 / 登录和 Lobby 占位跳转的手动端到端测试。
- 本知识库环境本次未启动外部 Online RPG 项目、Unity Editor 或 .NET 服务端，因此上述运行结果记录为用户实践证据，不升级为当前模型亲自验证。

## 当前不能对外夸大的内容

- 不能写成已完成 UDP / KCP 或战斗同步。
- 不能写成已完成商业级账号安全体系；当前账号数据仍是内存态，密码处理是 MVP 简化。
- 不能写成已完成数据库持久化、匹配系统、Ready / StartBattle 或战斗加载。
- 不能写成 Unity Lobby / Room UI 已完成；02B 当前只是启动记录。

## 下一步

1. 完成 02B Unity Lobby / Room 接入：`RoomMessages`、`LobbyClient`、`LobbyPanel`、房间列表与成员面板。
2. 做双客户端手动验证，并保留截图 / 录屏 / 服务端日志。
3. 增加 Ready / StartBattle 最小协议，让房间能进入战斗场景加载前置状态。
4. 开始战斗同步 MVP：服务端 Tick、角色生成、位置 / 朝向快照、客户端插值缓冲。
5. 补弱网和工程证据：断线、重连、请求超时、重复登录、房间广播丢失和日志面板。

## 面试表达边界

当前可表达为：

> 在 Online Action RPG Demo 中搭建 Unity 客户端与 .NET 服务端的 WebSocket + JSON 通信链路，完成 Ping / Pong 调试面板、账号注册 / 登录、token 会话，以及服务端大厅 / 房间权威状态容器和 `RoomStateNtf` 广播验证。当前正在接入 Unity Lobby / Room UI，后续进入战斗同步。

更强的表达需要等 02B 与战斗同步完成后再升级。

