# 搜索插入位置

> [LeetCode 35. Search Insert Position](https://leetcode.cn/problems/search-insert-position/) - Easy
>
> 学习状态：已完成 C++ 练习
>
> 练习日期：2026-08-26
>
> 本次实现：C++，二分查找 / 左边界
>
> 验证状态：用户放入知识库前已完成练习；本次整理未重复运行 LeetCode 判题
>
> 证据归属：用户 `inbox/8月26号leetcode.txt` 原始记录

## 学习目标

- 用二分查找在有序数组中找到 `target`。
- 当 `target` 不存在时，返回它应该插入的位置。
- 形成“找第一个 `>= target` 的位置”的左边界模板。

## 题意与核心思路

数组已经升序排列。插入位置其实就是：

```text
第一个满足 nums[i] >= target 的下标
```

如果所有元素都小于 `target`，答案就是 `nums.size()`，也就是插到数组末尾。

## 推荐写法：维护答案的闭区间二分

```cpp
class Solution
{
public:
    int searchInsert(vector<int>& nums, int target)
    {
        int left = 0;
        int right = static_cast<int>(nums.size()) - 1;
        int answer = static_cast<int>(nums.size());

        while (left <= right)
        {
            int mid = left + (right - left) / 2;

            if (nums[mid] >= target)
            {
                answer = mid;
                right = mid - 1;
            }
            else
            {
                left = mid + 1;
            }
        }

        return answer;
    }
};
```

当 `nums[mid] >= target` 时，`mid` 已经是一个候选答案，但左边可能还有更早的位置，所以记录 `answer = mid`，继续向左半边找。

当 `nums[mid] < target` 时，`mid` 和它左边都不可能是插入位置，直接移动 `left = mid + 1`。

## 关于递归写法

用户原始记录中也尝试了递归辅助函数。递归可以做，但这题更推荐迭代模板，因为：

- 二分题最容易错在边界和返回值，迭代写法状态更集中。
- `answer = n` 可以自然覆盖“插入到末尾”的情况。
- `mid = left + (right - left) / 2` 比 `(left + right) / 2` 更稳，避免极端下标溢出。

## 复杂度

| 复杂度 | 说明 |
|---|---|
| 时间 | O(log n)，每轮排除一半区间 |
| 空间 | O(1)，只使用常数个变量 |

## 常见错误

- 用 `(left + right) / 2`，在极端大下标时可能溢出。
- 找到 `nums[mid] >= target` 后直接返回，导致没有找到最左插入位置。
- 忘记处理 `target` 大于所有元素的情况；初始化 `answer = nums.size()` 可以覆盖。
- 把循环条件和边界移动混用，出现死循环或漏查最后一个元素。

## 如何验证

至少覆盖：

- 命中中间：`[1,3,5,6], target = 5 -> 2`。
- 插入中间：`[1,3,5,6], target = 2 -> 1`。
- 插入末尾：`[1,3,5,6], target = 7 -> 4`。
- 插入开头：`[1,3,5,6], target = 0 -> 0`。
- 单元素数组：`[1], target = 0 / 1 / 2`。

本次整理遵循 LeetCode Inbox 规则：用户主动放入题解默认视为放入前已完成练习；当前智能体没有重新创建 C++ 工程或提交 LeetCode 复测。

## 相关内容

- 专题：[二分查找](index.md)
- C++：[刷题模板与易错点](../../../cpp/leetcode/templates.md)

> 标签：`二分查找` `左边界` `C++`
