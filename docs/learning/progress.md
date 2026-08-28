# 学习进度

> 当前日期：2026-08-29
> 当前阶段：大三上前准备期，目标是把《游戏客户端学习路线总纲要》落到每周计划和证据记录中。  
> 总纲入口：[游戏客户端学习路线总纲要](../roadmap/game-client-learning-roadmap.md)  
> 本周记录入口：[2026-W35](weekly/2026-W35.md)

---

## 进度文档怎么维护

这份文档是“当前能力快照”，不是单次计划本身。

- 每次生成计划前，先根据本页确认当前短板和优先级。
- 平时把题解、代码、笔记、项目讲稿、投递记录等原始证据放进 `inbox/`。
- 用户要求整理时，将本次材料追加到对应周学习记录，再按证据更新本页状态和下一步重点。
- 没有证据的新内容保持“待验证”或“待补证据”，不为了进度好看提前标记掌握。

## 当前基础进度总览

| 方向 | 当前状态 | 证据来源 | 当前判断 | 下一步 |
|---|---|---|---|---|
| Unity / C# 项目能力 | 项目中使用 | Backpack Survivor V0.3.11、项目页、检查清单、正式包用户验收记录、2026-W33 第 3 批面试复盘、第 5 批 V0.3 项目复盘、2026-W34 第 1-2 批项目复盘和 V0.3 阶段复盘；Online Action RPG Demo 00-02A 开发记录与 2026-W35 第 2 批整理 | 当前最强项仍是 Backpack Survivor 的完整单机交付；Online Action RPG Demo 开始补联网客户端专项证据，已覆盖通信、账号和服务端房间状态容器，但尚未完成 Unity Lobby 双客户端验证和战斗同步 | W35 剩余时间优先完成 Online Action RPG Demo 02B 双客户端 Lobby 验证，同时保留 Backpack Survivor V0.3 的 1 分钟表达稿 |
| C# 工程能力 | 学习中 / 项目中使用 | `interface`、事件、纯 C# 背包、对象池、asmdef、UGUI 投影、Build 记录；Online Action RPG Demo 中 `NetworkClient`、`AccountClient`、`ClientSession`、`LoginPanel` 和后续 `LobbyClient` 分层记录 | 有真实项目证据，并开始出现网络业务分层、异步回调、UI 状态快照和请求响应匹配；系统化 GC、异步、日志、异常策略仍待补 | 用 Online Action RPG Demo 补网络客户端分层、断线 / 超时 / 日志策略；用 Backpack Survivor 继续补 GC / Profiler 证据 |
| 算法 / LeetCode | 学习中 | 当前记录 37 道题，其中 5 道 C# / C++ 双语对照；2026-W35 新增 LC 35、LC 74、LC 34 三道 C++ 二分练习 | W35 已开始离开二叉树 / BST 舒适区，新增二分、二维映射和左右边界题；仍需要保持日刷、错题复盘，并继续补栈 / 堆 / 回溯覆盖 | 后续刷题优先用 C++，每题保留复杂度、错点和提交证据；W35 剩余题目优先补栈 / 堆 / 回溯入口 |
| C++ | 学习中 | C++ 基础语法 / STL / OOP / 内存笔记、部分 LeetCode；新增指针/引用、类与对象、栈 / 堆、继承 / 多态、虚析构、浅拷贝风险、`enum class`、结构化绑定、`map`、智能指针概念、BST 上下界 / 中序模板、二分模板、lambda、`std::sort` 比较器、`std::function`、函数模板、类模板、非类型模板参数和多道 C++ LeetCode 练习 | 能起步刷题，已接触 `vector`、`string`、`unordered_map`、`map`、`stack`、`queue`、`sort`、lambda、`std::function`、模板、递归上下界、二分边界、指针、引用、`nullptr`、初始化列表、`new/delete`、继承、虚函数和智能指针概念；但生命周期、浅拷贝、RAII、严格弱序、模板约束和可复核编译运行证据仍是短板 | W35 继续补 1 个带编译命令和输出的小程序，优先智能指针、浅拷贝风险、RAII 或模板异常边界；模板练习已有用户运行输出但仍需源文件路径 / 编译命令 |
| 计算机网络 | 学习中 / 项目中使用 | 简历写“了解 TCP/UDP”；2026-W33 新增网络基础、网络层 / IP / 路由、TCP/UDP 和应用层协议笔记；2026-W35 新增 Online Action RPG Demo 的 WebSocket + JSON、Ping / Pong、账号、token、大厅 / 房间和 `RoomStateNtf` 项目证据 | 已从纯笔记推进到项目实践：能围绕 WebSocket、协议日志、请求响应、服务端通知和房间权威状态讲项目链路；但 TCP/UDP 高频面试、弱网、重连、抓包、UDP / KCP 和战斗同步仍待补 | W35 先完成 02B Unity Lobby 双客户端验证；基础学习继续补 DNS / HTTP / TCP 高频问答和最小命令证据 |
| 操作系统 | 待系统学习 / 简历层了解 | 简历写“了解进程/线程/内存”；知识库 OS 内容仍未系统沉淀 | 当前缺少实验和题库证据 | 先补进程、线程、同步、虚拟内存和死锁基础 |
| 图形学 / Shader | 准备启动 / 待实验 | 简历写“了解图形渲染管线”；用户希望为作品集补 Shader 编写能力；`docs/graphics/shader-basics.md` 已建立最小实验计划 | 可作为作品集加分项预热，但尚无可复核渲染实验，不能写成掌握或已能实现复杂 Shader | 本周只从缓冲中抽 1-2h 做一个最小 Shader 实验准备；不挤占 C++、算法和项目表达 |
| Lua / 热更新 | 未开始 | 热更新目录为规划入口 | 当前不应写成会用 | 大三下再补 Lua 基础和热更新流程 |
| 性能优化 | 学习中 / 项目中使用 | 对象池、NonAlloc、sqrMagnitude、Profiler 快扫、Build 颜色修复、`PickUpMagnet` 背包被动重复汇总挂账、V0.3.7 敌群低频错峰移动和 V0.3 Release 前暂不大重构决策 | 有项目经验和取舍记录，但缺系统化前后数据；已能记录“暂不优化”和“先发布后挂账”的触发条件 | 准备一段面试表达：Profiler 如何判断“不重构”；后续用 V0.3 掉落量级和敌群规模验证 `PickUpMagnet` / `EnemyMovement` 是否需要共享缓存或更强空间查询 |
| 面试表达 | 准备中 | 简历、项目复盘、路线总纲、[Backpack Survivor 面试复盘第 01 阶段](../reviews/2026/backpack-survivor-interview-stage-01.md)、[Backpack Survivor V0.3 阶段复盘](../reviews/2026/backpack-survivor-v0.3-review.md)、[2026-W34 复盘](../reviews/2026/2026-W34.md)、[Online Action RPG Demo 项目含金量分析](../projects/online-action-rpg-demo/project-value-analysis.md) | 项目素材足，Backpack Survivor 适合作为完整单机项目主线；Online Action RPG Demo 适合作为联网专项潜力项目，但完成战斗同步前只能表达为通信 / 账号 / 房间状态容器，不能包装成完整联机动作 RPG | W35 同时压缩 Backpack Survivor V0.3 1 分钟稿，并给 Online Action RPG Demo 准备“当前已完成 / 尚未完成 / 下一步”的诚实表述 |
| 求职材料 | 准备中 | 简历 PDF、项目复盘、路线总纲 | 已有基础简历和项目事实，但存在 Git 提交数差异 | 投递前统一“46 次 / 49 次提交”等数据口径 |

