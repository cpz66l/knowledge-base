# 大厅 / 房间闭环

> 所属项目：[Online Action RPG Demo](index.md)
>
> 覆盖迭代：02
>
> 学习状态：02A 项目中使用；02B 进行中
>
> 证据归属：用户项目实践与运行记录；本次整理未重新运行 Unity、服务端或 smoke test
>
> 下一步：完成 Unity Lobby / Room UI 接入和双客户端验证

## 学习目标

- 在账号登录之后，让多个已登录玩家进入同一个服务端权威状态容器。
- 支持进入大厅、创建房间、加入房间、离开房间、房主转移和房间销毁。
- 区分单次操作的请求 / 响应和多人共享状态变化的服务端通知。

## 迭代边界

迭代 02 只处理大厅 / 房间，不处理战斗。

已纳入：

- token 鉴权。
- 房间列表查询。
- 创建 / 加入 / 离开房间。
- 服务端房间权威状态。
- `RoomStateNtf` 广播房间成员变化。

暂不纳入：

- Ready / StartBattle。
- 异步战斗场景加载。
- 角色移动、输入同步、技能、伤害、血量和结算。
- UDP / KCP 改造。

## 服务端完成内容（02A）

- 新增 `RoomModels`，区分内部可变状态和对外快照。
- 新增 `RoomService`，维护 `_roomsById` 和 `_roomIdByPlayerId`。
- 新增 `RoomMessages`，定义大厅 / 房间协议 DTO。
- `Program.cs` 接入 `EnterLobbyReq / CreateRoomReq / JoinRoomReq / LeaveRoomReq`。
- 房间请求统一先通过 `AccountService.GetSession(token)` 校验登录态。
- 新增 `ClientConnection` 和 `ConnectionRegistry`，维护 `connectionId -> connection` 与 `playerId -> connectionId`。
- 状态变更请求返回 `MessageDispatchResult`，外层连接循环先回复请求者，再向房间成员广播 `RoomStateNtf`。
- 新增并升级 `Tools/SmokeTests/Test-ServerRoom.ps1`，显式校验广播通知数量。

## 核心运行链路

```text
客户端 WebSocket 连接 /ws
  -> 服务端生成 connectionId
  -> ConnectionRegistry 记录连接
  -> 客户端 Register / Login
  -> Login 成功后绑定 playerId -> connectionId
  -> 客户端携带 token 发送大厅 / 房间请求
  -> AccountService.GetSession(token) 校验登录态
  -> RoomService 修改或读取服务端权威房间状态
  -> 服务端先返回 XxxRes 给请求者
  -> 状态变化时向房间在线成员广播 RoomStateNtf
```

## 关键设计思想

### 服务端权威状态

房间状态不能由各客户端分别自算。否则 A 客户端可能认为 B 已加入，B 客户端却认为自己还在大厅。02A 让 `RoomService` 成为唯一权威来源，客户端后续只展示服务端 response 和 notification 给出的结果。

这也是后续动作 RPG 战斗同步的基础：客户端可以负责输入、表现和插值，但多人共享世界状态需要逐步收敛到服务端权威。

### 请求 / 响应与通知分层

`CreateRoomRes / JoinRoomRes / LeaveRoomRes` 用来回答“我刚才点的按钮成功了吗”。

`RoomStateNtf` 用来回答“这个房间现在真实状态是什么”。如果只有请求响应，B 加入房间时 B 知道成功了，但 A 不会自动知道 B 已加入。

客户端 02B 必须把两类消息分开处理：

```text
Response: 带 requestId，用于匹配某次按钮操作
Notification: 通常不依赖 requestId，用于刷新共享状态
```

### Snapshot 不暴露内部对象

`RoomRecord` 是服务端内部可变对象，`RoomSnapshot` 是对外只读结果。业务层修改内部状态，网络层只拿快照转换 DTO 和序列化，避免外部模块误改房间内部字典。

### 玩家身份和连接状态分离

`AccountService` 负责 token 对应哪个玩家；`ConnectionRegistry` 负责这个玩家当前是否有在线 WebSocket 连接。两者分离后，账号模块不需要知道网络连接细节，房间模块也不需要直接保存 WebSocket。

## 验证记录

用户原始记录中保留的自动化验证：

```powershell
dotnet build Server\OnlineRpgServer\OnlineRpgServer.csproj
powershell.exe -NoProfile -ExecutionPolicy Bypass -File Tools\SmokeTests\Test-ServerRoom.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File Tools\SmokeTests\Test-ServerPing.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File Tools\SmokeTests\Test-ServerAccount.ps1
```

`Test-ServerRoom.ps1` 覆盖：

- 未登录进入大厅返回 `ErrorRes / 1002`。
- 三个测试玩家注册、登录成功。
- 玩家 A 创建房间并成为房主。
- 大厅列表可以查询到新房间。
- 玩家 C 加入不存在房间返回 `ErrorRes / 3001`。
- 玩家 B 加入房间成功，成员数变为 2。
- 房间满员后玩家 C 加入失败，返回 `ErrorRes / 3002`。
- 非成员离开房间失败，返回 `ErrorRes / 3003`。
- 房主 A 离开后，房主转移给 B。
- 最后玩家 B 离开后，房间销毁。
- 脚本显式校验 `RoomStateNtf` 数量为 4，证明广播链路已生效。

本次整理未重新运行这些命令，也未启动 Unity Editor。

## 02B 启动状态

Unity 客户端 Lobby / Room 接入尚未完成。下一步应补：

- `Lobby/RoomMessages.cs`：客户端大厅 / 房间协议 DTO。
- `LobbyClient.cs`：封装 EnterLobby / CreateRoom / JoinRoom / LeaveRoom 请求，解析 response 和 `RoomStateNtf`。
- `LobbyPanel.cs`：显示房间列表、当前房间成员、房间名输入、最大人数输入、创建 / 加入 / 离开按钮。
- 双客户端 Play Mode 或多实例测试：A 创建房间、B 加入 / 离开，A 的成员显示能刷新。

## 面试表达

可以说：

> 在 Online Action RPG Demo 中实现服务端大厅 / 房间状态容器，基于 WebSocket 长连接和 JSON 协议完成登录态鉴权、房间创建 / 加入 / 离开、房主转移、房间销毁，并通过 `RoomStateNtf` 向房间成员广播服务端权威快照；配套 smoke test 验证多人房间状态流转和历史 Ping / Account 链路回归。

当前不要说：

- 已完成完整大厅 UI。
- 已完成匹配系统。
- 已完成 Ready / StartBattle。
- 已完成联机战斗同步。

