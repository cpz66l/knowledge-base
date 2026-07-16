# Modern C++

> C++11/14/17/20/23 关键特性 —— 写"现代 C++"而非"带类的 C"

!!! tip "写 C++ 要写 Modern C++"
    面试官想看到的不是 `char*` 和 `malloc`，而是 `std::string`、`std::vector`、lambda 和智能指针。C++11 是分水岭——之前的叫"传统 C++"，之后的叫"现代 C++"。本节聚焦实际开发中最常用的特性。

---

## 版本演进一览

| 版本 | 年份 | 标志性特性 |
|------|------|----------|
| C++98 | 1998 | 第一版标准，STL |
| C++11 | 2011 | **分水岭**：移动语义、lambda、auto、智能指针、nullptr |
| C++14 | 2014 | 泛型 lambda、`make_unique`、`constexpr` 放宽 |
| C++17 | 2017 | `optional`、`variant`、`string_view`、结构化绑定、折叠表达式 |
| C++20 | 2020 | 概念（Concepts）、范围（Ranges）、协程、模块 |
| C++23 | 2023 | `std::expected`、`std::flat_map`、更多 constexpr |

---

## 核心特性速查

### 1. 移动语义（C++11）⭐⭐⭐⭐⭐

面试必考。避免不必要的深拷贝。

```cpp
std::string s1 = "hello";
std::string s2 = std::move(s1);   // 允许移动而非拷贝；s1 仍有效，但状态未指定

// 移动构造函数：
// 把源对象的资源"偷"过来，而非复制
// 对 vector<String> 来说，push_back 时用移动可减少大量分配
```

- `std::move`：只是将表达式转换为 xvalue，并不会自己搬运资源；最终是否移动由目标类型的移动构造/赋值决定
- `std::forward`：完美转发（模板中保持参数的值类别）
- 右值引用 `T&&`：绑定到临时对象或 `std::move` 的结果
- **Rule of Zero**：优先让 RAII 成员管理资源；只有直接管理资源时才按 Rule of Five 成套设计拷贝与移动操作

### 2. Lambda 表达式（C++11）⭐⭐⭐⭐

```cpp
// 基础语法: [捕获](参数) -> 返回类型 { 函数体 }
auto add = [](int a, int b) -> int { return a + b; };

// 捕获列表（核心区别 C# lambda 的地方）
int x = 10;
auto f1 = [x]()  { return x; };      // 按值捕获 x 的副本
auto f2 = [&x]() { x++; };            // 按引用捕获 x
auto f3 = [=]()  { return x; };      // 按值捕获所有使用的外部变量
auto f4 = [&]()  { x++; };            // 按引用捕获所有使用的外部变量
auto f5 = [=, &x]() { /* x 引用捕获，其他值捕获 */ };

// C++14 泛型 lambda
auto generic = [](auto a, auto b) { return a + b; };

// C++17 constexpr lambda
constexpr auto square = [](int n) { return n * n; };
```

!!! warning "注意引用捕获的生命周期"
    如果 lambda 在外部变量销毁后才执行，引用捕获就是悬空引用。异步场景、回调场景应明确捕获对象的所有权，避免无脑使用 `[&]`。

### 3. auto 类型推导（C++11）⭐⭐⭐⭐

```cpp
auto i = 42;                // int
auto f = 3.14;              // double
auto it = v.begin();        // std::vector<int>::iterator
auto& ref = obj;            // 引用（不加 & 就是拷贝）

// C++11: 尾置返回类型
auto add(int a, int b) -> int { return a + b; }

// C++14: 返回类型自动推导
auto add(int a, int b) { return a + b; }
```

### 4. constexpr 编译期计算（C++11/14/17/20）⭐⭐⭐

```cpp
// 编译期求值 → 零运行时开销
constexpr int factorial(int n) {
    return n <= 1 ? 1 : n * factorial(n - 1);
}
int arr[factorial(5)];  // 编译期确定数组大小 → int arr[120]
```

### 5. 范围 for 循环（C++11）⭐⭐⭐⭐

```cpp
// C# foreach ≈ C++ range-based for
for (auto& x : vec) { x *= 2; }          // 修改元素用引用
for (const auto& x : vec) { cout << x; } // 只读用 const 引用
for (auto x : vec) { /* x 是副本 */ }    // 拷贝用值
```

### 6. 常用 Modern C++ 工具类

| 特性 | 版本 | 用途 | 对应 C# |
|------|------|------|---------|
| `std::optional<T>` | C++17 | 值可有可无 | `T?` |
| `std::variant<Ts...>` | C++17 | 多选一类型 | 类型安全的 union |
| `std::string_view` | C++17 | 字符串只读视图（零拷贝） | `ReadOnlySpan<char>` |
| `std::expected<T,E>` | C++23 | 返回值或错误 | Rust `Result` |
| `[[nodiscard]]` | C++17 | 返回值不可丢弃 | — |
| `enum class` | C++11 | 作用域枚举 | `enum`（C# 默认行为） |

```cpp
// optional — 比返回 null 更安全
std::optional<int> divide(int a, int b) {
    if (b == 0) return std::nullopt;
    return a / b;
}
if (auto result = divide(10, 2)) {
    cout << *result;  // 安全使用
}

// string_view — 不拥有字符串，零拷贝子串
void print(std::string_view sv) { cout << sv; }
print("hello");                    // 字面量，不分配
std::string s = "hello";
print(std::string_view{s}.substr(0, 5)); // 视图本身不拷贝，也不延长 s 的生命周期

// 错误示例：返回指向临时字符串的视图
// std::string_view bad() { return std::string("temporary"); }
```

---

## 待填充内容

> 📝 随学习进度逐步添加：
>
> - 移动语义深入（`noexcept` 与容器优化）
> - 完美转发（`std::forward` 实战）
> - 折叠表达式（C++17）
> - Concepts（C++20）泛型约束
> - Ranges（C++20）管道式算法
> - 协程（C++20）基础

---

> 📎 标签：`C++` `Modern C++` `C++11` `lambda` `移动语义`
