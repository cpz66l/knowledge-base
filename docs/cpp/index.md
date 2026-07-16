# C++

> C++ 语言学习 — 面向 C# 开发者的 C++ 进阶路线，面向游戏引擎与面试

---

## 为什么学 C++？

Unity 的底层是 C++，理解 C++ 能帮你：

- 看懂 Unity 源码（如 [Unity Blog](https://blog.unity.com/) 的引擎技术文章）
- 写出更高效的 C#（内存布局、缓存友好的设计思路来自 C++ 经验）
- 未来转向 Unreal Engine（C++ 是一等公民）或自研引擎
- 通过大厂面试（游戏开发、引擎开发岗面试主流语言是 C++）

!!! tip "C# vs C++ 心态"
    不是"学一门新语言"，而是在 C# 基础上**打开黑盒**——理解 GC 在做什么、堆/栈真正怎么分配、虚函数为什么有开销。这些知识的受益者是你的 C# 编码能力，不是只服务于 C++。

---

## 目录

| 板块 | 内容 | 面试权重 |
|------|------|----------|
| [基础语法](basics/index.md) | 与 C# 对比：类型系统、指针/引用、const、编译链接 | ⭐⭐⭐ |
| [面向对象](oop/index.md) | 虚函数/vtable、多重继承、RAII、构造/析构顺序 | ⭐⭐⭐⭐⭐ |
| [内存管理](memory/index.md) | 栈/堆、智能指针、内存池、placement new | ⭐⭐⭐⭐⭐ |
| [STL 标准库](stl/index.md) | vector/map/unordered_map、迭代器、算法 | ⭐⭐⭐⭐ |
| [Modern C++](modern-cpp/index.md) | 移动语义、lambda、constexpr、C++11/14/17/20 特性 | ⭐⭐⭐⭐ |
| [LeetCode 算法](leetcode/index.md) | 与 C# 板块同步的算法题解，C++ 实现 | ⭐⭐⭐⭐⭐ |

---

## 学习路线建议

```
第一轮：基础语法（1-2 周）
  → 搞懂指针、引用、const，跟 C# 对照着学

第二轮：面向对象 + 内存（2-3 周）
  → 虚表、智能指针、RAII — 面试核心区

第三轮：STL + Modern C++（2 周）
  → 容器选择、移动语义 — 写代码的核心工具

第四轮：LeetCode（持续）
  → 用 C++ 刷题，熟悉 STL 和 C++ 的代码风格

```

---

## 技术栈（目标态）

```
语言：    C#（主） · C++（进阶） · Lua · HLSL/ShaderLab
引擎：    Unity 6 · Unreal Engine 5（计划） · URP
构建：    CMake · MSBuild
工具：    Rider · Visual Studio · Git · RenderDoc
```

---

> 📎 标签：`C++` `面试` `引擎开发` `Unreal Engine`
