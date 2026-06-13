# 网络编程

> 游戏网络架构基础 — TCP/UDP · Netcode · 同步模型 · 实战

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

## 目录

| 文章 | 内容 |
|------|------|
| [TCP/UDP 基础](tcp-udp-basics.md) | 协议选择、分包、粘包、可靠传输 |
| [Unity Netcode for GameObject](unity-netcode.md) | NetworkManager、RPC、NetworkVariable |
| [状态同步实战](state-sync.md) | 插值、预测、延迟补偿 |
| [帧同步与锁步](lockstep.md) | 确定性模拟、Checksum校验、回放 |
