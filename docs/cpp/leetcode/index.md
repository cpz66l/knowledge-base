# C++ 刷题语言笔记

> 状态：学习中。本页只沉淀 C++ 容器、指针、语法和实现习惯；具体题解统一进入双语题解区。

## 使用方式

- 后续算法题优先用 C++ 实现；C# 主要通过 Unity / 项目工程训练。若同一道题后续补充 C# 或 C++，仍合并到同一个权威题解页面。
- 本页记录跨题目复用的 C++ 容器选择、指针写法、标准库用法和常见编译错误。
- 题目思路、复杂度和边界条件写入[LeetCode 双语题解](../../csharp/leetcode/index.md)，不在这里重复正文。

## 题型路径

| 顺序 | 分类 | 状态 |
|---|---|---|
| 1 | 数组、哈希、双指针、滑动窗口 | 部分练习 |
| 2 | 链表、栈、队列、二叉树 | 已开始：LC 2、LC 19、LC 21、LC 24、LC 94、LC 101、LC 102、LC 104、LC 108、LC 138、LC 142、LC 148、LC 226、LC 543 |
| 3 | 二分、堆、贪心、回溯 | 未开始 |
| 4 | 图论、动态规划、多维动态规划 | 未开始 |
| 5 | 综合技巧与错题复盘 | 持续进行 |

题型顺序保留在本页作为 C++ 练习规划；新增题目时更新对应的双语题解页面。

## 当前记录

- 已形成双语对照：[LC 2 两数相加](../../csharp/leetcode/linked-list/add-two-numbers.md)、[LC 19 删除链表的倒数第 N 个结点](../../csharp/leetcode/linked-list/remove-nth-node-from-end-of-list.md)、[LC 21 合并两个有序链表](../../csharp/leetcode/linked-list/merge-two-sorted-lists.md)、[LC 24 两两交换链表中的节点](../../csharp/leetcode/linked-list/swap-nodes-in-pairs.md)、[LC 142 环形链表 II](../../csharp/leetcode/linked-list/linked-list-cycle-ii.md)
- 当前双语对照数量：5
- C++ 单语言新增练习：[LC 94 二叉树的中序遍历](../../csharp/leetcode/binary-tree/binary-tree-inorder-traversal.md)、[LC 101 对称二叉树](../../csharp/leetcode/binary-tree/symmetric-tree.md)、[LC 102 二叉树的层序遍历](../../csharp/leetcode/binary-tree/binary-tree-level-order-traversal.md)、[LC 104 二叉树的最大深度](../../csharp/leetcode/binary-tree/maximum-depth-of-binary-tree.md)、[LC 108 将有序数组转换为二叉搜索树](../../csharp/leetcode/binary-tree/convert-sorted-array-to-binary-search-tree.md)、[LC 138 复制带随机指针的链表](../../csharp/leetcode/linked-list/copy-list-with-random-pointer.md)、[LC 148 排序链表](../../csharp/leetcode/linked-list/sort-list.md)、[LC 226 翻转二叉树](../../csharp/leetcode/binary-tree/invert-binary-tree.md)、[LC 543 二叉树的直径](../../csharp/leetcode/binary-tree/diameter-of-binary-tree.md)
- 已练习题型：链表、哨兵节点、逐位加法与进位、递归、哈希集合、快慢指针、栈、队列、相邻节点重连、随机指针深拷贝、归并排序、二叉树 DFS / BFS、镜像递归、成对节点比较、树高与全局答案、层序结果分组、递归建树
- 本次语言复盘：随机链表深拷贝中 `node->random->next` 才是对应新节点；链表排序中每轮找最小节点会退化到 O(n²)，应改用归并排序；递归辅助函数需要用 `vector<int>&` 承接结果，避免写入副本；二叉树层序题需要先固定当前层 `queue.size()` 再处理该层节点，并先给外层结果 `push_back` 当前层数组；对称二叉树要让左右指针镜像移动，翻转二叉树要避免覆盖一侧子树；二叉树直径要区分“返回给父节点的深度”和“全树最大答案”；有序数组建 BST 要用中点切分并注意 LeetCode 中 `new TreeNode` 的节点释放责任由判题环境接管
- 下一道题：继续优先用 C++ 刷链表 / 栈 / 二叉树基础题，C# 练习主要放回 Unity 项目工程

持续沉淀入口：[C++ 刷题模板与易错点](templates.md)。
