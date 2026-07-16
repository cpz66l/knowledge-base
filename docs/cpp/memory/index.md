# 内存管理

> 手动管理 vs GC —— C++ 内存模型的面试核心与工程基础

!!! warning "面试与性能双核心"
    内存管理是 C++ 区别于 C# 的最本质差异。面试必考智能指针、RAII、栈/堆区别；工程实践中，自定义内存池是游戏引擎高性能的基石。理解 C++ 内存 → 反哺 C# 代码质量（写出更低 GC 压力的代码）。

---

## C++ vs C# 内存对比

| 维度 | C# | C++ |
|------|-----|-----|
| 堆分配 | `new` → GC 自动回收 | `new` → 必须手动 `delete` |
| 栈分配 | 值类型（struct） | 所有类型都可以栈分配 |
| 引用语义 | 类默认引用类型 | 指针/引用显式声明 |
| 确定性析构 | ❌（GC 不可预测） | ✅（离开作用域立即析构） |
| 内存泄漏 | 理论上可能（事件未解绑等） | 主要风险来源 |
| 内存碎片 | 由 GC 压缩处理 | 需自己管理（内存池） |

---

## 学习路线

### 1. 栈与堆 ⭐⭐⭐⭐⭐

```
栈（Stack）:
  - 函数局部变量、参数
  - 自动分配/释放（移动栈指针）
  - 快（连续内存，缓存友好）
  - 大小有限（通常 1-8 MB）

堆（Heap）:
  - new/malloc 分配
  - 手动管理生命周期
  - 慢（需要查找空闲块）
  - 容易碎片化
```

### 2. 智能指针 ⭐⭐⭐⭐⭐

Modern C++（C++11+）的核心工具，把裸指针的"谁负责释放"问题自动化。

| 类型 | 所有权 | 类比 |
|------|--------|------|
| `std::unique_ptr<T>` | 独占所有权 | C# 中无直接对应（类似 Rust 的 Box） |
| `std::shared_ptr<T>` | 共享所有权（引用计数） | 类似 C# 的 GC 引用（但有循环引用问题） |
| `std::weak_ptr<T>` | 不拥有、观察 | 类似 C# 的 `WeakReference<T>` |
| `T*`（裸指针） | 不拥有 | 用于性能关键路径的临时访问 |

```cpp
// unique_ptr：独占，不能拷贝，只能移动
auto p = std::make_unique<Foo>();     // C++14
auto p2 = std::move(p);                // 所有权转移，p 变为 nullptr

// shared_ptr：共享，引用计数
auto s1 = std::make_shared<Foo>();    // 引用计数 = 1
auto s2 = s1;                          // 引用计数 = 2
// 最后一个 shared_ptr 销毁时释放对象

// weak_ptr：打破 shared_ptr 循环引用
std::weak_ptr<Foo> weak = s1;
if (auto sp = weak.lock()) { /* 使用 sp */ }
```

### 3. RAII 与析构

内存只是资源的一种。RAII 把**任何资源**的生命周期绑定到对象：

- 内存：`std::vector`、智能指针
- 文件：`std::fstream`（析构自动 close）
- 互斥锁：`std::lock_guard`、`std::scoped_lock`（析构自动 unlock）
- 线程：`std::thread`（析构时 join/detach）

```cpp
// C# using 语句 ≈ C++ RAII
// C#: using var fs = new FileStream(...) { ... }
// C++: { std::ifstream fs("file.txt"); ... } // 离开作用域自动关闭
```

### 4. 内存池（面试进阶） ⭐⭐⭐

游戏引擎高频考点。避免频繁 `new`/`delete` 的碎片化问题。

- 对象池：子弹/粒子复用
- 栈分配器：帧内临时数据，帧尾全部释放
- 空闲链表：固定大小块的快速分配

### 5. Placement New ⭐⭐

在已分配好的内存上构造对象——自定义分配器的核心工具。

```cpp
alignas(Foo) char buffer[sizeof(Foo)];  // 预分配对齐内存
Foo* f = new (buffer) Foo();             // 在 buffer 上构造（不分配内存）
f->~Foo();                               // 手动调用析构
```

### 6. 内存对齐与缓存 ⭐⭐

- `alignof(T)` — 查询类型的对齐要求
- `alignas(N)` — 指定对齐
- 缓存行友好布局：SoA 优于 AoS（ECS 的核心设计原理）

---

## 待填充内容

> 📝 随学习进度逐步添加：
>
> - 自定义内存池实现（对象池 / 栈分配器）
> - `std::allocator` 的使用与替换
> - 内存泄漏检测工具（Valgrind / AddressSanitizer）
> - 移动语义与零拷贝优化

---

> 📎 标签：`C++` `内存` `智能指针` `RAII` `内存池` `placement new`
