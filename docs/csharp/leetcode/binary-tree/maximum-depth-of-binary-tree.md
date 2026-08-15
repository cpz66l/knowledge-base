# 二叉树的最大深度

> [LeetCode 104. Maximum Depth of Binary Tree](https://leetcode.cn/problems/maximum-depth-of-binary-tree/) - Easy
>
> 学习状态：已完成 C++ 练习
>
> 练习日期：2026-08-12
>
> 本次实现：C++，递归 DFS / 层序 BFS
>
> 验证状态：用户放入知识库前已完成练习；本次整理未重复运行 LeetCode 判题
>
> 证据归属：用户 `inbox/8月12号Leetcode.txt` 原始记录

## 学习目标

- 理解“树的最大深度”是从根节点到最远叶子节点路径上的节点数。
- 掌握二叉树递归：空树返回 0，非空树返回左右子树最大深度 + 1。
- 掌握层序 BFS：每处理完一整层，深度计数加 1。

## 题意与核心思路

本题要求返回二叉树最大深度。递归视角下，一棵树的最大深度取决于它左右子树中更深的一边：

```text
depth(root) = max(depth(root.left), depth(root.right)) + 1
depth(nullptr) = 0
```

BFS 视角下，每次处理队列中当前层的全部节点，然后把下一层节点入队。处理过多少轮层级，答案就是多少。

## 方法一：递归 DFS

```cpp
class Solution
{
public:
    int maxDepth(TreeNode* root)
    {
        if (root == nullptr)
        {
            return 0;
        }

        return std::max(maxDepth(root->left), maxDepth(root->right)) + 1;
    }
};
```

递归函数返回“以当前节点为根的子树最大深度”。单层逻辑只需要取左右子树较大值，再加上当前节点这一层。

## 方法二：层序 BFS

```cpp
class Solution
{
public:
    int maxDepth(TreeNode* root)
    {
        if (root == nullptr)
        {
            return 0;
        }

        std::queue<TreeNode*> queue;
        queue.push(root);
        int depth = 0;

        while (!queue.empty())
        {
            int levelSize = static_cast<int>(queue.size());

            while (levelSize > 0)
            {
                TreeNode* node = queue.front();
                queue.pop();

                if (node->left != nullptr)
                {
                    queue.push(node->left);
                }

                if (node->right != nullptr)
                {
                    queue.push(node->right);
                }

                levelSize--;
            }

            depth++;
        }

        return depth;
    }
};
```

这里的关键是先记录 `levelSize = queue.size()`，再只处理当前层已有的节点。处理当前层时新入队的是下一层节点，不能让它们混进本轮计数。

## 复杂度

| 方法 | 时间 | 辅助空间 | 说明 |
|---|---:|---:|---|
| DFS | O(n) | O(h) | n 是节点数，h 是树高；递归栈最坏 O(n) |
| BFS | O(n) | O(w) | w 是树的最大宽度；队列最多保存一层节点 |

## 常见错误

- 空树忘记返回 0，直接访问 `root->left` 导致空指针问题。
- DFS 忘记 `+ 1`，只返回了子树深度。
- BFS 没有固定当前层 `levelSize`，导致深度计数和队列推进混在一起。
- 把“最大深度”误写成节点总数或叶子节点数量。

## 如何验证

至少覆盖：

- 空树：`[] -> 0`。
- 单节点：`[1] -> 1`。
- 左右高度不同的普通树：`[3,9,20,null,null,15,7] -> 3`。
- 只有左链或只有右链的退化树，确认深度等于链长。

本次整理遵循 LeetCode Inbox 规则：用户主动放入题解默认视为放入前已完成练习；当前智能体没有重新创建 C++ 工程或提交 LeetCode 复测。

## 相关内容

- 专题：[二叉树](index.md)
- C++：[刷题模板与易错点](../../../cpp/leetcode/templates.md)

> 标签：`二叉树` `DFS` `BFS` `递归` `队列` `C++`
