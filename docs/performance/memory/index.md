# 内存管理

> 堆分配 · GC 机制 · 对象池 — 把内存控制在自己手里

---

## 目录

| 文章 | 内容 |
|------|------|
| [对象池](object-pool.md) | UnityEngine.Pool、GameObject 池化、预加热策略、实战练习 |
| [C# GC 与内存管理](../../csharp/gc-and-memory.md) | 托管分配、Unity GC、Profiler 验证与后续实验路线 |

## 项目应用

- [Backpack Survivor：刷怪器与对象池](../../projects/backpack-survivor/spawner-and-object-pooling.md)：敌人和投射物的预热、弹性扩容、状态重置与归还闭环。当前有外部代码/场景检查记录，但仍缺 Profiler 前后数据。

---

> 💡 对象池是内存优化的第一道防线 — 先控制分配量，再谈 GC 调优。
