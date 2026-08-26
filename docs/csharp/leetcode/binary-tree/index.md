# 二叉树

> DFS/BFS · 前中后序 · 层序 — 递归思维的试金石

---

## 题目列表

| 题目 | 难度 | 核心技巧 |
|---|---|---|
| [二叉树的中序遍历](binary-tree-inorder-traversal.md) | Easy | 递归、显式栈、前/中/后序遍历迁移 |
| [对称二叉树](symmetric-tree.md) | Easy | 镜像递归、成对队列比较 |
| [验证二叉搜索树](validate-binary-search-tree.md) | Medium | 递归上下界、中序严格递增、`long` 边界 |
| [二叉树的最大深度](maximum-depth-of-binary-tree.md) | Easy | DFS 递归高度、BFS 层序计数 |
| [二叉树的层序遍历](binary-tree-level-order-traversal.md) | Medium | BFS 层序、固定层大小、队列 |
| [翻转二叉树](invert-binary-tree.md) | Easy | 递归交换左右子树、镜像思维 |
| [二叉树的直径](diameter-of-binary-tree.md) | Easy | DFS 返回深度、全局答案记录最长路径 |
| [将有序数组转换为二叉搜索树](convert-sorted-array-to-binary-search-tree.md) | Easy | 有序数组中点建树、递归分治、平衡 BST |

---

## 核心技巧

- 前 / 中 / 后序遍历（递归 + 迭代）
- 层序遍历（BFS + Queue）
- 有序数据递归建树（中点分治）
- BST 验证：上下界递归 / 中序严格递增
- 递归三部曲：终止条件 -> 单层逻辑 -> 返回值
- 显式栈模拟系统调用栈
- 自顶向下 vs 自底向上
- 递归返回值 vs 全局答案

---

> 标签：`二叉树` `DFS` `BFS` `递归` `栈`
