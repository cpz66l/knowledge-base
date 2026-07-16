# LeetCode 算法

> C++ 实现 — 与 C# 板块同步刷题，熟悉 C++ 代码风格与 STL 运用

---

## 为什么用 C++ 刷题？

- 大厂面试（腾讯、网易、米哈游）的算法题主流语言是 C++
- 刷题过程熟悉 C++ 语法、STL 容器、迭代器 —— 一举两得
- 与 [C# LeetCode](../../csharp/leetcode/index.md) 板块对照学习，理解两种语言的表达差异

---

## 题目分类导航

| 分类 | 核心技巧 | 状态 |
|------|----------|------|
| 哈希 | `unordered_map` / `unordered_set`、查找优化 | 📋 待开始 |
| 双指针 | 快慢指针、左右对撞、`std::two_pointer` 思想 | 📋 待开始 |
| 滑动窗口 | 窗口伸缩、`deque` 单调队列 | 📋 待开始 |
| 子串 | 前缀和、KMP、子串问题套路 | 📋 待开始 |
| 数组 | 遍历、原地操作、前缀后缀 | 📋 待开始 |
| 矩阵 | 二维遍历、方向数组、旋转 | 📋 待开始 |
| 链表 | 反转、合并、环检测、`nullptr` | 📋 待开始 |
| 二叉树 | DFS/BFS、前中后序、`std::queue` 层序 | 📋 待开始 |
| 图论 | BFS/DFS、拓扑排序、并查集 | 📋 待开始 |
| 回溯 | 排列组合、子集、剪枝、`std::vector` 路径 | 📋 待开始 |
| 二分查找 | `std::lower_bound` 与手动实现、边界条件 | 📋 待开始 |
| 栈 | `std::stack`、单调栈、括号匹配 | 📋 待开始 |
| 堆 | `std::priority_queue`、TopK、多路归并 | 📋 待开始 |
| 贪心算法 | 区间调度、跳跃游戏 | 📋 待开始 |
| 动态规划 | 一维 DP、背包、`std::vector<int> dp` | 📋 待开始 |
| 多维动态规划 | 二维 DP、路径问题、编辑距离 | 📋 待开始 |
| 技巧 | 位运算、前缀和、差分、摩尔投票 | 📋 待开始 |

---

## 刷题记录

> 📊 进度追踪

| 难度 | 已完成 | 目标 |
|------|--------|------|
| Easy | 0 | — |
| Medium | 0 | — |
| Hard | 0 | — |

---

## C++ vs C# 刷题速查

| 场景 | C# | C++ |
|------|-----|-----|
| 哈希表 | `Dictionary<K,V>` | `std::unordered_map<K,V>` |
| 哈希集 | `HashSet<T>` | `std::unordered_set<T>` |
| 动态数组 | `List<T>` | `std::vector<T>` |
| 栈 | `Stack<T>` | `std::stack<T>` |
| 队列 | `Queue<T>` | `std::queue<T>` |
| 优先队列 | `PriorityQueue<T,TP>` | `std::priority_queue<T>` |
| 排序 | `Array.Sort()` | `std::sort()` |
| 空引用 | `null` | `nullptr` |
| 最大值 | `int.MaxValue` | `INT_MAX` / `std::numeric_limits<int>::max()` |

---

> 💡 每道题记录：题目链接、核心思路、**C++ 代码**、时空复杂度分析。
> 
> 📎 标签：`C++` `LeetCode` `算法` `STL`
