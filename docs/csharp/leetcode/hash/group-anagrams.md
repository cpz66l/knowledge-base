# 字母异位词分组

> [LeetCode 49. Group Anagrams](https://leetcode.cn/problems/group-anagrams/) - Medium

给你一个字符串数组，请将**字母异位词**组合在一起，可以按任意顺序返回结果列表。

字母异位词：由相同字母重排列而成的字符串，如 `"eat"` `"tea"` `"ate"`。

**核心思路：**

排序后的字符串作为 key，相同 key 的归为一组。`"eat"` -> 排序 -> `"aet"`，`"tea"` -> 排序 -> `"aet"`，它们 key 相同，放入同一 List。

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
            string key = new string(arr);   // "eat" -> "aet"

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
