# 模板与泛型

> 学习状态：学习中
>
> 练习日期：2026-08-28
>
> 证据归属：用户 `inbox/8月28号C++.txt` 记录已运行；本次整理未在本机重新编译
>
> 下一步：补一个模板编译错误或约束失败案例，理解“模板实例化时报错”的阅读方式

## 学习目标

- 理解函数模板和类模板的基本写法。
- 能解释模板是“代码蓝图”，只有使用具体类型时才会实例化。
- 能用简单类模板封装一个固定容量栈，并理解类型参数和非类型模板参数。
- 能把模板与 STL 容器联系起来：`vector<T>`、`map<K, V>`、`stack<T>` 都依赖模板提供泛型能力。

## 当前理解

模板是 C++ 实现泛型编程的核心机制。它允许先写一套和类型无关的代码，再由编译器在使用时根据具体类型生成对应版本。

可以把模板理解成：

```text
template 代码蓝图
  -> 使用 int 调用，实例化出 int 版本
  -> 使用 double 调用，实例化出 double 版本
  -> 使用 string 调用，实例化出 string 版本
```

同一种类型多次调用时，编译器不会为每次调用都重新生成一份完全独立代码；它会复用同一组实例化结果。

## 函数模板

最小函数模板：

```cpp
template <typename T>
void mySwap(T& a, T& b)
{
    T temp = a;
    a = b;
    b = temp;
}
```

使用时可以让编译器自动推导类型：

```cpp
int a = 1;
int b = 2;
mySwap(a, b);          // T 推导为 int

double x = 3.14;
double y = 2.71;
mySwap(x, y);          // T 推导为 double
```

也可以显式指定类型：

```cpp
mySwap<int>(a, b);
```

需要注意：模板参数必须支持函数体中的操作。比如 `getMax(a, b)` 内部使用 `a > b`，那么传入的类型就必须能比较大小。

## 类模板

当一个类需要存储或处理任意类型时，可以使用类模板。例如固定容量栈：

```cpp
template <class T, int MaxSize = 10>
class MyFixedStack
{
public:
    MyFixedStack() : topIndex(0)
    {
        for (int i = 0; i < MaxSize; i++)
        {
            data[i] = T{};
        }
    }

    void push(const T& value)
    {
        if (topIndex >= MaxSize)
        {
            throw std::overflow_error("stack is full");
        }

        data[topIndex++] = value;
    }

    T pop()
    {
        if (isEmpty())
        {
            throw std::underflow_error("stack is empty");
        }

        return data[--topIndex];
    }

    T& top()
    {
        if (isEmpty())
        {
            throw std::underflow_error("stack is empty");
        }

        return data[topIndex - 1];
    }

    bool isEmpty() const
    {
        return topIndex == 0;
    }

    int size() const
    {
        return topIndex;
    }

    int capacity() const
    {
        return MaxSize;
    }
private:
    T data[MaxSize]{};
    int topIndex;
};
```

使用方式：

```cpp
MyFixedStack<int, 5> intStack;
intStack.push(10);
intStack.push(20);

MyFixedStack<char> charStack;
charStack.push('a');
charStack.push('b');
```

`T` 是类型模板参数，`MaxSize` 是非类型模板参数。`MaxSize = 10` 是默认容量，因此 `MyFixedStack<char>` 会使用默认容量 10。

## 本次练习代码输出

用户记录的运行输出：

```text
44
6.45
98
b
myStack<int>
2
isEmpty:0
20,10
isEmpty:1
myStack<char>
2
isEmpty:0
b,a
isEmpty:1
```

输出说明：

- `getMax(1, 44)` 推导为 `int`，输出 `44`。
- `getMax(3.14, 6.45)` 推导为 `double`，输出 `6.45`。
- `getMax<int>('a', 'b')` 显式指定 `int`，字符转为 ASCII 数值比较，输出 `98`。
- `getMax('a', 'b')` 推导为 `char`，输出较大的字符 `b`。
- `MyFixedStack<int, 5>` 和 `MyFixedStack<char, 10>` 都表现为后进先出。

## 常见错误

- 认为模板定义后就已经生成可执行函数；实际上通常要等到使用具体类型时才实例化。
- 忘记包含异常头文件：示例长期保留版需要 `#include <stdexcept>`。
- 认为“类模板永远不能推导类型”过于绝对；C++17 有 CTAD，但刷题和当前学习阶段优先显式写 `vector<int>`、`MyFixedStack<int, 5>`，更清楚也更稳定。
- 在模板函数内部使用某个操作，却没有确认类型是否支持。例如 `a > b` 需要比较运算符。
- 类模板中如果手动管理堆内存，例如 `T* arr = new T[n]`，必须继续处理析构、拷贝构造、拷贝赋值和异常安全；否则容易出现浅拷贝和重复释放。

## 与 C# 泛型的区别

当前先保留最小认知：

| 对比点 | C++ 模板 | C# 泛型 |
|---|---|---|
| 生成时机 | 编译期实例化 | 运行时类型系统支持 |
| 约束方式 | 模板体内用到什么操作，实例化时才暴露问题；也可用 Concepts 明确约束 | 使用 `where` 约束表达类型能力 |
| 常见用途 | STL、泛型算法、零成本抽象 | 集合、接口、委托、业务泛型模型 |
| 报错特点 | 模板实例化错误可能很长 | 泛型约束错误通常更集中 |

这只是入门对照，不能据此写成已经掌握模板元编程或 Concepts。

## 如何验证

建议下次补一份更完整的可复核证据：

```powershell
g++ -std=c++17 main.cpp -o template_demo
.\template_demo.exe
```

最低测试：

- `getMax<int>`、`getMax<double>`、`getMax<char>` 输出符合预期。
- `MyFixedStack<int, 5>` 连续 push / pop 后保持后进先出。
- 空栈 `pop()` 抛出 `underflow_error`。
- 满栈继续 `push()` 抛出 `overflow_error`。

本次材料中已有用户运行输出，因此可记录为中等偏强的 C++ 小程序证据；但缺少编译命令、源文件路径和当前环境复测，暂不升级为“掌握模板”。

## 相关内容

- [C++ 刷题语言笔记](../leetcode/index.md)
- [STL 标准库](../stl/index.md)
- [内存与资源管理](../memory/index.md)

> 标签：`C++` `模板` `函数模板` `类模板` `STL`
