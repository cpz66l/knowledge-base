# 二叉树的中序遍历

> [LeetCode 94. Binary Tree Inorder Traversal](https://leetcode.cn/problems/binary-tree-inorder-traversal/) - Easy
>
> 学习状态：已完成 C++ 练习
>
> 练习日期：2026-08-11
>
> 本次实现：C++，递归 / 迭代栈；并复盘前序、后序迁移写法
>
> 验证状态：用户放入知识库前已完成练习；本次整理未重复运行 LeetCode 判题
>
> 证据归属：用户 `inbox/8月11号leetcode.txt` 原始记录

## 学习目标

- 掌握二叉树中序遍历顺序：左 -> 中 -> 右。
- 理解递归写法中 `vector<int>&` 为什么必须用引用传参。
- 用显式 `stack<TreeNode*>` 模拟递归调用栈。
- 从中序遍历迁移到前序和后序迭代写法。

## 题意与核心思路

中序遍历的访问顺序是：

```text
inorder(left)
visit(root)
inorder(right)
```

对二叉搜索树来说，中序遍历会得到升序序列；但本题只要求普通二叉树遍历，不要求树满足 BST 性质。

## 方法一：递归

```cpp
class Solution
{
public:
    std::vector<int> inorderTraversal(TreeNode* root)
    {
        std::vector<int> result;
        inorder(root, result);
        return result;
    }

private:
    void inorder(TreeNode* root, std::vector<int>& result)
    {
        if (root == nullptr)
        {
            return;
        }

        inorder(root->left, result);
        result.push_back(root->val);
        inorder(root->right, result);
    }
};
```

原始错点：如果写成 `void inorder(TreeNode* root, vector<int> result)`，`result` 会被复制一份，递归中追加的是副本，外层结果不会改变。这里必须写成 `vector<int>& result`。

## 方法二：迭代栈

```cpp
class Solution
{
public:
    std::vector<int> inorderTraversal(TreeNode* root)
    {
        std::vector<int> result;
        std::stack<TreeNode*> stack;
        TreeNode* current = root;

        while (current != nullptr || !stack.empty())
        {
            while (current != nullptr)
            {
                stack.push(current);
                current = current->left;
            }

            current = stack.top();
            stack.pop();
            result.push_back(current->val);

            current = current->right;
        }

        return result;
    }
};
```

迭代法的本质是：一路向左，把沿途节点压栈；左边走到底后弹出节点访问，再转向右子树。

## 前序与后序迁移

### 前序：中 -> 左 -> 右

栈是后进先出，所以要先压右节点，再压左节点。

```cpp
std::vector<int> preorderTraversal(TreeNode* root)
{
    std::vector<int> result;
    std::stack<TreeNode*> stack;

    if (root != nullptr)
    {
        stack.push(root);
    }

    while (!stack.empty())
    {
        TreeNode* node = stack.top();
        stack.pop();
        result.push_back(node->val);

        if (node->right != nullptr)
        {
            stack.push(node->right);
        }

        if (node->left != nullptr)
        {
            stack.push(node->left);
        }
    }

    return result;
}
```

### 后序：左 -> 右 -> 中

一种简化思路是先得到“中 -> 右 -> 左”，再整体反转，得到“左 -> 右 -> 中”。

```cpp
std::vector<int> postorderTraversal(TreeNode* root)
{
    std::vector<int> result;
    std::stack<TreeNode*> stack;

    if (root != nullptr)
    {
        stack.push(root);
    }

    while (!stack.empty())
    {
        TreeNode* node = stack.top();
        stack.pop();
        result.push_back(node->val);

        if (node->left != nullptr)
        {
            stack.push(node->left);
        }

        if (node->right != nullptr)
        {
            stack.push(node->right);
        }
    }

    std::reverse(result.begin(), result.end());
    return result;
}
```

## 复杂度

| 方法 | 时间 | 辅助空间 | 说明 |
|---|---:|---:|---|
| 递归 | O(n) | O(h) | h 是树高，最坏退化为 O(n) |
| 迭代栈 | O(n) | O(h) | 显式栈保存待访问路径 |

## 常见错误

- 递归辅助函数忘记 `vector<int>&`，导致结果写入副本。
- 中序迭代忘记在访问节点后转向 `current->right`。
- 前序迭代压栈顺序写反，导致输出变成中右左。
- 后序“先中右左再反转”时，压栈顺序应先左后右。
- 空树时没有判断，直接访问 `root->left` 或 `root->right`。

## 如何验证

至少覆盖：

- 空树：`[]`。
- 单节点：`[1]`。
- 普通结构：`[1,null,2,3]` 的中序结果为 `[1,3,2]`。
- 完全二叉树，确认前 / 中 / 后序顺序不同。
- 只有左链或只有右链的退化树。

本次整理遵循 LeetCode Inbox 规则：用户主动放入题解默认视为放入前已完成练习；当前智能体没有重新创建 C++ 工程或提交 LeetCode 复测。

## 相关内容

- 专题：[二叉树](index.md)
- C++：[刷题模板与易错点](../../../cpp/leetcode/templates.md)

> 标签：`二叉树` `DFS` `中序遍历` `递归` `栈` `C++`

