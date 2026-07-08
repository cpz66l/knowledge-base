# 最长连续序列

> [LeetCode 128. Longest Consecutive Sequence](https://leetcode.cn/problems/longest-consecutive-sequence/) - Medium

给定一个未排序的整数数组 `nums`，找出数字连续的最长序列的长度。要求 **O(n)** 时间复杂度。

**核心思路：**

全部扔进 `HashSet` 实现 O(1) 查找。只从**序列起点**开始往后数 - 如果 `num - 1` 不在 set 中，则 `num` 就是某个连续序列的起点，从它开始往后数 `num + 1`、`num + 2`... 直到断开。每个数字最多被访问两次，整体 O(n)。

```csharp
public class Solution
{
    public int LongestConsecutive(int[] nums)
    {
        // 边界：空数组直接返回
        if (nums.Length == 0) return 0;

        // 1. 全部存入 HashSet，去重 + O(1) 查找
        HashSet<int> set = new HashSet<int>(nums);
        int maxLength = 0;

        // 2. 遍历每个数，只从"序列起点"开始往后数
        foreach (int num in nums)
        {
            // 如果 num-1 存在，说明 num 不是起点，跳过
            // 这样才能保证 O(n) - 每个数最多被内层 while 访问一次
            if (set.Contains(num - 1))
            {
                continue;
            }

            // 3. 从起点往后找连续数字
            int currentNum = num;
            int currentLength = 1;

            while (set.Contains(currentNum + 1))
            {
                currentNum++;
                currentLength++;
            }

            // 4. 更新最长长度
            if (currentLength > maxLength)
            {
                maxLength = currentLength;
            }
        }

        return maxLength;
    }
}
```

| 复杂度 | |
|--------|------|
| 时间 | O(n)，每个数字最多被内层 while 访问一次 |
| 空间 | O(n)，HashSet 存储所有数字 |
