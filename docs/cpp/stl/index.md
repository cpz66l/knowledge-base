# STL 标准库

> 容器、算法、迭代器 —— C++ 面试与开发的核心工具

!!! tip "C# → C++ 速查"
    C# 有 LINQ + `List<T>` + `Dictionary<K,V>` 一条龙；C++ 的 STL 用迭代器串起容器和算法。核心转变：从"调用对象的方法"到"传迭代器给算法"。

---

## STL 六大组件

```
┌─────────────────────────────────────────────┐
│  容器 Containers                            │
│  vector / list / map / set / unordered_map  │
├─────────────────────────────────────────────┤
│  算法 Algorithms                            │
│  sort / find / binary_search / for_each     │
├─────────────────────────────────────────────┤
│  迭代器 Iterators                           │
│  begin() / end() / ++ / -- / *             │
├─────────────────────────────────────────────┤
│  适配器 Adapters                            │
│  stack / queue / priority_queue             │
├─────────────────────────────────────────────┤
│  仿函数 Functors                            │
│  less<T> / greater<T> / 自定义比较器        │
├─────────────────────────────────────────────┤
│  分配器 Allocators                          │
│  std::allocator<T>（可自定义）               │
└─────────────────────────────────────────────┘
```

---

## 常用容器速查

### 序列容器

| 容器 | 底层结构 | 随机访问 | 头插入 | 尾插入 | 特点 |
|------|----------|----------|--------|--------|------|
| `vector<T>` | 动态数组 | O(1) | O(n) | O(1)* | 最常用，缓存友好 |
| `deque<T>` | 分段数组 | O(1) | O(1) | O(1) | 双端队列 |
| `list<T>` | 双向链表 | — | O(1) | O(1) | 插入/删除不使迭代器失效 |

\* `vector::push_back` 均摊 O(1)，扩容时 O(n)

### 关联容器

| 容器 | 底层 | 查找 | 插入 | 有序 | 重复 key |
|------|------|------|------|------|----------|
| `set<T>` | 红黑树 | O(log n) | O(log n) | ✅ | ❌ |
| `map<K,V>` | 红黑树 | O(log n) | O(log n) | ✅ | ❌ |
| `multiset<T>` | 红黑树 | O(log n) | O(log n) | ✅ | ✅ |
| `multimap<K,V>` | 红黑树 | O(log n) | O(log n) | ✅ | ✅ |
| `unordered_set<T>` | 哈希表 | O(1) 平均 | O(1) 平均 | ❌ | ❌ |
| `unordered_map<K,V>` | 哈希表 | O(1) 平均 | O(1) 平均 | ❌ | ❌ |

### 关键对比

| 场景 | 选这个 | 别选那个 |
|------|--------|----------|
| 动态数组 | `vector` | `list`（CPU 缓存差 10x） |
| 键值查找 | `unordered_map` | `map`（除非需要有序遍历） |
| 大量头尾操作 | `deque` | `list` |
| 迭代器稳定性 | `list` | `vector`（扩容使所有迭代器失效） |

---

## 常用算法速查

```cpp
#include <algorithm>

// 排序
std::sort(v.begin(), v.end());                              // 升序 O(n log n)
std::sort(v.begin(), v.end(), std::greater<int>());         // 降序
std::sort(v.begin(), v.end(), [](int a, int b) {           // 自定义比较
    return abs(a) < abs(b);
});

// 查找
auto it = std::find(v.begin(), v.end(), target);            // 线性查找
bool b = std::binary_search(v.begin(), v.end(), target);    // 二分（必须有序）
auto lo = std::lower_bound(v.begin(), v.end(), target);    // 第一个 >= target
auto hi = std::upper_bound(v.begin(), v.end(), target);    // 第一个 > target

// 遍历
std::for_each(v.begin(), v.end(), [](int x) { cout << x; });

// 变换
std::transform(v.begin(), v.end(), result.begin(),
               [](int x) { return x * 2; });

// 计数
int n = std::count(v.begin(), v.end(), target);
int n2 = std::count_if(v.begin(), v.end(), [](int x) { return x > 10; });

// 去重（需先排序）
std::sort(v.begin(), v.end());
auto last = std::unique(v.begin(), v.end());
v.erase(last, v.end());
```

---

## C# → C++ 常用对照

| 操作 | C# | C++ |
|------|-----|-----|
| 创建动态数组 | `new List<int>()` | `std::vector<int> v;` |
| 添加元素 | `list.Add(x)` | `v.push_back(x)` 或 `v.emplace_back(args)` |
| 获取大小 | `list.Count` | `v.size()` |
| 判空 | `list.Count == 0` | `v.empty()` |
| 尾部取/删 | `list[^1]` | `v.back()` / `v.pop_back()` |
| 清空 | `list.Clear()` | `v.clear()` |
| 找元素 | `list.IndexOf(x)` | `std::find(v.begin(), v.end(), x)` |
| 排序 | `list.Sort()` | `std::sort(v.begin(), v.end())` |
| 反转 | `list.Reverse()` | `std::reverse(v.begin(), v.end())` |
| 截取 | `list.GetRange(i, n)` | `vector<T>(v.begin()+i, v.begin()+i+n)` |

!!! tip "`push_back` vs `emplace_back`"
    `push_back(obj)` 先构造临时对象再拷贝/移动到容器中；`emplace_back(args...)` 直接在容器内部原地构造，省掉一次临时对象。**能用 `emplace_back` 就用它。**

---

## 待填充内容

> 📝 随学习进度逐步添加：
>
> - 迭代器深入（`iterator_traits`、迭代器失效规则）
> - 自定义比较器实战
> - `std::string` 与 `std::string_view`
> - `std::optional`、`std::variant`（C++17）
> - 多线程容器与 `std::atomic`

---

> 📎 标签：`C++` `STL` `容器` `算法` `迭代器`
