# 在排序数组中查找元素的第一个和最后一个位置

> [LeetCode 34. Find First and Last Position of Element in Sorted Array](https://leetcode.cn/problems/find-first-and-last-position-of-element-in-sorted-array/) - Medium
>
> 学习状态：已完成 C++ 练习
>
> 练习日期：2026-08-28
>
> 本次实现：C++，二分查找 / 左右边界
>
> 验证状态：用户放入知识库前已完成练习；本次整理未重复运行 LeetCode 判题
>
> 证据归属：用户 `inbox/8月28号leetcod.txt` 原始记录

## 学习目标

- 在有重复元素的有序数组中找出 `target` 的左端点和右端点。
- 复用二分边界思想，把问题拆成“第一个 `>= target`”和“第一个 `> target`”。
- 保证总时间复杂度为 O(log n)，不退化为线性扫描。

## 题意与核心思路

如果直接从前往后扫描，可以记录第一次和最后一次出现的位置，但时间复杂度是 O(n)，没有利用数组已排序的条件。

有序数组中的目标区间可以写成：

```text
leftIdx  = 第一个 >= target 的位置
rightIdx = 第一个 > target 的位置 - 1
```

最后再校验 `leftIdx` 和 `rightIdx` 是否真的指向 `target`。如果目标不存在，返回 `[-1, -1]`。

## 推荐写法：复用边界二分

```cpp
class Solution
{
public:
    int binarySearch(vector<int>& nums, int target, bool lower)
    {
        int left = 0;
        int right = static_cast<int>(nums.size()) - 1;
        int answer = static_cast<int>(nums.size());

        while (left <= right)
        {
            int mid = left + (right - left) / 2;

            if (nums[mid] > target || (lower && nums[mid] >= target))
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

    vector<int> searchRange(vector<int>& nums, int target)
    {
        int leftIdx = binarySearch(nums, target, true);
        int rightIdx = binarySearch(nums, target, false) - 1;

        if (leftIdx <= rightIdx
            && rightIdx < static_cast<int>(nums.size())
            && nums[leftIdx] == target
            && nums[rightIdx] == target)
        {
            return vector<int>{ leftIdx, rightIdx };
        }

        return vector<int>{ -1, -1 };
    }
};
```

`lower = true` 时，条件等价于找第一个 `>= target` 的位置。

`lower = false` 时，条件等价于找第一个 `> target` 的位置。

这样不用写两份几乎一样的二分逻辑，也避免用 `target + 1` 时遇到 `INT_MAX` 溢出的风险。

## 复杂度

| 复杂度 | 说明 |
|---|---|
| 时间 | O(log n)，执行两次二分 |
| 空间 | O(1)，只使用常数个变量 |

## 常见错误

- 找到一个 `target` 后向左右线性扩展，最坏会退化成 O(n)。
- 只找第一个 `>= target`，忘记右边界应来自第一个 `> target`。
- 目标不存在时没有二次校验，导致返回错误区间。
- 使用 `(left + right) / 2`，极端下标下可能溢出；优先使用 `left + (right - left) / 2`。
- `rightIdx` 可能为 `-1`，校验时要先保证区间合法，再访问数组。

## 如何验证

至少覆盖：

- 多个命中：`[5,7,7,8,8,10], target = 8 -> [3,4]`。
- 不存在：`[5,7,7,8,8,10], target = 6 -> [-1,-1]`。
- 空数组：`[], target = 0 -> [-1,-1]`。
- 全部相等：`[2,2,2], target = 2 -> [0,2]`。
- 单元素命中 / 不命中：`[1], target = 1 / 0`。

本次整理遵循 LeetCode Inbox 规则：用户主动放入题解默认视为放入前已完成练习；当前智能体没有重新创建 C++ 工程或提交 LeetCode 复测。

## 相关内容

- 专题：[二分查找](index.md)
- C++：[刷题模板与易错点](../../../cpp/leetcode/templates.md)

> 标签：`二分查找` `左边界` `右边界` `C++`

