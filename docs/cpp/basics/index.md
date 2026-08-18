# 基础语法

> 当前阶段：学习中。此页只保留学习顺序和待办，不提前补写尚未掌握的结论。

## 学习顺序

1. 变量、基本类型、运算符、条件和循环
2. 函数、参数传递、作用域和命名空间
3. 数组、字符串、结构体和枚举
4. 指针、引用、nullptr 和 const
5. 值语义、对象生命周期和基础初始化
6. 头文件、源文件、声明、定义、编译和链接
7. 类型转换、异常处理和常见未定义行为

## 与 C# 对照记录

每次只记录自己实际遇到的差异，例如：

- C++ 的值传递、指针传递和引用传递
- C++ 字符串、数组和容器与 C# 的差异
- C++ 编译链接流程与 C# 构建流程的差异

## 2026-08-10/11 基础语法笔记

> 证据归属：用户学习笔记。以下内容是已阅读和练习中的语法记录，仍需通过小程序、刷题或编译错误复盘继续验证。

### 运算符与控制流

| 类别 | 语法 | 说明 |
|---|---|---|
| 算术 | `+` `-` `*` `/` `%` | `%` 常用于取余和循环下标 |
| 比较 | `==` `!=` `<` `>` `>=` `<=` | 返回布尔结果 |
| 逻辑 | `&&` `||` `!` | `!` 是英文感叹号，注意不要写成中文全角符号 |
| 赋值 | `=` `+=` `-=` `*=` `/=` `%=` | 复合赋值会先计算再写回 |
| 自增自减 | `++` `--` | `x++` 先用后加，`++x` 先加后用 |
| 三元表达式 | `condition ? a : b` | 简单条件取值可以用，但复杂逻辑不建议硬塞 |
| `sizeof` | `sizeof(type)` | 返回类型或对象占用字节数 |

`do while` 至少执行一次，适合“先执行一次，再根据输入决定是否继续”的场景：

```cpp
do
{
    // ...
} while (input != 0);
```

### 范围 for 与引用传参

```cpp
for (const auto& weapon : weapons)
{
    std::cout << weapon;
}
```

- `auto` 让编译器根据容器元素自动推断类型。
- `&` 表示引用，避免拷贝元素。
- `const` 表示只读，循环体内不能修改元素。

函数参数中也常用 `const std::string&` 避免不必要拷贝：

```cpp
void greet(const std::string& name)
{
    std::cout << "你好," << name << "!" << std::endl;
}
```

这和 C# 中引用类型变量“像是在传引用”的直觉接近，但 C++ 必须显式写出引用符号和只读语义。

### 函数声明、定义、重载和默认参数

```cpp
int add(int a, int b); // 声明

int add(int a, int b)  // 定义
{
    return a + b;
}
```

- 声明告诉编译器“有这个函数”。
- 定义给出函数体。
- 如果函数定义写在 `main` 后面，通常需要提前声明。
- 函数重载依赖参数类型或数量区分版本，例如 `int maxValue(int, int)` 和 `double maxValue(double, double)`。
- 默认参数应从右往左提供，避免调用时产生歧义。

### 结构体与嵌套

```cpp
struct Student
{
    std::string name;
    int score;
};

std::vector<Student> students;
students.push_back({"Alice", 95});
```

结构体可以嵌套，用来表达游戏对象里的位置、旋转、缩放等复合数据：

```cpp
struct Vector3
{
    float x;
    float y;
    float z;
};

struct Transform
{
    Vector3 position;
    Vector3 rotation;
    Vector3 scale;
};
```

## 2026-08-12 指针与引用笔记

> 证据归属：用户学习笔记。以下内容是 C++ 入门理解记录，本次没有额外创建 C++ 工程编译；需要继续通过刷题、小程序和编译错误复盘验证。

### 引用：已有变量的别名

引用 `T&` 可以理解为给已有变量起一个别名。通过引用修改，等价于修改原变量：

```cpp
int hp = 100;
int& hpRef = hp;

hpRef -= 30;
std::cout << hp;    // 70
std::cout << hpRef; // 70
```

必须记住三条规则：

| 规则 | 说明 |
|---|---|
| 必须初始化 | `int& bad;` 不能编译，因为引用必须绑定到已有对象 |
| 不能重新绑定 | 引用一旦绑定，就不能改成另一个变量的别名 |
| 语义上不可为空 | C++ 没有正常的 `nullptr` 引用；如果通过错误解引用制造引用，属于未定义行为 |

常见使用场景：

- 大对象只读传参：`void f(const std::string& s)`，避免拷贝且不允许修改。
- 需要修改外部变量：`void swap(int& a, int& b)`。
- 范围 for 修改元素：`for (auto& x : values)`。

一句话：引用更简洁，适合“必须有对象、不会换对象”的场景；如果需要表示“可能没有对象”或“运行中换目标”，优先用指针。

### 指针：保存地址的变量

