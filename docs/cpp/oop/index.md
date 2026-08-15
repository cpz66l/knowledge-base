# 面向对象

> 状态：学习中 / 待编译小程序验证。
> 证据归属：用户 2026-08-14 C++ 类与对象学习笔记；本次整理为概念提炼，未创建 C++ 工程编译验证。
> 下一步：用一个最小 `Player` 类小程序验证构造、析构、`const` 成员函数和链式调用。

## 当前学习目标

- 能写出一个包含构造函数、析构函数、访问控制和成员函数的最小类。
- 理解初始化列表和函数体赋值的区别。
- 区分 `class` 与 `struct` 的默认访问权限和常见使用约定。
- 理解 `this` 指针和返回 `*this` 的链式调用写法。

## 类的最小结构

```cpp
#include <iostream>
#include <string>

class Player
{
public:
    Player(const std::string& name, int hp, int attack)
        : name_(name), hp_(hp), attack_(attack)
    {
        std::cout << name_ << " created\n";
    }

    ~Player()
    {
        std::cout << name_ << " destroyed\n";
    }

    const std::string& getName() const
    {
        return name_;
    }

    bool isAlive() const
    {
        return hp_ > 0;
    }

    void takeDamage(int damage)
    {
        hp_ -= damage;
        if (hp_ < 0)
        {
            hp_ = 0;
        }
    }

private:
    std::string name_;
    int hp_;
    int attack_;
};
```

这里的核心要素：

| 要素 | 作用 | 当前注意点 |
|---|---|---|
| `public` / `private` | 控制外部能访问哪些成员 | `class` 默认 `private`，通常显式写出访问段 |
| 构造函数 | 创建对象时初始化状态 | 推荐用初始化列表初始化成员 |
| 析构函数 | 对象生命周期结束时自动调用 | 适合观察生命周期，资源管理后续还要结合 RAII |
| `const` 成员函数 | 承诺不修改对象状态 | 读取函数优先标注 `const` |
| 私有成员变量 | 封装对象内部状态 | 外部通过成员函数访问或修改 |

## 初始化列表

初始化列表会在成员构造阶段直接初始化成员：

```cpp
Player(const std::string& name, int hp)
    : name_(name), hp_(hp), attack_(10)
{
}
```

如果在函数体里赋值，成员会先默认构造，再被赋值。对 `std::string` 这类对象来说，初始化列表通常更直接；对 `const` 成员和引用成员来说，初始化列表是必须的。

```cpp
class SpawnRecord
{
public:
    SpawnRecord(int id, Player& owner)
        : id_(id), owner_(owner)
    {
    }

private:
    const int id_;
    Player& owner_;
};
```

`const` 成员创建后不能再赋值，引用成员绑定后也不能改绑到另一个对象，所以它们必须在初始化列表里完成初始化。

## `class` vs `struct`

两者在语法能力上几乎一样，核心区别是默认访问权限：

| 写法 | 默认访问权限 | 常见用途 |
|---|---|---|
| `struct` | `public` | 简单数据打包，例如 `Vector3`、`Color`、配置记录 |
| `class` | `private` | 有行为、有封装、有不变式的对象，例如 `Player`、`Inventory` |

当前阶段可以先用工程约定记忆：纯数据优先 `struct`，有行为和封装优先 `class`。后续学到继承、拷贝和对象模型时再补更细的差异。

## `this` 指针与链式调用

成员函数内部可以通过 `this` 访问当前对象。返回 `*this` 的引用，可以形成链式调用：

```cpp
class Counter
{
public:
    Counter& add(int value)
    {
        value_ += value;
        return *this;
    }

    int value() const
    {
        return value_;
    }

private:
    int value_ = 0;
};

Counter counter;
counter.add(10).add(20).add(30);
```

`this` 可以理解为指向当前对象的指针；`*this` 是当前对象本身。链式调用返回引用，是为了避免返回副本。

## 待验证

当前只有学习笔记，还不能写成掌握。下一步至少补一个：

- 编译运行一个 `Player` 小程序，记录构造和析构输出顺序。
- 对比初始化列表和函数体赋值，说明 `const` 成员、引用成员为什么只能用初始化列表。
- 写一个 `Counter` 链式调用最小例子，验证返回 `Counter&` 与返回 `Counter` 的差异。
- 后续再进入继承、虚函数、拷贝 / 移动和对象切片。
