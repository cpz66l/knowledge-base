# C++ 刷题语言笔记

> 状态：持续练习中。本页只沉淀 C++ 容器、指针、语法和实现习惯；具体题解统一进入双语题解区。

## 使用方式

- 每日题目分别用 C# 与 C++ 独立实现，再合并到同一个权威题解页面。
- 本页记录跨题目复用的 C++ 容器选择、指针写法、标准库用法和常见编译错误。
- 题目思路、复杂度和边界条件写入[LeetCode 双语题解](../../csharp/leetcode/index.md)，不在这里重复正文。

## 题型路径

| 顺序 | 分类 | 状态 |
|---|---|---|
| 1 | 数组、哈希、双指针、滑动窗口 | 部分练习 |
| 2 | 链表、栈、队列、二叉树 | 已开始：LC 2、LC 19、LC 21、LC 24、LC 142 |
| 3 | 二分、堆、贪心、回溯 | 待学习 |
| 4 | 图论、动态规划、多维动态规划 | 待学习 |
| 5 | 综合技巧与错题复盘 | 持续进行 |

题型顺序保留在本页作为 C++ 练习规划；新增题目时更新对应的双语题解页面。

## 当前记录

- 已形成双语对照：[LC 2 两数相加](../../csharp/leetcode/linked-list/add-two-numbers.md)、[LC 19 删除链表的倒数第 N 个结点](../../csharp/leetcode/linked-list/remove-nth-node-from-end-of-list.md)、[LC 21 合并两个有序链表](../../csharp/leetcode/linked-list/merge-two-sorted-lists.md)、[LC 24 两两交换链表中的节点](../../csharp/leetcode/linked-list/swap-nodes-in-pairs.md)、[LC 142 环形链表 II](../../csharp/leetcode/linked-list/linked-list-cycle-ii.md)
- 当前双语对照数量：5
- 已练习题型：链表、哨兵节点、逐位加法与进位、递归、哈希集合、快慢指针、栈、相邻节点重连
- 本次语言复盘：C++ 临时哨兵节点优先放在栈上；相邻节点交换需要先保存 `first` 和 `second`，再按顺序重连，避免后续链表断开
- 下一道题：待填写

持续沉淀入口：[C++ 刷题模板与易错点](templates.md)。
