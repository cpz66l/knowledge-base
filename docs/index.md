# 🎮 GameDev 知识库

> Unity 客户端开发学习笔记 —— C# · C++ · Unity · 图形学 · 性能优化 · 网络编程 · 热更新

---

## 当前重点

根据最近一次复盘，当前只保留三个明确重点：

- 每天使用 C# 与 C++ 各完成一遍 LeetCode，并整理到[双语题解](csharp/leetcode/index.md)。
- 继续补齐 C++ 基础语法、指针、引用和常用 STL。
- 继续推进 Backpack Survivor V0.1：接入主动武器，并修复敌人复用与自动索敌的生命周期边界。

!!! important "当前原则"
    尚未学习的内容只保留路线与待办，不提前写成完整结论。已有文章全部保留，后续通过练习、项目和复盘逐步补充自己的理解。

---

## 使用入口

- **决定下一步**：进入[学习路线总览](roadmap/index.md)。
- **查询具体知识**：使用左侧专题导航或右上角搜索。
- **判断是否掌握**：进入[学习检查清单](checklists/index.md)。
- **整理学习结果**：进入[复盘中心](reviews/index.md)。

---

## 学习闭环

```text
路线规划 → 学习文章 → 最小练习 → 项目应用 → 工具验证 → 复盘回写
```

| 当前入口 | 用途 |
|----------|------|
| [C# / Unity 主线](roadmap/csharp-unity.md) | 当前主要学习方向 |
| [C++ 底层副线](roadmap/cpp.md) | 面试、底层与引擎开发基础 |
| [计算机基础路线](roadmap/computer-science.md) | 算法、组成原理、操作系统、网络与图形数学规划 |
| [专项能力路线](roadmap/specializations.md) | 性能、图形、网络、热更新 |
| [项目实践路线](roadmap/projects.md) | 把知识应用到可运行项目 |
| [学习检查清单](checklists/index.md) | 判断是否真正掌握 |
| [复盘中心](reviews/index.md) | 沉淀问题、验证与下一步 |

---

## 最近沉淀

- [Backpack Survivor：目标注册表、自动武器与投射物](projects/backpack-survivor/target-registry-and-auto-weapon.md)
- [Backpack Survivor：敌人追击、近战与死亡流程](projects/backpack-survivor/enemy-ai-and-melee.md)
- [Unity 生命周期：初始化、启用与禁用](unity/lifecycle.md)
- [Backpack Survivor：伤害管线与危险区](projects/backpack-survivor/damage-pipeline-and-hazard-zone.md)

---

## 关于这个知识库

这是一个面向 Unity 客户端开发的个人知识库，目标是保存经过理解、练习或验证的**消化输出**。

- 附上关键代码片段，理论与实现结合
- 持续更新，commit 历史就是我的学习轨迹
- 以路线、练习、项目、验证和复盘形成学习闭环

> 如果发现错误或想交流，欢迎提 [Issue](https://github.com/CPZ66L/knowledge-base/issues) 或在 [Discussions](https://github.com/CPZ66L/knowledge-base/discussions) 讨论。
