# C# / Unity 主线

> 主线目标是独立完成 Unity 客户端功能与工程模块。未学习的主题只保留规划入口，等真正学习后再补充正文。

---

## 路线顺序

### 阶段 1：C# 语言基础

阶段入口：[C# 语言与面向对象路线](../csharp/language/index.md)。

推荐从现有内容开始：

1. [面向对象编程](../csharp/oop/index.md)
2. [值类型与引用类型](../csharp/oop/value-vs-reference.md)
3. [泛型](../csharp/oop/generics.md)
4. [委托与事件](../csharp/oop/delegates-and-events.md)
5. [C# LeetCode](../csharp/leetcode/index.md)，作为持续练习而非主线终点

最小产出：

- 一个不依赖 Unity 场景的纯 C# 模块
- 一段泛型或事件的真实使用记录
- 至少一道算法题的思路与复杂度说明

### 阶段 2：Unity 核心能力

专题入口：[Unity](../unity/index.md)。该页面只展示已经形成内容的文章，未完成主题保留为计划清单。

当前已有内容：

1. [UGUI](../unity/ugui/index.md)
2. [动画系统](../unity/animation/index.md)

计划主题：生命周期、ScriptableObject、Prefab、Addressables 和 Editor 工具。完成最小实验后再建立正式文章。

最小产出：

- 一个可运行 UI 或交互 Demo
- 一份生命周期调用顺序记录
- 一个 ScriptableObject / Prefab / Addressables 的实际应用

### 阶段 3：C# 工程能力

以下内容已经进入规划，但当前占位内容不代表已经学会：

1. [运行时与异步路线](../csharp/runtime/index.md)
2. [C# 工程实践路线](../csharp/engineering/index.md)
3. [GC 与内存管理](../csharp/gc-and-memory.md)
4. [async/await 异步](../csharp/async-await.md)
5. 测试、日志、异常处理、程序集与模块化：待学习后新增

学习这些内容时，优先记录：

- 真实问题是什么
- 使用什么工具或实验验证
- 结论适用于什么 Unity / .NET 环境
- 最终应用到了哪个项目

### 阶段 4：进入专项

只有当主线项目产生需要时，再进入：

- [性能优化](../performance/index.md)
- [网络编程](../networking/index.md)
- [图形学](../graphics/index.md)
- [热更新](../hotupdate/index.md)

---

## 阶段完成判断

| 状态 | 判断标准 |
|------|----------|
| 已阅读 | 能复述文章内容 |
| 已练习 | 独立完成一个最小示例 |
| 已应用 | 在 Demo 或项目中真实使用 |
| 已验证 | 有测试、Profiler、日志或运行结果 |
| 已复盘 | 记录过错误、取舍和改进方向 |

检查入口：[C# 工程能力清单](../checklists/csharp-engineering.md)与[Unity 项目清单](../checklists/unity-project.md)。

---

## 下一步

当前只选择一个阶段作为主目标，并在[学习路线总览](index.md)更新当前产出。
