# 网络编程

> 游戏网络架构基础 — TCP/UDP · Netcode · 同步模型 · 实战

---

## 学习定位

> 路线：专项能力，项目需求驱动
> 前置：C# 基础、Unity 生命周期与基础异步概念
> 路线入口：[专项能力路线](../roadmap/specializations.md)
> 掌握检查：[专项能力清单](../checklists/specializations.md)

学习时优先画消息流和状态流，再补实现细节；没有完成联机或消息实验的主题保持“待实践”。

---

## 为什么需要理解网络编程

多人游戏（联机）是游戏行业的主流趋势。即使是客户端开发，也需要理解：

- 客户端和服务端如何同步状态
- 延迟、丢包对游戏体验的影响
- 预测与插值、延迟补偿的实现原理

---

## 同步模型对比

| | 状态同步 (State Sync) | 帧同步 (Lockstep) |
|------|------|------|
| **原理** | 服务端下发状态，客户端插值 | 所有端执行相同帧输入 |
| **流量** | 大（序列化状态） | 小（只有输入指令） |
| **确定性** | 不需要 | 必须 Float Determinism |
| **回放** | 困难 | 天然支持（帧指令重放） |
| **代表** | FPS、MMO | RTS、MOBA、格斗 |
| **Unity方案** | Netcode for GameObject | 自行实现或第三方 |

---

## 计划主题

以下主题需要实际通信或同步实验后再创建正式文章。

## 已整理基础笔记

| 主题 | 证据边界 |
|---|---|
| [计算机网络基础概念](network-foundations.md) | 用户学习笔记；已整理网络/互联网、交换方式、性能指标和五层模型，尚未完成抓包或通信实验 |
| [IP 与路由基础](ip-routing-basics.md) | 用户学习笔记；已整理网络层服务、IPv4/CIDR、ARP、NAT、IPv6、RIP/OSPF/BGP，尚未完成抓包、路由配置或子网计算验证 |
| [TCP/UDP 基础](tcp-udp-basics.md) | 用户学习笔记与学习规划；已建立 TCP/UDP、HTTP/HTTPS、Socket 和游戏同步的面试学习范围，尚未完成抓包、Socket 或联机实验 |
| [应用层基础协议](application-layer-basics.md) | 用户学习笔记与截图；已整理 DNS、FTP、URL/HTTP/HTML 和常见应用层端口，尚未完成 DNS 查询或 HTTP 抓包 |

## 后续计划主题

| 主题 | 计划验证内容 |
|------|------|
| HTTP/HTTPS 基础 | 请求/响应结构、常见状态码、HTTPS 加密大意 |
| Socket 最小实验 | TCP 或 UDP 客户端/服务端收发 |
| Unity Netcode for GameObject | NetworkManager、RPC、NetworkVariable |
| 状态同步实战 | 插值、预测、延迟补偿 |
| 帧同步与锁步 | 确定性模拟、Checksum 校验、回放 |

---

## 最小闭环

```text
明确同步需求 → 画消息流 → 完成最小通信 → 模拟延迟/断线 → 记录取舍 → 回到项目
```
