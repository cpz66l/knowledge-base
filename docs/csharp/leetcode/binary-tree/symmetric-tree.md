# 对称二叉树

> [LeetCode 101. Symmetric Tree](https://leetcode.cn/problems/symmetric-tree/) - Easy
>
> 学习状态：已完成 C++ 练习
>
> 练习日期：2026-08-15
>
> 本次实现：C++，递归镜像判断 / 队列迭代判断
>
> 验证状态：用户放入知识库前已完成练习；本次整理未重复运行 LeetCode 判题
>
> 证据归属：用户 `inbox/8月15号leetcode.txt` 原始记录

## 学习目标

- 理解对称二叉树的判断不是比较左右子树是否完全相同，而是比较是否互为镜像。
- 掌握两个指针同步向相反方向移动的递归写法。
- 用队列保存成对节点，练习二叉树迭代比较。

## 题意与核心思路

一棵树对称，意味着它的左子树和右子树互为镜像。两个节点 `left` 和 `right` 互为镜像需要同时满足：

- 两个节点都为空，或者两个节点都非空且值相同。
- `left->left` 与 `right->right` 镜像。
- `left->right` 与 `right->left` 镜像。

## 方法一：递归镜像判断

```cpp
class Solution
{
public:
    bool isSymmetric(TreeNode* root)
    {
        if (root == nullptr)
        {
            return true;
        }

        return isMirror(root->left, root->right);
    }

private:
    bool isMirror(TreeNode* left, TreeNode* right)
    {
        if (left == nullptr && right == nullptr)
        {
            return true;
        }

        if (left == nullptr || right == nullptr)
        {
            return false;
        }

        return left->val == right->val
            && isMirror(left->left, right->right)
            && isMirror(left->right, right->left);
    }
};
```

递归时两个指针不是同向移动，而是镜像移动：一个去左边，另一个就去右边。

## 方法二：队列迭代判断

```cpp
class Solution
{
public:
    bool isSymmetric(TreeNode* root)
    {
        if (root == nullptr)
        {
            return true;
        }

        std::queue<TreeNode*> queue;
        queue.push(root->left);
        queue.push(root->right);

        while (!queue.empty())
        {
            TreeNode* left = queue.front();
            queue.pop();
            TreeNode* right = queue.front();
            queue.pop();

            if (left == nullptr && right == nullptr)
            {
                continue;
            }

            if (left == nullptr || right == nullptr || left->val != right->val)
            {
                return false;
            }

            queue.push(left->left);
            queue.push(right->right);
            queue.push(left->right);
            queue.push(right->left);
        }

        return true;
    }
};
```

队列里始终按“两两一组”的方式保存待比较节点。入队顺序必须成镜像：外侧一组 `left->left / right->right`，内侧一组 `left->right / right->left`。

## 复杂度

| 方法 | 时间 | 辅助空间 | 说明 |
|---|---:|---:|---|
| 递归 | O(n) | O(h) | h 是树高，递归栈最坏 O(n) |
| 队列迭代 | O(n) | O(w) | w 是树的最大宽度，队列保存成对节点 |

## 常见错误

- 递归时写成 `left->left` 对 `right->left`，把镜像比较写成同向比较。
- 只比较节点值，没有继续比较子树结构。
- 队列写法中遇到两个空节点没有 `continue`，后面继续访问空指针。
- 队列入队顺序不成对，导致后续比较的两个节点不是镜像位置。

## 如何验证

至少覆盖：

- 对称树：`[1,2,2,3,4,4,3] -> true`。
- 值相同但结构不对称：`[1,2,2,null,3,null,3] -> false`。
- 单节点：`[1] -> true`。
- 左右一边为空、一边非空的最小反例。

本次整理遵循 LeetCode Inbox 规则：用户主动放入题解默认视为放入前已完成练习；当前智能体没有重新创建 C++ 工程或提交 LeetCode 复测。

## 相关内容

- 专题：[二叉树](index.md)
- C++：[刷题模板与易错点](../../../cpp/leetcode/templates.md)

> 标签：`二叉树` `DFS` `BFS` `递归` `队列` `镜像` `C++`

