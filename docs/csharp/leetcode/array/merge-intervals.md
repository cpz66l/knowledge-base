# 合并区间 ⭐ 重点

> [LeetCode 56. Merge Intervals](https://leetcode.cn/problems/merge-intervals/) - Medium

!!! warning "高频重点"
    区间类问题的**模板题**。掌握"排序 + 贪心合并"这一套路后，可秒杀"插入区间"、"用最少数量的箭引爆气球"、"无重叠区间"等一整套变体题。面试出现频率极高。

以数组 `intervals` 表示若干个区间的集合，其中单个区间为 `intervals[i] = [starti, endi]`。请你合并所有重叠的区间，并返回一个不重叠的区间数组，该数组需恰好覆盖输入中的所有区间。

**核心思路：**

排序 + 贪心。先把所有区间按**左端点升序**排序，这样能合并的区间一定相邻。遍历排序后的区间，维护结果集 `res`：取结果集中最后一个区间 `last` 与当前区间 `current` 比较 -- 若 `last` 的右端点 `>= current` 的左端点，说明重叠，把 `last` 的右端点更新为两者右端点的较大值（合并）；否则不重叠，把 `current` 直接加入结果集。

```
intervals = [[1,3],[2,6],[8,10],[15,18]]

排序后（按左端点）：[[1,3],[2,6],[8,10],[15,18]]  （本题已有序）

遍历过程（res = 结果集，last = res 中最后一个区间）：
i=0, [1,3]:  res 为空 -> 直接加入              res = [[1,3]]
i=1, [2,6]:  last=[1,3], last[1]=3 >= current[0]=2 -> 重叠！
             last[1] = max(3, 6) = 6            res = [[1,6]]
i=2, [8,10]: last=[1,6], last[1]=6 < current[0]=8 -> 不重叠
             直接加入                            res = [[1,6],[8,10]]
i=3, [15,18]:last=[8,10],last[1]=10 < current[0]=15 -> 不重叠
             直接加入                            res = [[1,6],[8,10],[15,18]]

结果 = [[1,6],[8,10],[15,18]]
```

```csharp
public class Solution
{
    public int[][] Merge(int[][] intervals)
    {
        // 边界：空数组直接返回
        if (intervals.Length == 0) return Array.Empty<int[]>();

        List<int[]> res = new List<int[]>();

        // 关键：按左端点升序排序，保证可能重叠的区间相邻
        Array.Sort(intervals, (a, b) => a[0].CompareTo(b[0]));

        // 第一个区间直接放入结果集
        res.Add(intervals[0]);

        for (int i = 1; i < intervals.Length; i++)
        {
            // 取结果集中最后一个区间与当前区间比较
            int[] last = res[res.Count - 1];
            int[] current = intervals[i];

            if (last[1] >= current[0])
            {
                // 重叠：合并 -- 右端点取两者较大值
                // 注意 last 是 res 中的引用，直接修改即可反映到结果集
                last[1] = Math.Max(last[1], current[1]);
            }
            else
            {
                // 不重叠：当前区间作为新区间加入结果集
                res.Add(current);
            }
        }

        return res.ToArray();
    }
}
```

| 复杂度 | |
|--------|------|
| 时间 | O(n log n)，排序占主导；遍历 O(n) |
| 空间 | O(n)，结果集最多存 n 个区间（排序额外 O(log n)） |

!!! tip "为什么排序后只需和结果集最后一个区间比较？"
    排序后区间按左端点递增，结果集中最后一个区间 `last` 的左端点 ≤ 所有未处理区间的左端点。所以能与后续区间重叠的，**只可能是 `last`** -- 它是当前右端点最大的已合并区间。新区间要么被 `last` 吞并（重叠），要么自成一段（不重叠），无需回看更早的区间。
