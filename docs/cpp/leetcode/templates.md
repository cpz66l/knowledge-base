# C++ 刷题模板与易错点

> 目标是用标准、稳定、容易解释的 C++ 写算法题，而不是堆缩写或竞赛宏。

---

## 常用头文件

```cpp
#include <algorithm>
#include <array>
#include <climits>
#include <functional>
#include <limits>
#include <numeric>
#include <queue>
#include <stack>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>
```

`#include <bits/stdc++.h>` 在部分在线评测的 GCC 环境可用，但它不是 C++ 标准头文件。面试或工程代码建议包含实际需要的头文件。

---

## 容器初始化

```cpp
using Graph = std::vector<std::vector<int>>;

std::vector<int> values(n, 0);
std::vector<std::vector<int>> grid(rows, std::vector<int>(cols, 0));
std::unordered_map<int, int> frequency;
std::unordered_set<int> visited;
std::queue<int> bfs;
std::stack<int> dfs;
```

不要使用 `#define int long long`，它会改变接口、重载解析和标准库代码的含义。

---

## 排序与比较器

```cpp
std::sort(values.begin(), values.end());

std::sort(intervals.begin(), intervals.end(),
          [](const auto& a, const auto& b) {
              if (a[0] != b[0]) return a[0] < b[0];
              return a[1] < b[1];
          });
```

比较器应表达严格弱序。不要写 `a <= b`，否则排序行为未定义。

---

## 最小堆

`std::priority_queue` 默认是最大堆：

```cpp
std::priority_queue<int> max_heap;

std::priority_queue<int,
                    std::vector<int>,
                    std::greater<int>> min_heap;
```

存储 pair 时，默认按 first、second 的字典序比较。

---

## 二分查找

```cpp
auto first_not_less = std::lower_bound(values.begin(), values.end(), target);
auto first_greater = std::upper_bound(values.begin(), values.end(), target);

int index = static_cast<int>(first_not_less - values.begin());
```

手写二分时先明确搜索区间是 `[left, right]` 还是 `[left, right)`，循环条件和边界更新必须保持同一套不变量。

---

## DFS / BFS

```cpp
void dfs(int node,
         const Graph& graph,
         std::vector<char>& visited) {
    if (visited[node]) return;
    visited[node] = true;

    for (int next : graph[node]) {
        dfs(next, graph, visited);
    }
}
```

深图可能导致递归栈溢出，必要时改用显式 `std::stack`。BFS 通常在入队时标记访问，避免同一节点被重复入队。

---

## 数值与溢出

```cpp
long long product = 1LL * a * b;
constexpr int inf = std::numeric_limits<int>::max();
int middle = left + (right - left) / 2;
```

- 两个 `int` 相乘后再赋给 `long long` 仍可能先溢出
- 无符号 `size_t` 做倒序循环时容易下溢
- 空容器上计算 `size() - 1` 会产生无符号下溢

---

## 传参与返回值

```cpp
int solve(const std::vector<int>& values);       // 只读借用，不拷贝
void sort_in_place(std::vector<int>& values);    // 修改调用者数据
std::vector<int> build_result();                 // 按值返回，可做返回值优化/移动
```

- 不返回局部变量的指针、引用或 `string_view`
- 不为小型标量参数滥用 `const int&`
- 容器扩容后不要继续使用旧引用或迭代器

---

## 提交前检查

- 空数组、单元素、全相同、已排序、逆序是否覆盖？
- `int` 是否可能溢出？
- 下标是否越界？
- 比较器是否满足严格弱序？
- 时间复杂度和空间复杂度能否清楚说明？
- 使用的是标准 C++，还是某个评测环境专属扩展？

---

> 📎 标签：`C++` `LeetCode` `刷题模板` `STL` `面试`
