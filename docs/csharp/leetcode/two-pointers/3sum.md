# 三数之和 ⭐ 重点

> [LeetCode 15. 3Sum](https://leetcode.cn/problems/3sum/) - Medium

!!! warning "高频重点"
    这道题是双指针的**标杆题**，面试出现频率极高。排序 + 固定一端 + 对撞指针的组合思路，在四数之和、最接近的三数之和等变体中反复出现。**务必彻底掌握。**

给你一个整数数组 `nums`，判断是否存在三元组 `[nums[i], nums[j], nums[k]]` 满足 `i != j`、`i != k` 且 `j != k`，同时还满足 `nums[i] + nums[j] + nums[k] == 0`。请你返回所有和为 `0` 且不重复的三元组。

**注意：** 答案中不可以包含重复的三元组。

**核心思路：**

先排序，然后固定第一个数，剩余两数用左右对撞指针找。排序有两个好处：① 双指针可以根据和的大小决定左移还是右移；② 重复元素相邻排列，方便跳过。

```csharp
public class Solution
{
    public IList<IList<int>> ThreeSum(int[] nums)
    {
        // 先排序 - 双指针依赖有序性，同时让重复元素相邻方便去重
        Array.Sort(nums);
        List<IList<int>> result = new List<IList<int>>();

        // 固定第一个数 nums[i]
        for (int i = 0; i < nums.Length; i++)
        {
            // 剪枝：排序后最小的数都 > 0，后面不可能凑出 0
            if (nums[i] > 0) break;

            // 去重：当前数和前一个相同时跳过，避免产生重复三元组
            if (i > 0 && nums[i] == nums[i - 1]) continue;

            // 转化为两数之和问题：在 [i+1, n-1] 中找两数之和为 -nums[i]
            int left = i + 1;
            int right = nums.Length - 1;
            int target = -nums[i];

            while (left < right)
            {
                int sum = nums[left] + nums[right];

                if (sum == target)
                {
                    // 找到一个解，加入结果
                    result.Add(new List<int> { nums[i], nums[left], nums[right] });

                    // 去重：跳过左边重复元素
                    while (left < right && nums[left] == nums[left + 1]) left++;
                    // 去重：跳过右边重复元素
                    while (left < right && nums[right] == nums[right - 1]) right--;

                    // 收缩两端，继续寻找下一组解
                    left++;
                    right--;
                }
                else if (sum > target)
                {
                    // 和太大 -> 右指针左移，让和变小
                    right--;
                }
                else
                {
                    // 和太小 -> 左指针右移，让和变大
                    left++;
                }
            }
        }

        return result;
    }
}
```

| 复杂度 | |
|--------|------|
| 时间 | O(n²)，排序 O(n log n) + 外层循环 × 内层双指针 |
| 空间 | O(1)，不计结果列表（或 O(log n) 排序栈空间） |
