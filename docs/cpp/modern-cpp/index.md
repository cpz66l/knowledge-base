# Modern C++

> 状态：学习中。当前通过 C++ 小练习和 LeetCode 逐步引入 `auto`、范围 for、lambda、`std::function` 和智能指针等特性。

## 计划学习内容

- C++11/14/17/20 的常用特性
- auto、范围 for 和 lambda
- 移动语义与右值引用
- constexpr、optional、variant、string_view
- 默认成员函数和 Rule of Zero
- 现代 C++ 的可读性与安全性

## 最小产出

- 把一个旧式写法改成现代 C++ 写法
- 记录一次移动或生命周期实验
- 说明某个特性解决了什么实际问题

## 当前记录

- 状态：学习中
- 关联练习：2026-08-26 lambda + `std::sort`；2026-08-27 `std::function` 回调练习；智能指针仍待可运行输出
- 仍未理解：lambda 捕获生命周期、严格弱序、`std::function` 类型擦除成本、空状态调用异常和 C# 委托 / 事件的边界

## 2026-08-26/27 lambda 与 std::function 入门

> 证据归属：用户 `inbox/8月26号C++.txt` 和 `inbox/8月27号C++.txt` 学习记录；用户标注代码已运行。当前环境未安装 `g++` / `clang++` / `cl`，本次未重新编译。

### lambda 基本结构

```cpp
[捕获列表](参数列表) -> 返回类型
{
    函数体
}
```

当前先记住：lambda 是一个临时定义的可调用对象，可以直接放到算法、回调或局部逻辑中使用。返回类型很多时候可以让编译器自动推导。

常见捕获方式：

| 写法 | 含义 | 当前阶段注意点 |
|---|---|---|
| `[]` | 不捕获外部局部变量 | 最安全，适合纯比较器 |
| `[=]` | 按值捕获用到的外部变量 | 默认只读副本；要修改副本需额外理解 `mutable` |
| `[&]` | 按引用捕获用到的外部变量 | 能修改外部变量，但要小心引用对象生命周期 |
| `[x]` | 只按值捕获 `x` | 比 `[=]` 更明确 |
| `[&x]` | 只按引用捕获 `x` | 比 `[&]` 更明确 |
| `[=, &x]` | 其余按值，`x` 按引用 | 混合捕获时要让读者一眼看出谁会被修改 |

### lambda 作为 sort 比较器

```cpp
std::vector<int> nums{3, 5, 8, 6, 9, 1};

std::sort(nums.begin(), nums.end(), [](int a, int b)
{
    return a > b; // 降序
});
```

比较器返回 `true` 的含义是：第一个参数应该排在第二个参数前面。因此：

- `a < b` 表示升序。
- `a > b` 表示降序。
- 对结构体排序时，可以先比较主字段，再比较次字段。

```cpp
struct Student
{
    std::string name;
    int score;
};

std::sort(students.begin(), students.end(), [](const Student& a, const Student& b)
{
    if (a.score != b.score)
    {
        return a.score > b.score; // 分数高的在前
    }

    return a.name < b.name;       // 同分时按名字升序
});
```

用户练习中同分时写的是 `a.name > b.name`，表示名字按逆序排列；这是合法规则，只要排序目标本来就是“名字降序”。面试和工程中要把主次排序规则写清楚，避免比较器看起来像写反。

### std::function：统一保存可调用对象

`std::function` 可以保存函数指针、lambda、函数对象等，只要签名匹配：

```cpp
#include <functional>

int add(int a, int b)
{
    return a + b;
}

std::function<int(int, int)> operation = add;
operation = [](int a, int b) { return a * b; };
```

当前理解可以和 C# 委托类比：两者都能“把方法当作数据传递”。但边界不同：

| 对比点 | C++ `std::function` | C# 委托 / event |
|---|---|---|
| 定位 | 标准库模板类，统一包装一个可调用对象 | 运行时支持的类型安全方法引用 |
| 多播 | 不原生多播，可用 `std::vector<std::function<...>>` 自己组织 | 委托天然支持 `+=` / `-=` 多播 |
| 事件安全 | 本身不提供发布订阅访问限制 | `event` 限制外部只能订阅 / 取消，不能直接触发或覆盖 |
| 空状态 | 可以用 `if (func)` 判断；空调用会抛 `std::bad_function_call` | 委托调用前通常要判空或用 `?.Invoke()` |

### 当前易错点

- 使用 `std::numeric_limits` 时需要包含 `<limits>`。
- 做除法 lambda 前要处理除数为 0，否则运行时会出错。
- 遍历 `std::vector<Student>` 时，若只读输出，优先写 `for (const auto& student : students)`，避免拷贝结构体。
- `std::sort` 的比较器要满足严格弱序：不要让 `compare(a, b)` 和 `compare(b, a)` 同时为 true。

## 相关内容

- [STL 标准库](../stl/index.md)
- [C++ 刷题模板与易错点](../leetcode/templates.md)
- C# 对照：[委托与事件](../../csharp/oop/delegates-and-events.md)
