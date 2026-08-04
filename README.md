# GameDev 知识库

这是一个面向 **Unity 游戏客户端开发实习** 的个人知识库，使用 [MkDocs Material](https://squidfunk.github.io/mkdocs-material/) 搭建，并通过 GitHub Pages 发布。

在线访问：<https://cpz66l.github.io/knowledge-base/>

## 知识库定位

这个仓库不是资料搬运，也不是为了把目录填满而提前写结论。它用于沉淀我在准备游戏客户端开发方向时，经过学习、练习、项目验证或复盘后的内容。

当前主线是：

- 用 C# / Unity 做出可运行、可复盘、可展示的项目。
- 用 C++ 和计算机基础补齐客户端岗位的底层能力。
- 用 LeetCode 双语题解训练算法表达和 C# / C++ 对照能力。
- 用项目日志、Bug 记录、Review 和检查清单，把“学过”推进到“能解释、能实现、能验证”。

## 内容结构

| 模块 | 内容 |
| --- | --- |
| [学习路线](docs/roadmap/index.md) | C# / Unity 主线、C++ 副线、计算机基础、专项能力和项目路线 |
| [C#](docs/csharp/index.md) | 面向对象、泛型、委托事件、GC 与内存、async/await、工程实践 |
| [C++](docs/cpp/index.md) | 基础语法、OOP、内存管理、STL、Modern C++、工具链和刷题路线 |
| [LeetCode 双语题解](docs/csharp/leetcode/index.md) | 使用 C# / C++ 对照整理常见题型、模板和易错点 |
| [Unity](docs/unity/index.md) | 生命周期、UGUI、Prefab、ScriptableObject、资源管理、动画和编辑器工具 |
| [图形学](docs/graphics/index.md) | 渲染管线、Shader、光照着色、PBR、阴影等专题路线 |
| [性能优化](docs/performance/index.md) | Profiler、GC、对象池、渲染性能、CPU 与代码优化 |
| [网络编程](docs/networking/index.md) | TCP/UDP、Unity Netcode、状态同步、帧同步与锁步 |
| [热更新](docs/hotupdate/index.md) | Lua、xLua、资源热更新和完整热更流程 |
| [项目实践](docs/projects/index.md) | Backpack Survivor 项目日志、技术拆解和复盘 |
| [检查与复盘](docs/checklists/index.md) | 面试、Unity 项目、C# 工程能力、每周复盘和项目复盘模板 |

## 当前重点

截至 2026-08-04，知识库共有约 154 篇 Markdown 笔记，当前优先级如下：

- **项目主线**：持续推进 [Backpack Survivor](docs/projects/backpack-survivor/index.md)，把 Unity、C#、UGUI、对象池、掉落、背包、波次、数值和复盘串成一个可展示 Demo。
- **算法训练**：继续维护 [LeetCode 双语题解](docs/csharp/leetcode/index.md)，重点补齐链表、树、图、动态规划、堆和常见面试题型。
- **语言基础**：补齐 C++ 基础语法、STL、内存模型和 C# 工程能力，为后续实习面试和更底层的客户端开发打基础。
- **专项储备**：图形学、性能、网络和热更新先保留路线与最小笔记，等项目或面试需要时再深入补全。

## 使用方式

- 看整体路线：从 [学习路线总览](docs/roadmap/index.md) 开始。
- 查具体知识：进入左侧专题目录，或使用站点搜索。
- 看项目沉淀：进入 [项目实践](docs/projects/index.md)，重点查看 Backpack Survivor 系列。
- 判断是否掌握：使用 [学习检查清单](docs/checklists/index.md)。
- 写新笔记：参考 [知识文章模板](docs/guides/note-template.md)。
- 做阶段复盘：使用 [复盘中心](docs/reviews/index.md)。

## 本地运行

```bash
pip install -r requirements.txt
mkdocs serve
```

构建静态站点：

```bash
mkdocs build
```

推送到 `main` 后，GitHub Actions 会自动构建并部署到 GitHub Pages。

## 收件箱工作流

临时资料、截图、PDF、链接、脚本或待整理内容可以先放入 `inbox/`。整理时再按照 `AGENTS.md` 和 `HANDOFF.md` 的规则归档到对应专题。

- `docs/`：正式知识库内容，会进入 Git。
- `inbox/`：本地收件箱，默认不提交。
- `archive/`：本地原始资料归档，默认不提交。

## 维护原则

- 不提前把未学习内容写成完整结论。
- 每篇笔记尽量包含问题背景、关键概念、最小示例、验证方式和踩坑记录。
- 项目经验优先写“现象 -> 排查 -> 根因 -> 修复 -> 沉淀规则”。
- 面试表达优先来自真实项目、真实 Bug 和真实练习，而不是空泛背诵。

## License

MIT
