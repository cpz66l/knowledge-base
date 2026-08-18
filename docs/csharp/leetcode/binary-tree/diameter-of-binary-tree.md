# 二叉树的直径

> [LeetCode 543. Diameter of Binary Tree](https://leetcode.cn/problems/diameter-of-binary-tree/) - Easy
>
> 学习状态：已完成 C++ 练习
>
> 练习日期：2026-08-16
>
> 本次实现：C++，DFS 返回深度并顺手更新全局最大直径
>
> 验证状态：用户放入知识库前已完成练习；本次整理未重复运行 LeetCode 判题
>
> 证据归属：用户 `inbox/8月16号leetcode.txt` 原始记录

## 学习目标

- 理解“直径”是任意两个节点之间最长路径的边数，不一定经过根节点。
- 复用 [LC104 二叉树的最大深度](maximum-depth-of-binary-tree.md) 的 DFS 高度思路。
- 掌握二叉树题中“递归返回值”和“全局答案”分离的套路。

## 题意与核心思路

对任意节点来说，如果最长路径经过它，那么路径长度取决于它的左子树深度和右子树深度：

```text
经过当前节点的节点数 = leftDepth + rightDepth + 1
经过当前节点的边数 = leftDepth + rightDepth
```

递归函数 `depth(node)` 仍然返回“以当前节点为根的最大深度”。同时在每个节点处更新一次全局答案，记录目前见过的最大路径。

## 方法：DFS 返回深度

```cpp
class Solution
{
public:
    int diameterOfBinaryTree(TreeNode* root)
    {
        maxNodeCount_ = 1;
        depth(root);
        return maxNodeCount_ - 1;
    }

private:
    int maxNodeCount_ = 1;

    int depth(TreeNode* root)
    {
        if (root == nullptr)
        {
            return 0;
        }

        int leftDepth = depth(root->left);
        int rightDepth = depth(root->right);

        maxNodeCount_ = std::max(maxNodeCount_, leftDepth + rightDepth + 1);
        return std::max(leftDepth, rightDepth) + 1;
    }
};
```

这里 `depth()` 的返回值服务父节点计算高度；`maxNodeCount_` 记录全树范围内的最佳答案。两者不要混成一个返回值，否则容易只算出根节点路径，而漏掉“不经过根”的最长路径。

如果直接记录边数，也可以把更新写成 `answer = max(answer, leftDepth + rightDepth)`，最后不需要再减 1。

## 复杂度

| 方法 | 时间 | 辅助空间 | 说明 |
|---|---:|---:|---|
| DFS | O(n) | O(h) | n 是节点数，h 是树高；每个节点只访问一次 |

## 常见错误

- 把直径理解成根到叶子的最长路径，漏掉“不经过根”的情况。
- 忘记题目要求返回边数，而不是节点数。
- 只返回 `max(leftDepth, rightDepth) + 1`，没有在每个节点更新全局答案。
- 全局变量没有在入口函数中初始化，导致多组测试之间状态残留。

## 如何验证

至少覆盖：

- 空树或单节点：直径为 `0`。
- 普通树：`[1,2,3,4,5] -> 3`。
- 退化链表：长度为 n 的单链树，直径为 `n - 1`。
- 最长路径完全在某一侧子树内部，不经过根节点。

本次整理遵循 LeetCode Inbox 规则：用户主动放入题解默认视为放入前已完成练习；当前智能体没有重新创建 C++ 工程或提交 LeetCode 复测。

## 相关内容

- 专题：[二叉树](index.md)
- 前置题：[二叉树的最大深度](maximum-depth-of-binary-tree.md)
- C++：[刷题模板与易错点](../../../cpp/leetcode/templates.md)

> 标签：`二叉树` `DFS` `递归` `最大深度` `C++`

