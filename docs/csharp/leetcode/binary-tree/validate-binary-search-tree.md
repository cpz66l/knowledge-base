# 验证二叉搜索树

> [LeetCode 98. Validate Binary Search Tree](https://leetcode.cn/problems/validate-binary-search-tree/) - Medium
>
> 学习状态：已完成 C++ 练习
>
> 练习日期：2026-08-19
>
> 本次实现：C++，递归上下界 / 中序遍历
>
> 验证状态：用户放入知识库前已完成练习；本次整理未重复运行 LeetCode 判题
>
> 证据归属：用户 `inbox/8月19日Leetcode.txt` 原始记录

## 学习目标

- 理解 BST 不是只要求“当前节点大于左孩子、小于右孩子”，而是整棵左子树都必须小于当前节点，整棵右子树都必须大于当前节点。
- 掌握递归上下界写法：每向下一层递归，都收窄当前节点允许的数值范围。
- 掌握中序遍历写法：合法 BST 的中序序列必须严格递增。

## 题意与核心思路

有效二叉搜索树要求：

```text
左子树所有节点 < root.val
右子树所有节点 > root.val
左右子树本身也都是有效 BST
```

因此不能只比较直接左右孩子。比如右子树里某个更深的节点如果小于根，也会破坏整棵树的 BST 性质。

## 方法一：递归上下界

```cpp
class Solution
{
public:
    bool isValidBST(TreeNode* root)
    {
        return IsValid(root, LONG_MIN, LONG_MAX);
    }

private:
    bool IsValid(TreeNode* root, long lower, long upper)
    {
        if (root == nullptr)
        {
            return true;
        }

        if (root->val <= lower || root->val >= upper)
        {
            return false;
        }

        return IsValid(root->left, lower, root->val)
            && IsValid(root->right, root->val, upper);
    }
};
```

每个节点都有一个允许区间 `(lower, upper)`。进入左子树时，上界变成当前节点值；进入右子树时，下界变成当前节点值。

这里边界使用 `long` 而不是 `int`，是为了覆盖节点值等于 `INT_MIN` 或 `INT_MAX` 的用例。如果用 `int` 保存上下界，哨兵边界和真实节点值可能冲突。

## 方法二：中序遍历

```cpp
class Solution
{
public:
    bool isValidBST(TreeNode* root)
    {
        std::stack<TreeNode*> stack;
        long previous = LONG_MIN;
        TreeNode* current = root;

        while (!stack.empty() || current != nullptr)
        {
            while (current != nullptr)
            {
                stack.push(current);
                current = current->left;
            }

            current = stack.top();
            stack.pop();

            if (current->val <= previous)
            {
                return false;
            }

            previous = current->val;
            current = current->right;
        }

        return true;
    }
};
```

合法 BST 的中序遍历结果是严格升序。遍历时只需要保存上一个访问值，发现当前值 `<= previous` 就说明不合法。

用户本次记录的错点：入栈顺序应是“先 push 当前非空节点，再走向左子树”。如果先把指针移到右子树或空位置再 push，后续可能把空指针压栈，导致访问 `cur->val` 时出错。

## 复杂度

| 方法 | 时间 | 辅助空间 | 说明 |
|---|---:|---:|---|
| 递归上下界 | O(n) | O(h) | h 是树高，最坏 O(n) |
| 中序遍历 | O(n) | O(h) | 显式栈保存一路左链 |

## 常见错误

- 只比较当前节点和直接左右孩子，漏掉深层节点越界。
- 上下界使用 `int`，遇到 `INT_MIN / INT_MAX` 边界用例时误判。
- BST 要求严格小于 / 严格大于，重复值应判 false。
- 中序遍历时把空指针压入栈，后续访问成员导致错误。
- 中序比较忘记更新 `previous`。

## 如何验证

至少覆盖：

- 合法普通树：`[2,1,3] -> true`。
- 深层越界：`[5,1,4,null,null,3,6] -> false`。
- 重复值：`[2,2,2] -> false`。
- 边界值：节点值包含 `INT_MIN` 或 `INT_MAX`。
- 单节点和空树。

本次整理遵循 LeetCode Inbox 规则：用户主动放入题解默认视为放入前已完成练习；当前智能体没有重新创建 C++ 工程或提交 LeetCode 复测。

## 相关内容

- 专题：[二叉树](index.md)
- 前置题：[二叉树的中序遍历](binary-tree-inorder-traversal.md)
- C++：[刷题模板与易错点](../../../cpp/leetcode/templates.md)

> 标签：`二叉树` `BST` `DFS` `中序遍历` `C++`

