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

### ⭐ 找到字符串中所有字母异位词

> [LeetCode 438. Find All Anagrams in a String](https://leetcode.cn/problems/find-all-anagrams-in-a-string/) — Medium

给定两个字符串 `s` 和 `p`，找到 `s` 中所有 `p` 的**异位词**的子串，返回这些子串的起始索引（顺序不限）。

**异位词**：由相同字母重排列而成的字符串。例如 `"abc"` 的异位词有 `"abc"`, `"acb"`, `"bac"`, `"bca"`, `"cab"`, `"cba"`。

**核心思路：**

固定长度滑动窗口（窗口大小 = `p.Length`），在 `s` 上滑动，每次只动左右各一个字符，判断窗口内字符频率是否与 `p` 一致。频率一致即为异位词。

```
s = "cbaebabacd", p = "abc"（p 的频率：a=1, b=1, c=1）

[cba]ebabacd  → 频率 {c:1,b:1,a:1} = p 频率 ✅ → 加入 0
c[bae]babacd  → 频率 {b:1,a:1,e:1} ≠ p        → 跳过
cb[aeb]abacd  → 频率 {a:1,e:1,b:1} ≠ p        → 跳过
cba[eba]bacd  → 频率 {e:1,b:1,a:1} ≠ p        → 跳过
cbae[bab]acd  → 频率 {b:2,a:1} ≠ p            → 跳过
cbaeb[aba]cd  → 频率 {a:2,b:1} ≠ p            → 跳过
cbaeba[bac]d  → 频率 {b:1,a:1,c:1} = p  ✅    → 加入 6
cbaebab[acd]  → 频率 {a:1,c:1,d:1} ≠ p        → 跳过
```

### 方法一：双字典 + 滑动窗口

适用于**任意字符集**。用 `Dictionary<char, int>` 统计频率，通用性好。

```csharp
public class Solution
{
    public IList<int> FindAnagrams(string s, string p)
    {
        List<int> result = new List<int>();
        int pLen = p.Length;
        int sLen = s.Length;

        // 边界：p 比 s 长，不可能有异位词
        if (pLen > sLen) return result;

        // 1. 统计 p 的字符频率（标准答案，后续窗口与之对比）
        Dictionary<char, int> pMap = new Dictionary<char, int>();
        foreach (char c in p)
        {
            if (pMap.ContainsKey(c)) pMap[c]++;
            else pMap[c] = 1;
        }

        // 2. 初始化第一个窗口（s 的前 pLen 个字符）
        Dictionary<char, int> sMap = new Dictionary<char, int>();
        for (int i = 0; i < pLen; i++)
        {
            if (sMap.ContainsKey(s[i])) sMap[s[i]]++;
            else sMap[s[i]] = 1;
        }

        // 3. 检查第一个窗口
        if (DictEquals(pMap, sMap)) result.Add(0);

        // 4. 滑动窗口：右进左出，每次只更新两个字符的计数
        for (int right = pLen; right < sLen; right++)
        {
            // 右边界扩展：新字符加入窗口
            char inChar = s[right];
            if (sMap.ContainsKey(inChar)) sMap[inChar]++;
            else sMap[inChar] = 1;

            // 左边界收缩：旧字符移出窗口
            char outChar = s[right - pLen];
            sMap[outChar]--;
            // 计数归零后移除 key，保证 DictEquals 的 Count 比较有效
            if (sMap[outChar] == 0) sMap.Remove(outChar);

            // 频率一致 → 找到异位词
            if (DictEquals(pMap, sMap)) result.Add(right - pLen + 1);
        }

        return result;
    }

    // 比较两个字典的键值对是否完全相等
    private bool DictEquals(Dictionary<char, int> a, Dictionary<char, int> b)
    {
        if (a.Count != b.Count) return false;
        foreach (var kv in a)
        {
            if (!b.TryGetValue(kv.Key, out int val) || val != kv.Value)
                return false;
        }
        return true;
    }
}
```

### 方法二：数组计数 + 滑动窗口

仅适用于**字符集为 26 个小写字母**的场景（题目约束）。将字母映射为数组下标（`'a'` → 0, `'b'` → 1 ...），数组值存储出现次数。省去字典的哈希开销，时间与空间都更优。

```csharp
public class Solution
{
    public IList<int> FindAnagrams(string s, string p)
    {
        List<int> result = new List<int>();
        int pLen = p.Length;
        int sLen = s.Length;

        // 边界：p 比 s 长，不可能有异位词
        if (pLen > sLen) return result;

        // 1. 用长度为 26 的数组统计 p 的字符频率
        //    索引 = c - 'a'，值 = 出现次数
        int[] pCount = new int[26];
        int[] sCount = new int[26];

        foreach (char c in p)
        {
            pCount[c - 'a']++;
        }

        // 2. 初始化第一个窗口
        for (int i = 0; i < pLen; i++)
        {
            sCount[s[i] - 'a']++;
        }

        // 3. 检查第一个窗口
        if (ArrayEquals(pCount, sCount)) result.Add(0);

        // 4. 滑动窗口：右进左出
        for (int right = pLen; right < sLen; right++)
        {
            // 右边界扩展：新字符计数 +1
            sCount[s[right] - 'a']++;

            // 左边界收缩：旧字符计数 -1（无需 Remove，归零也无妨）
            sCount[s[right - pLen] - 'a']--;

            if (ArrayEquals(pCount, sCount)) result.Add(right - pLen + 1);
        }

        return result;
    }

    // 逐位比较两个数组 — 固定 26 次循环，O(1)
    private bool ArrayEquals(int[] a, int[] b)
    {
        for (int i = 0; i < 26; i++)
        {
            if (a[i] != b[i]) return false;
        }
        return true;
    }
}
```

### 两种方法对比

| | 方法一：双字典 | 方法二：数组计数 |
|------|------|------|
| **适用场景** | 任意字符集（Unicode、ASCII） | 仅限 26 个小写字母 |
| **空间占用** | O(k)，k 为实际不同字符数 | O(1)，固定 26 × 4 = 104 字节 |
| **判等开销** | O(k)，遍历字典键值对 | O(1)，固定 26 次整数比较 |
| **代码复杂度** | 略高，需处理 key 增删 | 低，纯整数操作 |
| **通用性** | ✅ 通用 | ❌ 依赖字符集约束 |
| **性能** | 中规中矩 | 🚀 该场景下最优 |

> **选择建议**：题目明确限定小写字母时优先用数组（方法二），简洁且高效；字符集不确定时用字典（方法一）。

---

## 核心技巧

- 右指针扩展、左指针收缩
- 固定窗口 vs 可变窗口
- 用 Dictionary 统计窗口内字符/元素频率
- 小写字母场景用 `int[26]` 替代 Dictionary，常数级优化

---

> 📎 标签：`滑动窗口` `双指针` `子串`