指针 `T*` 保存的是某个对象的地址。`&` 取地址，`*` 解引用，`->` 访问指针指向对象的成员：

```cpp
int hp = 100;
int* ptr = &hp;

std::cout << ptr;  // 输出地址值
std::cout << *ptr; // 100

*ptr = 70;
std::cout << hp;   // 70
```

`ptr->member` 是 `(*ptr).member` 的简写。

指针比引用多出几类能力，也带来更多风险：

| 能力 / 风险 | 说明 |
|---|---|
| 可以为 `nullptr` | 使用前应判断；解引用空指针属于未定义行为 |
| 可以重新指向 | 适合“目标可能变化”的场景 |
| 可以做指针算术 | 例如 `*(arr + i)` 等价于 `arr[i]`，但越界风险更高 |
| 可能悬空 | `delete` 后原指针仍保存旧地址，继续使用属于未定义行为 |

如果手动 `delete` 裸指针，释放后应立刻置空：

```cpp
delete ptr;
ptr = nullptr;
```

这只是降低误用风险，不代表裸指针管理资源是推荐默认方案。后续进入 RAII 和智能指针后，应优先让对象所有权由类型系统表达。

### 三种传参方式

| 方式 | 例子 | 是否修改外部变量 | 适用场景 |
|---|---|---|---|
| 值传递 | `void f(int x)` | 否，修改的是副本 | 小对象、无需修改调用方 |
| 引用传递 | `void f(int& x)` | 是 | 必须有对象，且要修改调用方 |
| 指针传递 | `void f(int* x)` | 可以，需先判空 | 目标可能为空或可能换指向 |

```cpp
void levelUp(int* level)
{
    if (level != nullptr)
    {
        *level += 1;
    }
}

int value = 10;
levelUp(&value);
std::cout << value; // 11
```

### `const` 与指针组合

| 写法 | 口诀 | 含义 |
|---|---|---|
| `const int* p` | 指向常量的指针 | 可以改 `p` 指向，不能通过 `p` 改值 |
| `int* const p` | 常量指针 | 不能改 `p` 指向，可以通过 `p` 改值 |
| `const int* const p` | 双锁 | 指向和值都不能改 |

阅读口诀：`const` 修饰它右边的东西；如果右边没有东西，就修饰左边。

## 2026-08-17 Modern C++ 入门笔记

> 证据归属：用户学习笔记与智能指针截图。以下内容是已阅读 / 待验证的语法记录；本次没有额外创建 C++ 工程编译。

### `enum class`：更安全的枚举

```cpp
enum class WeaponType
{
    Sword,
    Bow,
    Staff,
    Axe,
};

WeaponType weapon = WeaponType::Sword;
int rawValue = static_cast<int>(weapon);
```

- `enum class` 不会隐式转换为 `int`，比旧式 `enum` 更不容易误用。
- 使用时需要写枚举类型作用域，例如 `WeaponType::Sword`。
- 如果确实需要数字值，要显式 `static_cast<int>(weapon)`。

### 结构化绑定

```cpp
std::map<std::string, int> scores = {
    {"Alice", 98},
    {"Bob", 90},
};

for (const auto& [name, score] : scores)
{
    std::cout << name << ":" << score << std::endl;
}

struct Point
{
    float x;
    float y;
};

Point p{10.0f, 20.0f};
auto [px, py] = p;
```

- 结构化绑定可以拆 `std::pair`、`std::tuple` 或简单聚合结构体。
- 遍历 `map` 时常写 `const auto& [key, value]`，避免拷贝键值对。

### `nullptr` 与统一初始化

```cpp
int* ptr = nullptr;
if (ptr == nullptr)
{
    std::cout << "ptr 是空指针" << std::endl;
}

int a{10};
double b{3.14};
std::vector<int> values{1, 2, 3, 4, 5};
std::string text{"Hello"};
```

- `nullptr` 是类型安全的空指针字面量，优先替代旧的 `NULL` 或 `0`。
- 花括号初始化能统一基础类型、容器和对象初始化写法，也能减少部分窄化转换问题。

## 最小练习

- [ ] 独立完成一个多函数 C++ 小程序
- [ ] 用 C++ 重写一道已经做过的算法题
- [ ] 记录一次编译错误或运行时错误的排查过程
- [ ] 用最小程序验证值传递、引用传递、指针传递的差异
- [ ] 写下目前仍然分不清的语法概念

## 当前记录

- 已学内容：运算符、分支循环、范围 for、函数声明 / 定义 / 重载、默认参数、结构体基础、引用、指针、`nullptr`、`const` 指针组合
- 已验证内容：能够完成部分 LeetCode 题目
- 待补内容：引用 / 指针生命周期、悬空指针、RAII、头文件拆分、编译链接、异常处理
- 下一步：用一个多函数小程序验证函数声明、结构体、`vector`、`string`、引用和指针传参的组合使用
