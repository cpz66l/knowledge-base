# 面向对象

> 状态：学习中 / 待编译小程序验证。
> 证据归属：用户 2026-08-14 C++ 类与对象学习笔记、2026-08-16 继承与多态学习笔记；本次整理为概念提炼，未创建 C++ 工程编译验证。
> 下一步：用一个最小多态小程序验证基类指针、虚函数派发、虚析构和 `override` 编译检查。

## 当前学习目标

- 能写出一个包含构造函数、析构函数、访问控制和成员函数的最小类。
- 理解初始化列表和函数体赋值的区别。
- 区分 `class` 与 `struct` 的默认访问权限和常见使用约定。
- 理解 `this` 指针和返回 `*this` 的链式调用写法。
- 理解继承、多态、虚函数、虚析构和抽象类的最小用法。

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

## 继承与虚函数

继承可以让子类复用基类的公共接口，多态则允许“用基类指针 / 引用操作子类对象”。一个最小例子：

```cpp
#include <iostream>
#include <memory>
#include <string>
#include <vector>

class Character
{
public:
    Character(const std::string& name, int hp)
        : name_(name), hp_(hp)
    {
    }

    virtual ~Character() = default;

    void printInfo() const
    {
        std::cout << "Name: " << name_ << "\n";
        std::cout << "HP: " << hp_ << "\n";
    }

    virtual void useSkill()
    {
        std::cout << name_ << " uses a normal attack\n";
    }

protected:
    std::string name_;
    int hp_;
};

class Warrior : public Character
{
public:
    explicit Warrior(const std::string& name)
        : Character(name, 200)
    {
    }

    void useSkill() override
    {
        std::cout << name_ << " uses Whirlwind\n";
    }
};

class Mage : public Character
{
public:
    explicit Mage(const std::string& name)
        : Character(name, 120)
    {
    }

    void useSkill() override
    {
        std::cout << name_ << " casts Fireball\n";
    }
};

std::vector<std::unique_ptr<Character>> team;
team.push_back(std::make_unique<Warrior>("Warrior"));
team.push_back(std::make_unique<Mage>("Mage"));

for (const auto& member : team)
{
    member->printInfo();
    member->useSkill();
}
```

多态成立通常需要三件事：

| 条件 | 含义 |
|---|---|
| 继承关系 | 子类继承基类，例如 `Warrior : public Character` |
| 虚函数 | 基类把可能被子类改写的行为标成 `virtual` |
| 基类指针或引用 | 调用点使用 `Character*`、`Character&` 或智能指针持有基类类型 |

`override` 不是语法上必须和 `virtual` “成对出现”，但强烈建议在子类重写虚函数时写上。它能让编译器检查函数签名是否真的覆盖了基类虚函数，避免拼写错误或参数不一致导致“以为重写了，其实没有”。

## 虚析构

如果一个类有虚函数，并且可能通过基类指针删除子类对象，基类析构函数应写成虚析构：

```cpp
class Base
{
public:
    virtual ~Base() = default;
};
```

原因是：

```cpp
Base* object = new Derived();
delete object;
```

如果 `Base` 的析构函数不是虚函数，通过 `Base*` 删除 `Derived` 对象时，子类析构可能不会正确执行，资源释放链路会出问题。当前学习阶段先记规则：**基类只要用于多态，就优先提供虚析构**。

## 抽象类与纯虚函数

纯虚函数用 `= 0` 表示当前类不提供默认实现，要求具体子类补上实现：

```cpp
class Shape
{
public:
    virtual ~Shape() = default;
    virtual float area() const = 0;
};
```

包含至少一个纯虚函数的类是抽象类，不能直接实例化，只能作为接口或基类使用。需要注意：抽象类不一定“全是纯虚函数”，它也可以有普通成员函数、数据成员或构造函数；本页先记录最常见的接口式用法。

## 运算符重载入口

运算符重载可以让自定义类型支持 `+`、`==`、`<<` 等运算符。当前材料只记录学习入口，尚未形成可验证代码。后续至少补一个最小例子：

```cpp
struct Vector2
{
    float x;
    float y;
};

Vector2 operator+(const Vector2& a, const Vector2& b)
{
    return {a.x + b.x, a.y + b.y};
}
```

`operator<<` 常用于输出调试文本，通常会写成非成员函数，并返回 `std::ostream&` 以支持链式输出。

## 待验证

当前只有学习笔记，还不能写成掌握。下一步至少补一个：

- 编译运行一个 `Player` 小程序，记录构造和析构输出顺序。
- 对比初始化列表和函数体赋值，说明 `const` 成员、引用成员为什么只能用初始化列表。
- 写一个 `Counter` 链式调用最小例子，验证返回 `Counter&` 与返回 `Counter` 的差异。
- 编译运行一个 `Character / Warrior / Mage` 小程序，验证虚函数派发和虚析构。
- 后续再进入拷贝 / 移动、对象切片和更系统的资源所有权。