## 当前已掌握或接近掌握的基础

### Unity / C# 项目实践

状态：项目中使用。

已具备的基础：

- 能独立推进 Unity 小型项目，从功能设计、编码实现、调试验证到 Windows Build 交付。
- 能使用 C# 接口、事件、泛型集合、委托和组件化方式拆分玩法系统。
- 能用纯 C# 数据层承载核心规则，并让 Unity UI 做投影而不是复制规则。
- 能围绕对象池、NonAlloc 查询、Profiler 快扫和 Build 验收做性能与交付取舍。
- 能把 Bug 复盘成“现象、排查、根因、修复、沉淀规则”的面试材料。

证据：

- [Backpack Survivor 项目总览](../projects/backpack-survivor/index.md)
- [C# 工程能力检查清单](../checklists/csharp-engineering.md)
- [Unity 项目能力检查清单](../checklists/unity-project.md)
- [Bug 记录簿](../projects/backpack-survivor/bug-log.md)
- [性能优化记录](../projects/backpack-survivor/performance-optimization-log.md)

仍待补强：

- 系统化 Profiler 前后对照数据。
- 目标平台性能预算。
- 更完整的 Play Mode / EditMode 测试证据。
- 资产、Prefab、Canvas、Input Actions、Layer 的成体系验收清单。

### C# 语言与工程基础

状态：学习中 / 项目中使用。

已具备的基础：

- 能在真实项目中使用 `interface`、事件发布订阅、泛型集合和分层职责。
- 能理解 class 实例身份在背包物品、合并、邻接和武器映射中的作用。
- 能识别静态状态、事件订阅、对象池状态残留带来的生命周期风险。

仍待补强：

- 值类型 / 引用类型的系统化表达。
- GC 分配、装箱、闭包、字符串和集合扩容成本。
- 异步、Coroutine、Task、线程和 Unity 主线程边界。
- 日志、异常、失败流程和可测试性策略。

### 算法基础

状态：学习中。

已有基础：

- 知识库已记录 37 道 LeetCode 题，其中 5 道形成 C# / C++ 双语对照；2026-W35 新增 LC 35、LC 74、LC 34 三道 C++ 二分练习题。
- 已有题型覆盖哈希、双指针、滑动窗口、子串、数组、矩阵和链表的部分内容。

仍待补强：

- 每日稳定刷题节奏。
- 图、回溯、栈、堆、贪心、动态规划；二分已开始补 LC35、LC74 和 LC34，但 W35 仍要继续离开二叉树舒适区，不能只刷二分。
- 错题复盘和复杂度口头表达。
- C++ 手写熟练度，尤其是随机指针、链表拆分、归并、二叉树镜像递归、树高全局答案和空指针边界。

### C++ 基础

状态：学习中。

已有基础：

- 已能进入基础语法和部分 LeetCode 练习。
- 已明确 C++ 是游戏客户端笔试、面试和未来底层能力的副线。
- 已开始用 C++ 作为算法刷题主语言；C# 训练重点转回 Unity / 项目工程实践。
- 已整理运算符、控制流、函数、结构体、`enum class`、结构化绑定、`vector`、`string`、`map`、`stack`、`sort`、lambda、`std::function`、函数模板、类模板、非类型模板参数、指针、引用、`nullptr`、`const` 指针组合、类与对象、初始化列表、`this`、继承、多态、虚析构、抽象类、栈 / 堆、`new/delete`、浅拷贝风险、智能指针概念、BST 验证边界和二分边界的入门笔记。

仍待补强：

- 指针、引用、对象生命周期、构造 / 析构、虚函数派发、浅拷贝风险、智能指针和模板约束的编译运行验证。
- `vector`、`string`、`unordered_map`、`map`、`set`、`queue`、`stack`、`priority_queue`、`sort` 比较器严格弱序。
- RAII、智能指针、拷贝 / 移动、虚函数和对象模型。
- 多文件工程、编译、链接、CMake 和调试。

### 计算机网络基础

状态：学习中 / 项目中使用。

已有基础：

- 已整理网络、互联网、边缘部分、核心部分、主机和路由器的基本概念。
- 已学习电路交换、报文交换、分组交换的基本差异。
- 已记录速率、带宽、吞吐量、发送时延、传播时延、RTT 等性能指标。
- 已用“异地朋友聊天”类比梳理五层模型和封装 / 解封装流程。
- 已整理网络层数据报服务、IPv4/CIDR、ARP、NAT、IPv6、RIP/OSPF/BGP 和 TCP/UDP 对比的学习笔记。
- 已整理 DNS、FTP、URL、HTTP、HTML 和常见应用层协议端口的学习笔记。
- 已通过 Online Action RPG Demo 记录 WebSocket + JSON、Ping / Pong、Unity 网络调试面板、账号注册 / 登录、token 会话、服务端大厅 / 房间权威状态和 `RoomStateNtf` 广播的项目实践证据。

仍待补强：

- TCP / UDP 高频面试题，尤其是三次握手、四次挥手、TIME_WAIT、可靠传输、粘包 / 拆包和游戏客户端 UDP 场景。
- HTTP / HTTPS、DNS 解析流程、WebSocket 等应用层高频题。
- 子网划分计算、ARP / 路由观察、抓包、`ping`、流程图或最小通信实验等强证据。
- Socket / WebSocket 最小收发实验已在项目中开始落地，但仍需要抓包、弱网、断线、重连、状态同步 / 帧同步对比图和战斗同步证据。

### 面试表达

状态：准备中。

已有基础：

- 已整理 Backpack Survivor 前 5 轮模拟面试复盘，覆盖项目总览、背包分层、拾取入包链路、BUG-001 物品蒸发和 `EndDrag` 兜底设计。
- 已形成几张可背表达卡：背包不是硬套 MVC，而是纯数据 Model + UI 投影 + Gameplay Adapter；拾取采用请求-确认；BUG-001 根因是旧格子仍为空的脆弱假设被自动入包破坏。
- 已新增 V0.3 项目复盘证据：升级候选池、邻接效果架构、背包被动 / 邻接构筑收益分层、内容池价值平衡、基础音频系统、设置菜单、敌群移动优化、远程敌人与波次混编、本地存档、V0.3 Release 和 `PickUpMagnet` / `EnemyMovement` 性能挂账。
- 已新增 Online Action RPG Demo 早期项目表达：通信调试、账号登录、服务端房间状态容器和项目含金量边界。

仍待补强：

- 把 Backpack Survivor 和 Online Action RPG Demo 分别口述成 1 分钟 / 3 分钟版本，避免两个项目的定位混在一起。
- 继续训练对象池、`TargetRegistry`、`AdjacencyRuleBook / Resolver`、`LevelUpOptionGenerator`、`BackpackEffectCollector`、`BackpackPassiveCollector`、`WaveDirector` 和 Profiler 快扫追问。
- 每个回答都要带上类名、调用链、版本边界和验证方式。

### 图形学 / Shader 基础

状态：准备启动 / 待实验。

当前定位：Shader 编写适合作为作品集和简历加分项，但当前阶段只能做小规模预热，不能抢占 P0 的算法、C++ 和项目表达时间。

本轮目标：先完成 1 个 Unity 可观察小效果，例如 UV 流动 / 流光、受击闪白、简单溶解或 Unlit 颜色控制。

需要补的证据：

- Shader 源码或 Shader Graph 关键节点截图。
- Unity 场景截图或 5-15 秒录屏。
- 效果目标、关键参数、挂载对象、验证方式和仍不理解的问题。
- 若接入 Backpack Survivor，需要记录使用场景、运行观察和可能的性能 / 材质实例化风险。

简历门槛：完成 1 个可复现实验前，只能写“正在学习 Shader 基础”或保留“了解图形渲染管线基础”；完成实验后，再考虑写“了解 Shader 基础，能在 Unity 中实现简单材质效果”。

## 当前短板排序

| 优先级 | 短板 | 为什么先补 |
|---|---|---|
| P0 | 算法日刷和错题复盘 | 直接影响笔试和一面，通过短期训练收益高 |
| P0 | C++ 基础和 STL 熟练度 | 游戏客户端岗位常见硬门槛，当前仍是明显短板 |
| P0 | 项目面试表达压缩 | Backpack Survivor 是完整单机王牌；Online Action RPG Demo 是联网潜力项目，两者都需要转成可讲故事线 |
| P1 | C# GC / 性能证据 | 已有对象池和 Profiler 快扫，但还缺更硬的数据表达 |
| P1 | OS / 计网高频基础 | 中大厂会问，当前只能写“了解” |
| P2 | 图形学 / Shader / Lua / 热更新 | 加分项；Shader 已准备启动最小实验，但仍不能抢 P0 时间 |

## 本周学习安排来源

根据当前基线、[2026-W34 复盘](../reviews/2026/2026-W34.md)和 [2026-W35 第 2 批整理](weekly/2026-W35.md)，W35 原计划是不急着开新项目，但本周实际启动了 Online Action RPG Demo。后续需要把这个新项目压成可验证小闭环，避免挤掉算法和 C++：

1. 算法恢复：本周已补 3 道 C++ 二分题，剩余优先补栈、堆或回溯；每题保留复杂度、边界和错点。
2. C++ 基础：lambda / `std::function` 和模板已有用户运行记录，下一步补 1 个带编译命令和输出的最小程序，优先智能指针、浅拷贝风险、RAII 或模板异常边界。
3. 项目表达：Backpack Survivor 继续压缩 1 分钟 V0.3 总览稿；Online Action RPG Demo 优先完成 02B Unity Lobby 双客户端验证，并保留截图 / 录屏 / 服务端日志。
4. 计网 / OS：网络已开始通过项目落地，仍要每天小步补 DNS / HTTP / TCP 高频问答；OS 先补进程 / 线程。
5. Shader：仍作为可选缓冲，P0 未完成时不推进简历表述。
6. 进度系统：用第一篇周学习记录验证“计划 -> 执行 -> 证据 -> 复盘 -> 更新进度”的闭环。

具体计划见：[2026-W35 周学习记录](weekly/2026-W35.md)。
