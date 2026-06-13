# 哈希

> Dictionary / HashSet — 空间换时间，O(1) 查找

---

## 题目列表

### 字母异位词分组

> [LeetCode 49. Group Anagrams](https://leetcode.cn/problems/group-anagrams/) — Medium

给你一个字符串数组，请将**字母异位词**组合在一起，可以按任意顺序返回结果列表。

字母异位词：由相同字母重排列而成的字符串，如 `"eat"` `"tea"` `"ate"`。

**核心思路：**

排序后的字符串作为 key，相同 key 的归为一组。`"eat"` → 排序 → `"aet"`，`"tea"` → 排序 → `"aet"`，它们 key 相同，放入同一 List。

```csharp
public class Solution
{
    public IList<IList<string>> GroupAnagrams(string[] strs)
    {
        // key: 排序后的字符串  value: 同一组字母异位词列表
        Dictionary<string, List<string>> map = new Dictionary<string, List<string>>();

        foreach (var str in strs)
        {
            // 1. 转 char[] 后排序，得到统一 key
            char[] arr = str.ToCharArray();
            Array.Sort(arr);
            string key = new string(arr);   // "eat" → "aet"

            // 2. key 不存在则先创建空列表
            if (!map.ContainsKey(key))
            {
                map[key] = new List<string>();
            }

            // 3. 将原字符串加入对应分组
            map[key].Add(str);
        }

        // 4. 返回所有分组（Values 是 List<string> 的集合）
        return new List<IList<string>>(map.Values);
    }
}
```

| 复杂度 | |
|--------|------|
| 时间 | O(n · k log k)，n 个字符串，每个长度 k 排序 |
| 空间 | O(n · k)，哈希表存储所有字符串 |

---

### 最长连续序列

> [LeetCode 128. Longest Consecutive Sequence](https://leetcode.cn/problems/longest-consecutive-sequence/) — Medium

给定一个未排序的整数数组 `nums`，找出数字连续的最长序列的长度。要求 **O(n)** 时间复杂度。

**核心思路：**

全部扔进 `HashSet` 实现 O(1) 查找。只从**序列起点**开始往后数 — 如果 `num - 1` 不在 set 中，则 `num` 就是某个连续序列的起点，从它开始往后数 `num + 1`、`num + 2`... 直到断开。每个数字最多被访问两次，整体 O(n)。

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
            // 这样才能保证 O(n) — 每个数最多被内层 while 访问一次
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

---

## 核心技巧

- 用 `Dictionary<T, int>` 记录出现次数/索引
- 用 `HashSet<T>` 去重、判存在
- 哈希表 + 前缀和经典套路

---

> 📎 标签：`哈希表` `查找优化`
