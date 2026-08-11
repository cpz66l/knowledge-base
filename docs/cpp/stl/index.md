# STL 标准库

> 状态：学习中。刷题和语法笔记中接触到的容器先单独记录，之后再系统整理。

## 计划学习内容

- vector、string、array
- map、set、unordered_map、unordered_set
- stack、queue、deque、priority_queue
- 迭代器和范围访问
- 标准算法与比较器
- 容器选择、复杂度和迭代器失效

## 最小产出

- 用三种常用容器完成小练习
- 记录一次容器选择理由
- 记录一次迭代器或引用失效问题

## 当前记录

- 已接触：`vector`、`string`、`unordered_map`、`stack`
- 系统掌握：未完成，仍需用题目和小程序验证
- 待补内容：迭代器失效、容器复杂度、`map` / `set`、`queue`、`priority_queue`

## 2026-08-10/11 容器笔记

> 证据归属：用户 C++ 学习笔记和 LeetCode 练习。以下是当前可复用用法，不代表已经系统掌握 STL。

### `std::vector`

```cpp
std::vector<int> scores;
std::vector<int> nums = {1, 2, 3, 4, 5};
std::vector<std::string> names(5, "未命名");
```

常用操作：

| 操作 | 说明 |
|---|---|
| `push_back(value)` | 尾部添加 |
| `pop_back()` | 尾部删除 |
| `erase(vec.begin() + i)` | 删除指定迭代器位置 |
| `clear()` | 清空 |
| `operator[]` | 下标访问，不检查越界 |
| `at(i)` | 下标访问，会做越界检查并可能抛异常 |
| `size()` | 元素数量，返回 `size_t` |
| `empty()` | 判断是否为空 |

遍历方式：

```cpp
for (int i = 0; i < static_cast<int>(nums.size()); i++)
{
    std::cout << nums[i];
}

for (int n : nums)
{
    std::cout << n;
}

for (auto iter = nums.begin(); iter != nums.end(); ++iter)
{
    std::cout << *iter;
}
```

注意点：

- `size()` 返回无符号的 `size_t`，和 `int` 比较时容易出现警告或隐藏问题。
- `push_back` 可能触发扩容，扩容本质是换一块更大的连续内存，旧迭代器、引用或指针可能失效。
- 大对象遍历优先用 `const auto&`，避免拷贝。

### `std::string`

```cpp
std::string s1 = "Hello";
std::string s2("World");
std::string s3(5, '*'); // "*****"
```

常用操作：

| 操作 | 说明 |
|---|---|
| `+` / `append` | 拼接字符串 |
| `size()` / `length()` | 字符长度 |
| `substr(pos, len)` | 从 `pos` 开始取 `len` 个字符 |
| `find(pattern)` | 查找子串，找不到返回 `std::string::npos` |
| `std::to_string(value)` | 数值转字符串 |
| `std::stoi(s)` / `std::stof(s)` | 字符串转数值 |
| `std::getline(std::cin, s)` | 读取整行，包含空格 |

易错点：

- `substr(0, 5)` 是从下标 0 开始取 5 个字符，不是取到下标 5。
- `std::string::npos` 常用于判断 `find` 是否失败。
- `s[s.size() - 1]` 前要确保字符串非空。
