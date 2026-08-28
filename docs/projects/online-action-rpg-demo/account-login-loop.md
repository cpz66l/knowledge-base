# 账号注册 / 登录闭环

> 所属项目：[Online Action RPG Demo](index.md)
>
> 覆盖迭代：01 / 01B
>
> 学习状态：项目中使用
>
> 证据归属：用户项目实践与运行记录；本次整理未重新运行 Unity、服务端或 smoke test
>
> 下一步：登录后进入 Lobby / Room 真实状态容器

## 学习目标

- 在已验证的网络通信层之上实现第一条真实业务链路。
- 让客户端能注册、登录、处理错误码，并保存本次会话 token。
- 保持 UI、账号业务层、网络层和传输层分离，避免按钮脚本直接操作 WebSocket。

## 协议范围

| msgId | type | 方向 | 说明 |
|---:|---|---|---|
| 1001 | `RegisterReq` | Client -> Server | 注册账号 |
| 1002 | `RegisterRes` | Server -> Client | 注册成功响应 |
| 1003 | `LoginReq` | Client -> Server | 登录账号 |
| 1004 | `LoginRes` | Server -> Client | 登录成功响应 |
| 9999 | `ErrorRes` | Server -> Client | 通用错误响应 |

本阶段保留的错误码：

| code | 场景 | 客户端显示建议 |
|---:|---|---|
| 1001 | 参数错误 | 输入信息不完整或格式错误 |
| 2001 | 账号已存在 | 该账号已注册，请直接登录 |
| 2002 | 账号或密码错误 | 账号或密码错误 |

## 服务端实现

- 新增 `AccountModels.cs`，记录账号与会话模型。
- 新增 `AccountService.cs`，维护 `username -> AccountRecord` 和 `token -> PlayerSession`。
- 新增 `AccountMessages.cs`，定义注册 / 登录请求与响应 payload。
- `Program.cs` 接入 `RegisterReq / LoginReq` 协议分发。
- 新增 `Tools/SmokeTests/Test-ServerAccount.ps1`。

第一版账号数据保存在服务端内存字典中。这个选择适合本地客户端 Demo 验证，但不是正式账号系统。正式项目还需要密码哈希、加盐、持久化、限流、日志审计和更完整的安全策略。

## Unity 客户端实现

- `NetworkClient` 扩展为通用 JSON 网络入口，新增 `SendJsonAsync(string json)` 和 `TextMessageReceived`。
- `AccountMessages.cs` 对齐服务端账号协议结构。
- `ClientSession.cs` 保存 `token / playerId / nickname`。
- `AccountClient.cs` 负责构造注册 / 登录请求、按 `requestId` 匹配响应、处理 `ErrorRes`，并在登录成功后写入 `ClientSession`。
- `LoginPanel.cs` 读取用户名、密码、昵称输入，显示注册 / 登录结果，并在成功后切换到 Lobby 占位状态。

客户端调用链保持：

```text
LoginPanel
  -> AccountClient
  -> NetworkClient
  -> INetworkTransport
  -> WebSocketTransport
```

## 关键设计取舍

### 内存账号优先于数据库

当前项目的核心目标是验证客户端登录链路和协议错误反馈。数据库会显著增加后端工作量，但对当前客户端展示价值提升有限，因此第一版先用内存账号。

### Token 先只保存在内存会话

`ClientSession` 只保存本次 Play Mode / 运行期间的 token、playerId 和 nickname。退出后重新登录是可接受的 MVP 限制。写磁盘会引入过期、清理和安全表达问题，暂不提前展开。

### 账号不存在和密码错误统一返回

错误密码和账号不存在统一返回 `code = 2002`，避免通过错误提示泄露账号是否存在。虽然当前是本地 Demo，但这个取舍能体现安全边界意识。

## 验证记录

用户原始记录中保留的验证：

- 服务端 `dotnet build Server/OnlineRpgServer/OnlineRpgServer.csproj` 通过，0 warning / 0 error。
- `Test-ServerAccount.ps1` 通过，覆盖注册成功、重复注册、登录成功和错误密码。
- `Test-ServerPing.ps1` 仍然通过，说明账号协议接入没有破坏 Ping 链路。
- Unity 脚本编译通过，Editor 日志出现 `Tundra build success`。
- 用户在 Unity Play Mode 中完成端到端手动测试：连接服务端、注册新账号、重复注册错误提示、正确登录、错误密码提示、登录成功写入 `ClientSession`、切换到 Lobby 占位面板。

本次整理未重新运行这些命令，也未启动 Unity Editor。

## 当前边界

已完成：

- 服务端注册 / 登录协议。
- Unity 客户端账号业务入口。
- 登录成功后的本地会话保存和 Lobby 占位跳转。
- smoke test 与 Play Mode 手动验收记录。

未完成：

- 数据库持久化账号系统。
- 商业级账号安全体系。
- 第三方登录。
- 真实 Lobby / Room UI 和战斗同步。

## 面试表达

可以说：

> 在 Online Action RPG Demo 中实现账号注册 / 登录链路，基于 WebSocket + JSON 协议接入自研 .NET 服务端，封装 `AccountClient`、`ClientSession` 和错误反馈流程，并通过 `requestId` 完成请求响应匹配。该链路有服务端 smoke test 和 Unity Play Mode 手动验收记录。

不要说：

- 已完成完整账号安全系统。
- 已完成数据库持久化账号体系。
- 已完成大厅房间或联机战斗。

