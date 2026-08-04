# GameDev 知识库

> 面向 Unity 游戏客户端开发实习的个人学习与项目复盘系统。
>
> 主线是 C# / Unity，副线是 C++、算法、计算机基础、图形学、性能、网络与热更新。

---

## 现在看什么

| 入口 | 适合场景 |
| --- | --- |
| [学习路线总览](roadmap/index.md) | 不确定下一步学什么，先看路线和阶段目标 |
| [Backpack Survivor 项目实践](projects/backpack-survivor/index.md) | 查看当前主推 Unity 项目的系统拆解、Bug 记录和复盘 |
| [LeetCode 双语题解](csharp/leetcode/index.md) | 用 C# / C++ 对照训练算法和面试表达 |
| [Unity 专题](unity/index.md) | 查生命周期、UGUI、资源、Prefab、ScriptableObject 等 Unity 基础 |
| [C# 专题](csharp/index.md) | 查面向对象、泛型、委托事件、GC、异步和工程实践 |
| [C++ 专题](cpp/index.md) | 补齐 C++ 基础、STL、内存管理和工具链 |
| [检查与复盘](checklists/index.md) | 判断是否真的掌握，并把学习结果回写成复盘 |

!!! important "维护原则"
    尚未学习或尚未验证的内容只保留路线、问题和待办，不提前写成“已掌握”的完整结论。知识库更看重真实练习、项目应用和复盘证据。

---

## 当前重点

截至 2026-08-04，当前只保留三条高优先级主线：

- **项目主线**：推进 Backpack Survivor Demo。当前已记录到旋转邻接方向修正，下一步进入武器稀有度与等级差异。
- **算法主线**：继续维护 C# / C++ 双语 LeetCode 题解，优先补链表、树、图、动态规划、堆和常见面试题型。
- **基础主线**：补 C++ 基础语法、指针引用、STL、操作系统、网络和图形学的面试可解释版本。

---

## 学习闭环

```text
路线规划
  -> 学习笔记
  -> 最小练习
  -> 项目应用
  -> 工具或运行验证
  -> Bug / Review / 周复盘
  -> 回写知识文章
```

一个知识点至少要经过“能解释、能实现、能验证、能复盘”中的三个环节，才从“看过”升级为“可用于面试表达”。

---

## 内容地图

| 模块 | 重点内容 | 当前作用 |
| --- | --- | --- |
| [C#](csharp/index.md) | OOP、泛型、委托事件、GC、异步、工程实践 | Unity 客户端主语言能力 |
| [C++](cpp/index.md) | 基础语法、STL、内存、Modern C++、工具链 | 面试和底层能力补齐 |
| [Unity](unity/index.md) | 生命周期、UGUI、Prefab、资源、动画、编辑器工具 | 客户端工程基础 |
| [项目实践](projects/index.md) | Backpack Survivor 系列开发日志 | 把知识转成可运行 Demo |
| [性能优化](performance/index.md) | Profiler、GC、对象池、渲染和 CPU 优化 | 项目稳定性和面试深度 |
| [图形学](graphics/index.md) | 渲染管线、Shader、光照、PBR、阴影 | 客户端长期竞争力 |
| [网络编程](networking/index.md) | TCP/UDP、状态同步、帧同步、锁步 | 游戏客户端专项储备 |
| [热更新](hotupdate/index.md) | Lua、xLua、资源热更和完整流程 | 商业项目常见能力储备 |
| [检查清单](checklists/index.md) | C#、Unity、专项、面试检查表 | 防止“看过但不会用” |
| [复盘中心](reviews/index.md) | 周复盘、项目复盘、文章模板 | 沉淀问题和下一步 |

---

## 最近沉淀

- [Backpack Survivor：旋转邻接方向修正](projects/backpack-survivor/rotation-adjacency-direction-fix.md)
- [Backpack Survivor：数值调参台与首轮平衡](projects/backpack-survivor/balance-tuning-and-first-playtest.md)
- [Backpack Survivor：合并升级收益兑现](projects/backpack-survivor/merge-upgrade-reward-payoff.md)
- [Backpack Survivor：背包价值与物品价值显示](projects/backpack-survivor/backpack-value-and-item-value-display.md)
- [Backpack Survivor：金币掉落与局内经济 HUD](projects/backpack-survivor/gold-drops-and-economy-hud.md)
- [Backpack Survivor：精英宝箱与终局压力强化](projects/backpack-survivor/elite-chests-endgame-pressure.md)
- [Backpack Survivor：构筑最小兑现](projects/backpack-survivor/build-payoff-dual-wield.md)
- [Backpack Survivor：胜负结算与重开闭环](projects/backpack-survivor/run-result-and-restart-loop.md)
- [LC 19 删除链表的倒数第 N 个结点：C# / C++ 对照](csharp/leetcode/linked-list/remove-nth-node-from-end-of-list.md)
- [LC 2 两数相加：C# / C++ 对照](csharp/leetcode/linked-list/add-two-numbers.md)

---

## 求职展示口径

这个知识库希望展示的不只是“看过很多资料”，而是：

- 能把学习路线拆成阶段目标，并持续推进。
- 能把项目问题整理成可复用的技术复盘。
- 能在 Unity 项目中验证 C#、UGUI、对象池、配置、数值、反馈和工程边界。
- 能用 C# / C++ 对照解释算法和语言差异。
- 能把面试表达建立在真实代码、真实 Bug 和真实项目决策上。

> 如果发现错误或想交流，可以在 GitHub 仓库中提交 Issue 或 Discussion。
