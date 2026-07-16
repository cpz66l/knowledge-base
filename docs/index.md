# 🎮 GameDev 知识库

> Unity 客户端开发学习笔记 —— C# · C++ · Unity · 图形学 · 性能优化 · 网络编程 · 热更新

---

## 从这里开始

知识库同时提供两种入口：

- **按路线学习**：先进入[学习路线总览](roadmap/index.md)，查看当前阶段、学习顺序和阶段产出
- **按专题查询**：直接进入下方 C#、C++、Unity、性能等专题目录

!!! important "当前原则"
    尚未学习的内容只保留路线与待办，不提前写成完整结论。已有文章全部保留，后续通过练习、项目和复盘逐步补充自己的理解。

---

## 学习闭环

```text
路线规划 → 学习文章 → 最小练习 → 项目应用 → 工具验证 → 复盘回写
```

| 当前入口 | 用途 |
|----------|------|
| [C# / Unity 主线](roadmap/csharp-unity.md) | 当前主要学习方向 |
| [C++ 底层副线](roadmap/cpp.md) | 面试、底层与引擎开发基础 |
| [专项能力路线](roadmap/specializations.md) | 性能、图形、网络、热更新 |
| [项目实践路线](roadmap/projects.md) | 把知识应用到可运行项目 |
| [学习检查清单](checklists/index.md) | 判断是否真正掌握 |
| [复盘中心](reviews/index.md) | 沉淀问题、验证与下一步 |

---

## 关于我

游戏客户端开发学习者，专注于 **Unity / C#** 方向。

目前正在系统学习：

- 💻 **C#**：GC 机制、面向对象编程、async/await、Unity C# 最佳实践、LeetCode 算法笔记
- 🖥️ **C++**：当前学习基础语法与部分 LeetCode；OOP、内存、STL、Modern C++、模板、并发、CMake/调试均作为后续路线
- 🎯 **Unity**：生命周期、ScriptableObject、Prefab、Addressables、Editor 工具
- 🖼️ **图形学**：渲染管线、Shader 编程、PBR、光照模型、阴影技术
- ⚡ **性能优化**：Profiler 深度使用、内存与 GC 优化、渲染性能、CPU/代码优化
- 🌐 **网络编程**：TCP/UDP、Unity Netcode、状态同步、帧同步
- 🔥 **热更新 (Lua)**：Lua 基础、xLua、AssetBundle、完整热更流程
- 🔧 **项目实践**：Unity Demo 项目、技术选型、踩坑记录

---

## 知识库导航

| 分类 | 内容 |
|------|------|
| [C#](csharp/index.md) | GC 内存、值类型与引用类型、async/await、Unity C# 实践、LeetCode |
| [C++](cpp/index.md) | 基础语法、对象模型、内存与 RAII、STL、模板、并发、构建调试、LeetCode |
| [Unity](unity/index.md) | 生命周期、ScriptableObject、Prefab、Addressables、Editor |
| [图形学](graphics/index.md) | 渲染管线、Shader、光照、PBR、阴影 |
| [性能优化](performance/index.md) | Profiler、内存管理、渲染性能、CPU 优化 |
| [网络编程](networking/index.md) | TCP/UDP、Netcode、状态同步、帧同步 |
| [项目实践](projects/index.md) | 作品集、技术选型、踩坑记录 |
| [热更新 (Lua)](hotupdate/index.md) | Lua 基础、xLua、资源热更、完整流程 |

---

## 技术栈

```
语言：    C#（主） · C++（进阶） · Lua · HLSL/ShaderLab · Python
引擎：    Unity 6 · Unreal Engine 5（计划） · URP
框架：    xLua · Netcode for GameObject
工具：    Rider · Git · RenderDoc · Unity Profiler
```

---

## 关于这个知识库

这个知识库是我学习 Unity 客户端开发的**消化输出**。

- 附上关键代码片段，理论与实现结合
- 持续更新，commit 历史就是我的学习轨迹
- 以路线、练习、项目、验证和复盘形成学习闭环

> 如果发现错误或想交流，欢迎提 [Issue](https://github.com/CPZ66L/knowledge-base/issues) 或在 [Discussions](https://github.com/CPZ66L/knowledge-base/discussions) 讨论。
