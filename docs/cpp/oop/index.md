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

面试高频考点。C++ 标准没有规定必须使用 vtable，但主流编译器通常通过对象中的 vptr 和虚函数表实现动态绑定。

```
对象内存布局:

┌─────────────────┐
│  vptr (8 bytes) │ ──→ ┌──────────────────┐
├─────────────────┤     │ type_info        │
│  成员变量...      │     │ &Derived::Foo()  │ ← 虚函数表（vtable）
│                 │     │ &Derived::Bar()  │
└─────────────────┘     └──────────────────┘
```

- 虚调用通常需要读取 vptr，再从表中取得目标函数地址；具体布局和成本由 ABI、编译器与优化决定
- 编译器能确定动态类型时可能执行去虚拟化，虚函数不一定产生运行时间接调用
- 构造函数不能声明为虚函数；对象尚未完成构造时也没有完整的派生类语义
- 只有当类型会被当作多态基类并通过基类指针销毁时，基类析构函数才必须是 `virtual`

### 2. 构造与析构顺序

- 构造：基类 → 成员（声明顺序）→ 构造函数体
- 析构：析构函数体 → 成员（声明逆序）→ 基类（逆序）
- **如果通过基类指针 `delete` 派生对象，而基类析构函数不是 virtual，会产生未定义行为**

### 3. 对象切片与动态类型

按值把派生类对象赋给基类对象，会只保留基类子对象，这叫对象切片：

```cpp
Derived derived;
Base value = derived;      // 切片：Derived 独有部分丢失
Base& reference = derived; // 不切片：保留动态类型
```

- 多态参数通常使用 `Base&`、`const Base&` 或观察型 `Base*`
- 容器若要保存异构多态对象，通常使用 `std::unique_ptr<Base>`
- 不要把“需要多态”自动等同于“必须继承”，组合通常更容易维护

### 4. 多重继承

C# 没有多重继承（只有多接口），C++ 有。

- 一个派生类有多个基类
- 可能有多个 vptr（每个基类一个）
- 菱形继承问题 → 虚继承（`virtual` 关键字在继承处）

### 5. RAII（资源获取即初始化）

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

### 6. 特殊成员函数与 Rule of Zero

编译器可以生成默认构造、析构、拷贝和移动操作。现代 C++ 优先遵循 **Rule of Zero**：让 `std::vector`、`std::string`、智能指针等 RAII 成员管理资源，业务类不手写析构/拷贝/移动。

只有直接管理底层资源时，才考虑 Rule of Five，并认真处理：

- 拷贝构造与拷贝赋值是否表示深拷贝
- 移动后源对象仍需处于“有效但状态未指定”的可析构状态
- 移动构造是否可标记 `noexcept`，以便标准容器安全地选择移动
- 是否应该用 `= delete` 禁止拷贝

### 7. 继承访问控制

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
> - 空基类优化（EBO）与 `[[no_unique_address]]`

---

> 📎 标签：`C++` `OOP` `vtable` `RAII` `多重继承`
