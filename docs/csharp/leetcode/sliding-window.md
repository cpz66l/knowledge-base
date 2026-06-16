# 滑动窗口

> 窗口伸缩 — 子数组/子串满足条件的最优解

---

## 题目列表

### ⭐ 无重复字符的最长子串

> [LeetCode 3. Longest Substring Without Repeating Characters](https://leetcode.cn/problems/longest-substring-without-repeating-characters/) — Medium

给定一个字符串 `s`，找出其中不含有重复字符的**最长子串**的长度。

**核心思路：**

滑动窗口 + HashSet。右指针不断向右扩展，当遇到重复字符时，左指针收缩直到窗口内无重复。整个过程窗口始终是"无重复子串"，每次扩张后更新最大长度。

```
s = "abcabcbb"

窗口变化（→ 扩张，← 收缩）：
[a]         → left=0, right=0, len=1
[ab]        → left=0, right=1, len=2
[abc]       → left=0, right=2, len=3  ← 目前为止最长
 bca        ← 'a' 重复，left 移到第一个 a 之后
[abc]       → left=1, right=3, len=3
  cab       → left=2, right=4, len=3
   abc      → left=3, right=5, len=3
     cb     → left=5, right=6, len=2
       b    → left=7, right=7, len=1
```

```csharp
public class Solution
{
    public int LengthOfLongestSubstring(string s)
    {
        // HashSet 维护当前窗口内的字符，保证 O(1) 判重
        HashSet<char> window = new HashSet<char>();
        int maxLen = 0;
        int left = 0;

        // 右指针逐位向右扩展
        for (int right = 0; right < s.Length; right++)
        {
            // 判断新窗口内有没有重复字符
            while (window.Contains(s[right]))
            {// 不断收缩左边界直到窗口内的重复消除
                window.Remove(s[left]);
                left++;//收缩
            }

            // 窗口内已无重复，加入当前字符
            window.Add(s[right]);

            // 此时 [left, right]窗口内是无重复子串，更新最大长度
            maxLen = Math.Max(maxLen, right - left + 1);
        }

        return maxLen;
    }
}
```

| 复杂度 | |
|--------|------|
| 时间 | O(n)，每个字符最多被左右指针各访问一次 |
| 空间 | O(k)，k 为字符集大小（ASCII 最多 128，扩展 ASCII 256） |
---

## 核心技巧

- 右指针扩展、左指针收缩
- 固定窗口 vs 可变窗口
- 用 Dictionary 统计窗口内字符/元素频率

---

> 📎 标签：`滑动窗口` `双指针` `子串`
