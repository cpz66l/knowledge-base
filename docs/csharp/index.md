# C#

> C# 语言深度与 Unity 实践 — GC · 内存模型 · 异步编程 · 最佳实践

---

## 学习定位

> 路线：C# / Unity 主线
> 当前原则：先消化已学习内容，未学习主题保持规划状态
> 路线入口：[C# / Unity 主线](../roadmap/csharp-unity.md)
> 掌握检查：[C# 工程能力清单](../checklists/csharp-engineering.md)

推荐顺序：

```text
语言与 OOP
  ↓
集合、泛型、委托与事件
  ↓
GC 与运行时
  ↓
异步与工程实践
  ↓
Unity 项目应用与复盘
```

LeetCode 是持续练习支线，不替代 C# 工程能力学习。

---

## 目录

| 文章 | 内容 |
|------|------|
| [面向对象编程](oop/index.md) | 类型系统、值类型与引用类型、内存模型 |
| [LeetCode算法](leetcode/index.md) | 17 类题型：哈希、双指针、滑动窗口、二叉树、DP... |
| [GC 与内存管理](gc-and-memory.md) | Unity GC 机制、堆/栈分配、内存泄漏排查 |
| [async/await 异步](async-await.md) | 异步编程模型、Unity 协程对比、Task 最佳实践 |
| [Unity C# 最佳实践](unity-csharp-practices.md) | 性能优化、空安全、异常处理、编码规范 |

---

## 当前状态

| 模块 | 状态说明 | 学习产出 |
|------|----------|----------|
| 面向对象与语言特性 | 已有笔记，继续通过项目校正理解 | 纯 C# 小模块 |
| LeetCode | 持续练习 | 思路、代码、复杂度与错题复盘 |
| GC 与内存 | 待按实际学习补充 | Profiler 或分配实验 |
| async/await | 待按实际学习补充 | 可取消的异步小实验 |
| Unity C# 工程实践 | 待按实际项目补充 | 模块化、测试或调试记录 |

完成一次真实练习后，将结果链接到[复盘中心](../reviews/index.md)，而不是只更新文章篇数。
