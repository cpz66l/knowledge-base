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

给定两个字符串 s 和 p，找到 s 中所有 p 的 异位词 的子串，返回这些子串的起始索引。不考虑答案输出的顺序。

方法一：双字典+滑动窗口
public class Solution {
    public IList<int> FindAnagrams(string s, string p) {
        List<int> list = new List<int> ();
        Dictionary<char,int> pMap =new Dictionary<char,int> ();
        Dictionary<char,int> sMap =new Dictionary<char,int> ();
        if(p.Length>s.Length) return list;

        foreach(var i in p){
            if(pMap.ContainsKey(i)) pMap[i]++;
            else pMap[i] = 1;
        }
        int pLen = p.Length;

        for(int right = 0;right<pLen;right++){
            if(sMap.ContainsKey(s[right])) sMap[s[right]]++;
            else sMap[s[right]] = 1;
        }
        if(DictionEqual(pMap,sMap)) list.Add(0);
        
        for(int right = pLen ;right <s.Length;right++){
            //左边界扩展
            if(sMap.ContainsKey(s[right])) sMap[s[right]]++;
            else sMap[s[right]] = 1;
            //右边界收缩
            sMap[s[right-pLen]]--;
            if(sMap[s[right-pLen]] == 0) sMap.Remove(s[right-pLen]);

            if(DictionEqual(pMap,sMap)) list.Add(right-pLen+1);
        }
        return list;
    }
    public bool DictionEqual(Dictionary<char,int> a ,Dictionary<char,int> b){
        if(a.Count != b.Count) return false;
        foreach(var kv in a){
            if(!b.TryGetValue(kv.Key ,out int val) || val != kv.Value){
                return false;
            }
        }
        return true;
    }
}

方法二：数组+滑动窗口

方法适用于字符串由26个小写字母组成，将数组长度设为26，则字母字符的ACSLL码处理过可以用成下标索引，数组内部则是存储字母出现频次，这种方法远高于双字典空间与时间效率

public class Solution {
    public IList<int> FindAnagrams(string s, string p) {
        List<int> list = new List<int>();
        int[] pCount =new int[26];
        int[] sCount =new int[26];
        int pLen = p.Length;
        int sLen = s.Length;
        if(pLen > sLen) return list;

        foreach(char c in p){
            pCount[c-'a']++;
        }
        for(int right = 0; right <pLen ;right++){
            sCount[s[right] - 'a']++;
        }
        if(intEqual(pCount ,sCount)) list.Add(0);

        for(int right = pLen ;right<sLen;right++){
            //右边扩展
            sCount[s[right] - 'a']++;
            //左边收缩
            sCount[s[right-pLen] - 'a']--;

            if(intEqual(pCount ,sCount)) list.Add(right-pLen+1);
        }
        return list;

    }

    public bool intEqual(int[] a ,int[] b){
        for(int i =0;i<26 ;i++){
            if(a[i] != b[i]){
                return false;
            }
        }
        return true;
    }
}

## 核心技巧

- 右指针扩展、左指针收缩
- 固定窗口 vs 可变窗口
- 用 Dictionary 统计窗口内字符/元素频率

---

> 📎 标签：`滑动窗口` `双指针` `子串`
