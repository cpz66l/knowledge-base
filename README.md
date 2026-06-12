# 🎮 GameDev 知识库

游戏客户端开发学习笔记，使用 [MkDocs Material](https://squidfunk.github.io/mkdocs-material/) 搭建，托管于 GitHub Pages。

## 本地运行

```bash
# 安装依赖
pip install mkdocs-material

# 启动本地预览
mkdocs serve
```

打开 http://127.0.0.1:8000 即可浏览。

## 内容结构

```
图形学      → 渲染管线、Shader、光照、PBR、阴影
引擎原理    → 游戏循环、ECS、内存管理、动画系统
游戏物理    → 碰撞检测、刚体、角色移动控制器
设计模式    → 组件、观察者、命令、对象池、状态机
游戏数学    → 向量矩阵、四元数、曲线插值
C++ 深度    → 内存模型、智能指针、移动语义、模板、多线程
项目复盘    → 作品集、技术选型、踩坑记录
读书笔记    → 经典书籍的消化输出
```

## 部署

Push 到 `main` 分支后，GitHub Actions 自动构建并部署到 GitHub Pages。

## License

MIT
