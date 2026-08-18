# 二叉树的层序遍历

> [LeetCode 102. Binary Tree Level Order Traversal](https://leetcode.cn/problems/binary-tree-level-order-traversal/) - Medium
>
> 学习状态：已完成 C++ 练习
>
> 练习日期：2026-08-17
>
> 本次实现：C++，队列 BFS 按层处理
>
> 验证状态：用户放入知识库前已完成练习；本次整理未重复运行 LeetCode 判题
>
> 证据归属：用户 `inbox/8月17号Leetcode.txt` 原始记录

## 学习目标

- 理解层序遍历的本质是 BFS：先访问当前层，再把下一层节点入队。
- 掌握“先固定当前层节点数，再处理这一层”的写法。
- 熟悉 `std::queue<TreeNode*>` 与 `std::vector<std::vector<int>>` 的组合使用。

## 题意与核心思路

题目要求从上到下、从左到右返回二叉树每一层的节点值。关键不是只会用队列，而是要能区分“当前层”和“下一层”。

做法：

```text
队列先放 root
while 队列不空：
  记录当前队列长度 levelSize
  新建当前层数组
  循环 levelSize 次：只弹出当前层节点
  把弹出节点的左右孩子加入队列，留给下一轮处理
```

这样每轮外层循环都严格对应树的一层。

## 方法：BFS 固定层大小

```cpp
class Solution
{
public:
    std::vector<std::vector<int>> levelOrder(TreeNode* root)
    {
        std::vector<std::vector<int>> result;
        if (root == nullptr)
        {
            return result;
        }

        std::queue<TreeNode*> queue;
        queue.push(root);

        while (!queue.empty())
        {
            int levelSize = static_cast<int>(queue.size());
            result.push_back(std::vector<int>());

            for (int i = 0; i < levelSize; i++)
            {
                TreeNode* node = queue.front();
                queue.pop();

                result.back().push_back(node->val);

                if (node->left != nullptr)
                {
                    queue.push(node->left);
                }

                if (node->right != nullptr)
                {
                    queue.push(node->right);
                }
            }
        }

        return result;
    }
};
```

用户本次记录中的关键错点是：外层 `std::vector<std::vector<int>>` 创建后，内层数组不会自动存在。每处理一层前要先 `result.push_back(std::vector<int>())`，之后才能用 `result.back().push_back(node->val)` 写入当前层。

## 复杂度

| 方法 | 时间 | 辅助空间 | 说明 |
|---|---:|---:|---|
| BFS | O(n) | O(w) | n 是节点数，w 是二叉树最大层宽 |

## 常见错误

- 忘记空树提前返回，导致 `root == nullptr` 时仍入队或访问成员。
- 没有在每层开始时固定 `levelSize`，导致下一层节点混入当前层。
- 忘记创建当前层数组，直接向不存在的内层 `vector<int>` 写入。
- 左右孩子入队前不判空，后续访问 `nullptr->val`。

## 如何验证

至少覆盖：

- 空树：`[] -> []`。
- 单节点：`[1] -> [[1]]`。
- 普通树：`[3,9,20,null,null,15,7] -> [[3],[9,20],[15,7]]`。
- 只有单边链的树，确认每层只有一个元素。

本次整理遵循 LeetCode Inbox 规则：用户主动放入题解默认视为放入前已完成练习；当前智能体没有重新创建 C++ 工程或提交 LeetCode 复测。

## 相关内容

- 专题：[二叉树](index.md)
- 前置题：[二叉树的最大深度](maximum-depth-of-binary-tree.md)
- C++：[刷题模板与易错点](../../../cpp/leetcode/templates.md)

> 标签：`二叉树` `BFS` `队列` `层序遍历` `C++`

