# C++

> 面向 C# / Unity 开发者的 C++ 学习路线：C# 仍是主线，C++ 用于补足底层能力、算法面试与引擎开发基础。

---

## 为什么学 C++？

Unity 引擎的原生层主要由 C++ 实现。学习 C++ 的价值不是把当前的 C# 主线替换掉，而是帮助你：

- 理解对象布局、内存生命周期、缓存与虚调用等底层成本，反哺 Unity C# 性能意识
- 使用 C++ 完成算法题和笔试，熟悉游戏客户端、引擎岗位常见的代码环境
- 为 Unreal Engine、Unity Native Plug-in、自研引擎或底层工具开发打基础
- 建立编译、链接、并发、调试和跨平台构建等工程能力

!!! tip "学习定位"
    建议保持 **C# / Unity 70%～80%，C++ 20%～30%**。先学会写安全、清晰的现代 C++，再深入对象模型、分配器、无锁结构等引擎专题，不必一开始追求语言细枝末节。

---

## 板块导航

| 板块 | 核心内容 | 优先级 |
|------|----------|--------|
| [基础语法](basics/index.md) | 指针、引用、`const`、值语义、声明与定义 | 必学 |
| [面向对象](oop/index.md) | 构造/析构、虚函数、对象切片、多重继承 | 必学 |
| [内存与资源管理](memory/index.md) | RAII、智能指针、生命周期、对齐与分配器 | 必学 |
| [STL 标准库](stl/index.md) | 容器、迭代器、算法、失效规则、复杂度 | 必学 |
| [Modern C++](modern-cpp/index.md) | 移动语义、lambda、`optional`、`string_view` | 必学 |
| [模板与泛型](templates/index.md) | 函数/类模板、特化、Concepts、SFINAE | 面试高频 |
| [并发与内存模型](concurrency/index.md) | 线程、锁、条件变量、原子、数据竞争 | 面试/引擎高频 |
| [构建、链接与调试](toolchain/index.md) | CMake、库、ODR/ABI、Sanitizer、测试 | 工程必学 |
| [LeetCode 算法](leetcode/index.md) | C++ 刷题模板、STL 选型、与 C# 题解同步 | 持续练习 |

!!! note "哪些不是第一阶段重点"
    模板元编程黑魔法、无锁队列、自定义通用分配器、复杂虚继承布局都应放到第二阶段。第一阶段只需能解释基本原理、写出安全代码，并能定位常见错误。

---

## 推荐学习路线

### 第一轮：能写 C++（2～3 周）

1. 基础语法：指针、引用、`const`、作用域与生命周期
2. STL：优先掌握 `vector`、`string`、`unordered_map`、`queue`、`priority_queue`
3. LeetCode：把正在学习的 C# 题目用 C++ 再实现一次

### 第二轮：能解释 C++（3～5 周）

1. 构造/析构、虚函数、对象切片与 Rule of Zero
2. RAII、智能指针、移动语义、迭代器失效
3. 模板基础、线程同步、编译与链接常见错误

### 第三轮：能做工程（持续）

1. 用 CMake 建一个多文件小项目，并接入单元测试
2. 使用 AddressSanitizer / UndefinedBehaviorSanitizer 定位错误
3. 实现线程池或简化 Job System、对象池、帧分配器等小项目
4. 按需学习 Unity 原生插件接口、P/Invoke 或 Unreal C++

---

## 面试检查清单

能清楚回答以下问题，说明 C++ 基础已经形成闭环：

- 指针与引用有什么区别？悬空指针、野指针怎样产生？
- `const T*`、`T* const`、`const T&` 分别表示什么？
- 构造、析构、拷贝、移动的触发时机是什么？为什么优先 Rule of Zero？
- `unique_ptr`、`shared_ptr`、`weak_ptr` 如何选择？循环引用如何处理？
- `vector` 如何扩容？扩容后哪些指针、引用和迭代器会失效？
- `map` 与 `unordered_map` 的复杂度、顺序性和最坏情况有什么差异？
- 虚函数、虚析构、对象切片和动态绑定分别是什么？
- 模板为什么通常放在头文件？Concepts 解决了什么问题？
- 什么是数据竞争？`mutex`、`atomic`、条件变量分别解决什么问题？
- 声明、定义、编译单元、链接、ODR 和 ABI 是什么？

---

## 与现有知识库的衔接

- C++ 内存布局与缓存知识可结合[性能优化](../performance/index.md)学习
- 引擎渲染相关基础可结合[图形学](../graphics/index.md)学习
- 多线程网络程序可结合[网络编程](../networking/index.md)学习
- C++ 算法题与 [C# LeetCode](../csharp/leetcode/index.md)保持同题对照

---

## 参考资料

- [C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines)：资源管理、并发、模板、源文件与性能实践
- [cppreference](https://en.cppreference.com/w/cpp.html)：语言与标准库查询
- [CMake Tutorial](https://cmake.org/cmake/help/latest/guide/tutorial/index.html)：官方构建入门
- [Unity Native plug-ins](https://docs.unity3d.com/Manual/NativePlugins.html)：Unity 与原生代码互操作入口

---

> 📎 标签：`C++` `面试` `引擎开发` `Modern C++` `Unity`
