# 将有序数组转换为二叉搜索树

> [LeetCode 108. Convert Sorted Array to Binary Search Tree](https://leetcode.cn/problems/convert-sorted-array-to-binary-search-tree/) - Easy
>
> 学习状态：已完成 C++ 练习
>
> 练习日期：2026-08-18
>
> 本次实现：C++，递归选择中点建树
>
> 验证状态：用户放入知识库前已完成练习；本次整理未重复运行 LeetCode 判题
>
> 证据归属：用户 `inbox/8月18号leetcode.txt` 原始记录

## 学习目标

- 理解有序数组转 BST 的核心：中点作为根，左半边构成左子树，右半边构成右子树。
- 理解“平衡”来自每次尽量平均切分区间。
- 练习二叉树递归建树和指针返回值。

## 题意与核心思路

输入数组已经升序排列。二叉搜索树要求左子树节点值小于根，右子树节点值大于根；平衡要求左右子树高度差尽量小。

因此每次选择当前区间中点作为根节点：

```text
helper(left, right):
  如果 left > right，返回 nullptr
  mid = (left + right) / 2
  root = new TreeNode(nums[mid])
  root.left = helper(left, mid - 1)
  root.right = helper(mid + 1, right)
  return root
```

## 方法：递归中点建树

```cpp
class Solution
{
public:
    TreeNode* sortedArrayToBST(std::vector<int>& nums)
    {
        return build(nums, 0, static_cast<int>(nums.size()) - 1);
    }

private:
    TreeNode* build(std::vector<int>& nums, int left, int right)
    {
        if (left > right)
        {
            return nullptr;
        }

        int mid = left + (right - left) / 2;
        TreeNode* root = new TreeNode(nums[mid]);
        root->left = build(nums, left, mid - 1);
        root->right = build(nums, mid + 1, right);
        return root;
    }
};
```

本题在 LeetCode 环境中可以直接 `new TreeNode(...)` 并返回根节点，由判题环境管理树节点生命周期。普通 C++ 工程中如果自己建树，需要明确谁负责释放整棵树，不能把这个写法直接当作长期工程内存管理方案。

## 复杂度

| 方法 | 时间 | 辅助空间 | 说明 |
|---|---:|---:|---|
| 递归建树 | O(n) | O(log n) | 每个元素创建一个节点；递归深度约为树高 |

如果只考虑输出树本身之外的额外空间，递归栈为 O(log n)。创建出来的树包含 O(n) 个节点。

## 常见错误

- 递归终止条件写成 `left >= right`，导致单元素区间被漏掉。
- 右边界用错，入口应为 `nums.size() - 1`，空数组时会进入 `left > right` 分支。
- 只创建根节点，没有把左右递归结果接回 `root->left` 和 `root->right`。
- 普通工程中忘记树节点释放责任，把 LeetCode 写法误当成通用内存管理方案。

## 如何验证

至少覆盖：

- 空数组：`[] -> nullptr`。
- 单元素：`[1] -> 只有一个根节点`。
- 奇数长度：`[-10,-3,0,5,9]`，根可以取 `0`。
- 偶数长度：允许多个合法平衡 BST，重点检查中序遍历仍等于原数组，且高度基本平衡。

本次整理遵循 LeetCode Inbox 规则：用户主动放入题解默认视为放入前已完成练习；当前智能体没有重新创建 C++ 工程或提交 LeetCode 复测。

## 相关内容

- 专题：[二叉树](index.md)
- C++：[内存与资源管理](../../../cpp/memory/index.md)
- C++：[刷题模板与易错点](../../../cpp/leetcode/templates.md)

> 标签：`二叉树` `BST` `递归` `分治` `C++`

