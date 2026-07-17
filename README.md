# 🎮 GameDev 知识库

游戏客户端开发学习笔记，使用 [MkDocs Material](https://squidfunk.github.io/mkdocs-material/) 搭建，托管于 GitHub Pages。


打开 https://cpz66l.github.io/knowledge-base/ 即可浏览。

## 内容结构

| 模块 | 内容 |
|------|------|
| **C#** | 面向对象编程、GC 与内存管理、async/await、工程实践 |
| **LeetCode** | C# / C++ 双语题解，按哈希、双指针、滑动窗口、DP、二叉树等题型整理 |
| **C++** | C# 对照语法、对象模型、内存与 RAII、STL、Modern C++、模板、并发、CMake/调试、LeetCode |
| **Unity** | 生命周期、ScriptableObject、Prefab、Addressables 资源管理、Editor 工具、UGUI、动画系统 |
| **图形学** | 渲染管线、Shader 基础、光照与着色、PBR 理论、阴影技术 |
| **性能优化** | Profiler 深度使用、内存管理（对象池 / GC 优化）、渲染性能、CPU 与代码优化 |
| **网络编程** | TCP/UDP 基础、Unity Netcode、状态同步、帧同步与锁步 |
| **热更新** | Lua 基础、xLua、资源热更新、完整热更流程 |
| **项目实践** | 作品集总览 |

## 使用方式

- 从 `docs/roadmap/index.md` 查看当前学习路线与阶段产出
- 从 C#、C++、Unity 等专题目录查询已有知识
- 使用 `docs/checklists/` 判断知识是否已经完成练习和验证
- 使用 `docs/reviews/` 记录每周与项目复盘
- 尚未学习的主题只维护规划，不提前补写完整结论

## 知识收件箱

把随手笔记、Unity 脚本、截图、PDF、链接文件或脚本目录直接放入 `inbox/`，不需要提前分类或重命名。需要整理时告诉智能体“整理 inbox 中尚未处理的内容”即可。

智能体会按照 `AGENTS.md` 中的规则自动识别主题、检查重复内容、更新 `docs/`、提炼可复用示例并把原资料移动到本地的 `archive/`。`inbox/` 和 `archive/` 默认不会提交到 Git，避免误提交大文件或私人资料。

## 部署

Push 到 `main` 分支后，GitHub Actions 自动构建并部署到 GitHub Pages。

## License

MIT
