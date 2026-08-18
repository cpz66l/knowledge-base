# 内存与资源管理

> 状态：学习中 / 待实验。
> 证据归属：用户 2026-08-15 C++ 栈 / 堆学习笔记与内存示意图、2026-08-16 拷贝控制学习笔记；本次整理为概念提炼，未使用调试器或内存检测工具验证。
> 下一步：用最小程序验证对象生命周期，再进入 RAII 和智能指针。

## 当前学习目标

- 区分栈上局部变量、栈上指针变量和堆上动态对象。
- 明确 `new/delete` 与 `new[]/delete[]` 必须匹配。
- 理解内存泄漏、重复释放和悬空指针为什么危险。
- 建立“能用栈就用栈，必须表达所有权时优先 RAII / 智能指针”的方向感。
- 初步理解含裸指针成员的类为什么容易出现浅拷贝问题。
- 初步区分 `std::unique_ptr`、`std::shared_ptr` 和 `std::weak_ptr` 的所有权语义。

## 栈：自动生命周期

函数内的普通局部变量通常具有自动存储期，离开作用域后自动销毁：

```cpp
void createLocalPlayer()
{
    int hp = 100;
    std::string name = "Alice";
    Player player(name, hp, 20);
} // hp、name、player 在这里离开作用域
```

当前阶段可以先记住：栈上对象不需要手动 `delete`，生命周期跟作用域绑定，创建和释放成本通常较低，但空间有限，不适合放很大的对象或不确定生命周期的资源。

## 堆：动态分配与手动释放

`new` 会在堆上创建对象，并返回指向该对象的指针：

```cpp
int* hp = new int(100);
std::string* name = new std::string("Alice");
Player* player = new Player("Alice", 100, 20);

delete hp;
delete name;
delete player;
```

这里 `hp`、`name`、`player` 这三个指针变量本身通常仍是局部变量；它们保存的是堆上对象的地址。离开作用域时，指针变量会消失，但它们指向的堆对象不会因为指针变量消失而自动释放。

## `new/delete` 必须匹配

单个对象和数组对象的释放方式不同：

```cpp
int* value = new int(10);
delete value;

int* values = new int[10];
delete[] values;
```

规则：

- `new` 对应 `delete`。
- `new[]` 对应 `delete[]`。
- 混用属于未定义行为，可能崩溃，也可能暂时看似正常但埋下内存错误。

## 内存泄漏示例

```cpp
void leakyFunction()
{
    int* data = new int[1000];
    // 忘记 delete[] data;
}
```

如果这个函数被循环调用，堆内存会持续增长。LeetCode 这类短生命周期判题中有些泄漏不容易被立刻观察到，但普通工程和游戏客户端长时间运行时，这类问题会变成稳定性风险。

常见风险：

| 风险 | 典型原因 | 后果 |
|---|---|---|
| 内存泄漏 | `new` 后忘记释放 | 内存持续增长，长期运行变慢或崩溃 |
| 重复释放 | 同一地址 `delete` 两次 | 未定义行为，常见表现是崩溃 |
| 悬空指针 | `delete` 后继续使用旧指针 | 访问已释放内存，结果不可预测 |
| 数组释放不匹配 | `new[]` 后用 `delete` | 未定义行为 |

## 当前使用建议

在入门阶段，先按这条优先级思考：

1. 生命周期清晰、对象不大：优先栈上对象。
2. 必须动态创建：先问“谁拥有它，谁负责释放”。
3. 普通工程中避免裸 `new/delete` 扩散，后续优先学习 RAII、`std::unique_ptr` 和 `std::shared_ptr`。

当前还不能把“会用智能指针”写成掌握，因为本次材料只是阅读和理解记录，尚未完成智能指针实验。

## 智能指针入门

> 证据归属：用户 2026-08-17 C++ 学习笔记和 `inbox/智能指针.png` 截图。以下内容是概念学习记录，尚未通过最小程序验证析构时机、引用计数变化或循环引用。

### `std::unique_ptr`：独占所有权

```cpp
auto weapon = std::make_unique<Weapon>();
weapon->Use();

// auto copy = weapon;              // 不允许拷贝
auto moved = std::move(weapon);     // 可以移动所有权
```

- 默认优先考虑 `unique_ptr`，因为所有权最清楚。
- 不能拷贝，避免两个对象同时认为自己拥有同一份资源。
- 可以通过 `std::move` 转移所有权；转移后原指针不应继续当作有效对象使用。

### `std::shared_ptr`：共享所有权

```cpp
auto texture = std::make_shared<Texture>();
auto alias = texture;
```

- 多个 `shared_ptr` 可以共同拥有同一对象。
- 内部使用引用计数；最后一个拥有者销毁或重置时，对象才会释放。
- 如果两个对象互相用 `shared_ptr` 持有，可能形成循环引用，导致引用计数无法归零。

### `std::weak_ptr`：观察但不拥有

```cpp
std::shared_ptr<Texture> texture = std::make_shared<Texture>();
std::weak_ptr<Texture> observer = texture;

if (auto locked = observer.lock())
{
    locked->Use();
}
```

- `weak_ptr` 不增加引用计数，适合观察 `shared_ptr` 管理的对象。
- 使用前要通过 `lock()` 临时提升成 `shared_ptr`，并检查对象是否仍存在。
- 常用于打破循环引用。

当前阶段只记录选择口诀：**独占用 `unique_ptr`，确实共享生命周期才用 `shared_ptr`，只观察共享对象时用 `weak_ptr`**。这还不是掌握，W34 仍需要补一个能运行的小程序来观察构造、析构和引用计数变化。

## 拷贝控制与浅拷贝风险

C++ 默认拷贝会逐字段复制对象。对普通值字段来说通常没问题，但如果类里保存裸指针，默认拷贝会让两个对象指向同一块堆内存：

```cpp
class Buffer
{
public:
    Buffer(int size)
        : size_(size), data_(new int[size])
    {
    }

    ~Buffer()
    {
        delete[] data_;
    }

private:
    int size_;
    int* data_;
};
```

如果直接写：

```cpp
Buffer a(10);
Buffer b = a;
```

默认拷贝会让 `a.data_` 和 `b.data_` 指向同一块数组。随后两个对象析构时都会 `delete[]` 同一块内存，可能导致重复释放；其中一个对象释放后，另一个对象的指针也会变成悬空指针。

解决方向有两类：

| 方向 | 含义 | 当前阶段记忆点 |
|---|---|---|
| 深拷贝 | 自己实现拷贝构造和拷贝赋值，分配新内存并复制内容 | 能练习底层所有权，但容易写错异常安全 |
| 禁止拷贝 / 使用 RAII 类型 | 用 `std::vector`、`std::unique_ptr` 等类型表达所有权 | 更符合现代 C++ 默认方向 |

入门阶段可以先记住：**只要类直接拥有裸指针资源，就不能无脑依赖默认拷贝**。后续学习拷贝构造、拷贝赋值、移动语义和智能指针时，再把这条规则展开成 Rule of Three / Five / Zero。

## 待验证

后续至少补一个：

- 写一个小程序，观察栈上对象和堆上对象的构造 / 析构输出时机。
- 使用 `new[]/delete[]` 写数组分配示例，并记录匹配规则。
- 用 `std::unique_ptr` 改写一个裸指针示例，验证离开作用域自动释放。
- 记录一次真实悬空指针、重复释放或内存泄漏的排查过程。
- 写一个含裸指针成员的最小类，解释默认浅拷贝为什么会带来重复释放风险；如果实际运行，必须在安全环境中完成并记录结果。
