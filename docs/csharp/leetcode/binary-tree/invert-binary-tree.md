# 翻转二叉树

> [LeetCode 226. Invert Binary Tree](https://leetcode.cn/problems/invert-binary-tree/) - Easy
>
> 学习状态：已完成 C++ 练习
>
> 练习日期：2026-08-14
>
> 本次实现：C++，递归 DFS
>
> 验证状态：用户放入知识库前已完成练习；本次整理未重复运行 LeetCode 判题
>
> 证据归属：用户 `inbox/8月14号leetcode.txt` 原始记录

## 学习目标

- 理解“翻转二叉树”本质上是每个节点的左右子树交换。
- 练习二叉树递归的空节点边界。
- 区分“交换当前节点左右孩子”和“递归处理左右子树”的顺序关系。

## 题意与核心思路

题目要求把整棵二叉树镜像翻转。对任意一个非空节点，只要把它的左子树和右子树分别翻转后再互换位置，当前子树就完成了翻转。

递归定义可以写成：

```text
invert(root) = swap(invert(root.left), invert(root.right))
invert(nullptr) = nullptr
```

## 方法：递归 DFS

```cpp
class Solution
{
public:
    TreeNode* invertTree(TreeNode* root)
    {
        if (root == nullptr)
        {
            return nullptr;
        }

        TreeNode* left = invertTree(root->left);
        root->left = invertTree(root->right);
        root->right = left;

        return root;
    }
};
```

这段写法先保存“翻转后的左子树”，再把“翻转后的右子树”放到左侧，最后把保存的左子树放到右侧。

也可以先 `std::swap(root->left, root->right)`，再递归处理交换后的左右子树；核心不变：每个节点的两个孩子都要交换一次。

## 复杂度

| 方法 | 时间 | 辅助空间 | 说明 |
|---|---:|---:|---|
| 递归 DFS | O(n) | O(h) | n 是节点数，h 是树高；最坏退化链表时递归栈 O(n) |

## 常见错误

- 空节点没有提前返回，导致访问 `root->left` 时空指针错误。
- 只交换了根节点的左右孩子，忘记递归处理子树。
- 保存临时指针的顺序写错，导致一侧子树被覆盖丢失。
- 把“翻转二叉树”和“判断对称二叉树”混淆：前者会修改树结构，后者只比较镜像关系。

## 如何验证

至少覆盖：

- 空树：`[] -> []`。
- 单节点：`[1] -> [1]`。
- 普通树：`[4,2,7,1,3,6,9] -> [4,7,2,9,6,3,1]`。
- 只有左链或只有右链的退化树，确认链方向会反转。

本次整理遵循 LeetCode Inbox 规则：用户主动放入题解默认视为放入前已完成练习；当前智能体没有重新创建 C++ 工程或提交 LeetCode 复测。

## 相关内容

- 专题：[二叉树](index.md)
- C++：[刷题模板与易错点](../../../cpp/leetcode/templates.md)

> 标签：`二叉树` `DFS` `递归` `镜像` `C++`

