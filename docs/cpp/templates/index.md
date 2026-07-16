# 模板与泛型编程

> C++ 泛型能力的核心：从“能使用 STL”进阶到“能读懂标准库、理解编译期多态与模板报错”。

---

## C++ 模板与 C# 泛型的差异

| 维度 | C# 泛型 | C++ 模板 |
|------|---------|----------|
| 类型检查 | 泛型定义与使用处共同检查 | 实例化时根据实际类型检查表达式是否合法 |
| 约束 | `where T : ...` | C++20 `requires` / Concepts；旧代码常见 SFINAE |
| 实现方式 | 运行时类型系统参与，值类型可能生成特化代码 | 编译器按使用情况实例化，常产生不同机器码 |
| 能力范围 | 主要针对类型参数 | 类型、非类型值、模板本身都可作为参数 |
| 常见代价 | 装箱、运行时类型限制等 | 编译时间、代码膨胀、复杂报错 |

!!! tip "学习边界"
    面试和日常开发先掌握函数模板、类模板、类型推导、特化、Concepts 与模板放头文件的原因。复杂模板元编程可以后学。

---

## 1. 函数模板

```cpp
template <typename T>
T max_value(const T& a, const T& b) {
    return a < b ? b : a;
}

auto a = max_value(3, 5);          // T = int
auto b = max_value(2.5, 4.0);      // T = double
// max_value(1, 2.0);              // 推导冲突，需要统一类型或显式指定
```

关键点：

- `typename` 与模板参数列表中的 `class` 通常等价
- 模板不是函数本身，实例化后才产生具体函数
- 参数按值会发生拷贝和退化；只读大对象常用 `const T&`
- 标准库已有能力时优先使用标准库，例如 `std::max`

---

## 2. 类模板与非类型模板参数

```cpp
template <typename T, std::size_t N>
class FixedArray {
public:
    T& operator[](std::size_t index) { return data_[index]; }
    const T& operator[](std::size_t index) const { return data_[index]; }
    constexpr std::size_t size() const { return N; }

private:
    T data_[N]{};
};

FixedArray<float, 16> values;
```

`N` 是编译期常量。`std::array<T, N>` 就是同类设计，实际项目优先使用标准库版本。

---

## 3. 模板为什么通常写在头文件？

编译器在实例化模板时需要看到完整定义。如果只有声明，使用模板的编译单元通常无法生成对应实例。

常见方案：

1. 模板声明和定义都放在 `.h/.hpp`
2. 对有限类型做显式实例化，并把实例化定义放在 `.cpp`
3. 大型项目使用模块或专门的模板实例化策略降低编译成本

这也是 C++ 项目编译慢、错误信息跨越多个头文件的原因之一。

---

## 4. 重载、特化与偏特化

```cpp
template <typename T>
struct TypeName {
    static constexpr std::string_view value = "unknown";
};

template <>
struct TypeName<int> {
    static constexpr std::string_view value = "int";
};

template <typename T>
struct TypeName<T*> {
    static constexpr std::string_view value = "pointer";
};
```

- 函数模板通常优先通过重载表达不同逻辑，不支持偏特化
- 类模板支持全特化和偏特化
- 不要为了“炫技”过度特化，接口语义应保持一致

---

## 5. Concepts 与 requires（C++20）

Concepts 把“模板参数必须支持什么操作”写成可读约束，也能明显改善报错：

```cpp
#include <concepts>

template <typename T>
concept Number = std::integral<T> || std::floating_point<T>;

template <Number T>
T square(T value) {
    return value * value;
}
```

没有 Concepts 的旧代码常通过 `std::enable_if`、`decltype` 和 SFINAE 实现约束。面试时应知道 SFINAE 的含义：**模板替换失败不一定是编译错误，该候选可以从重载集合中移除**。日常新代码优先 Concepts。

---

## 6. 转发引用与完美转发

当 `T&&` 中的 `T` 由模板推导得到时，它可能是转发引用，而不只是普通右值引用：

```cpp
template <typename T, typename... Args>
std::unique_ptr<T> make_object(Args&&... args) {
    return std::unique_ptr<T>(
        new T(std::forward<Args>(args)...)
    );
}
```

- `std::forward` 保留参数原本的左值/右值类别
- 转发引用依赖引用折叠规则
- 实际项目直接使用 `std::make_unique`；这个例子用于理解原理

---

## 7. 模板常见风险

- 模板实例化导致可执行文件增大，应避免为大量近似类型生成重复逻辑
- 报错位置可能远离调用点，先找“第一个属于自己代码的错误”
- 过度泛型会降低可读性；只为真实需求抽象
- 模板库的实现细节暴露在头文件中，会增加增量编译成本
- `decltype(auto)`、转发引用与生命周期结合时容易返回悬空引用

---

## 面试检查清单

- 模板与宏、函数重载、运行时多态有什么区别？
- 函数模板与类模板的特化规则有什么不同？
- 为什么模板实现通常放在头文件？显式实例化是什么？
- `T&&` 什么时候是右值引用，什么时候是转发引用？
- `std::move` 与 `std::forward` 有什么区别？
- Concepts 相比 SFINAE 改善了什么？
- CRTP 如何实现静态多态？它与虚函数多态如何取舍？

---

## 后续练习

1. 实现一个支持迭代的 `FixedArray<T, N>`
2. 用 Concepts 约束一个只接受算术类型的函数
3. 写一个简化版工厂函数，观察左值和右值参数的拷贝/移动次数
4. 阅读 `std::vector` 或 `std::unique_ptr` 的公开接口，识别模板参数和约束

---

## 参考资料

- [C++ Core Guidelines：Templates and generic programming](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines#S-templates)
- [cppreference：Templates](https://en.cppreference.com/w/cpp/language/templates.html)
- [cppreference：Constraints and concepts](https://en.cppreference.com/w/cpp/language/constraints.html)

> 📎 标签：`C++` `模板` `泛型` `Concepts` `SFINAE`
