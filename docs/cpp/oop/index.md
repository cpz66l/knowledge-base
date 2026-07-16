# 面向对象

> 虚函数表、多重继承、RAII —— C++ OOP 的精髓与面试核心

!!! warning "面试重灾区"
    虚函数表（vtable）的工作机制、为什么析构函数要 virtual、多重继承的对象布局——这几乎是所有 C++ 面试的必考内容。C# 程序员最容易在这一块翻车，因为 C# 把大部分细节都隐藏了。

---

## C++ vs C# 面向对象对比

| 概念 | C# | C++ |
|------|-----|-----|
| 类定义 | `class Foo { }` | `class Foo { };`（注意分号） |
| 访问修饰符 | 成员各自标注 | `public:` / `private:` / `protected:` 分段 |
| 默认访问 | `private` | `class` 默认 `private`，`struct` 默认 `public` |
| 继承语法 | `class A : B` | `class A : public B`（三种继承方式） |
| 多态 | `virtual` + `override` | `virtual` + `override`（C++11 起） |
| 抽象类 | `abstract class` | 包含纯虚函数 `= 0` 的类 |
| 接口 | `interface` | 纯虚类（只有纯虚函数的抽象类） |
| GC | 自动回收 | 析构函数手动释放 / RAII |

---

## 学习路线

### 1. 虚函数与 vtable ⭐⭐⭐⭐⭐

面试最高频考点。理解虚函数调用为什么比普通函数调用多一次间接跳转。

```
对象内存布局:

┌─────────────────┐
│  vptr (8 bytes) │ ──→ ┌──────────────────┐
├─────────────────┤     │ type_info        │
│  成员变量...      │     │ &Derived::Foo()  │ ← 虚函数表（vtable）
│                 │     │ &Derived::Bar()  │
└─────────────────┘     └──────────────────┘
```

- 虚函数调用：对象 → vptr → vtable → 函数地址（三次间接）
- 非虚函数调用：编译期确定，直接跳转
- 构造函数不能是虚函数（构造时 vptr 尚未初始化）
- 析构函数应该是虚函数（基类指针 delete 时正确调用派生析构）

### 2. 构造与析构顺序

- 构造：基类 → 成员（声明顺序）→ 构造函数体
- 析构：析构函数体 → 成员（声明逆序）→ 基类（逆序）
- **如果基类析构不是 virtual，用基类指针 delete 派生对象 → 未定义行为**

### 3. 多重继承

C# 没有多重继承（只有多接口），C++ 有。

- 一个派生类有多个基类
- 可能有多个 vptr（每个基类一个）
- 菱形继承问题 → 虚继承（`virtual` 关键字在继承处）

### 4. RAII（资源获取即初始化）

C++ 最核心的设计哲学。资源（内存、文件句柄、锁）的生命周期绑定到对象的生命周期。

```cpp
// 构造时获取资源，析构时自动释放
// 没有 finally 块，没有 using 语句 — 析构函数就是保障
class FileHandle {
    FILE* f;
public:
    FileHandle(const char* path) : f(fopen(path, "r")) { }
    ~FileHandle() { if (f) fclose(f); }  // 离开作用域自动调用
};
```

### 5. 继承访问控制

C++ 有三种继承方式（C# 只有一种）：

| 继承方式 | 基类 public → | 基类 protected → | 基类 private → |
|----------|--------------|-----------------|---------------|
| `public` 继承 | public | protected | 不可访问 |
| `protected` 继承 | protected | protected | 不可访问 |
| `private` 继承 | private | private | 不可访问 |

99% 的情况用 `public` 继承。

---

## 待填充内容

> 📝 随学习进度逐步添加：
>
> - 虚函数表详解（含实验验证）
> - 虚继承与菱形继承
> - 协变返回类型
> - CRTP 静态多态
> - `final` / `override` 关键字
> - =default / =delete

---

> 📎 标签：`C++` `OOP` `vtable` `RAII` `多重继承`
