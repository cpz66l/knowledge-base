# 滑动窗口

> 窗口伸缩 — 子数组/子串满足条件的最优解

---

## 题目列表

<!-- TODO: 添加题目 -->
给定一个字符串 s ，请你找出其中不含有重复字符的 最长 子串 的长度。
public class Solution {
    public int LengthOfLongestSubstring(string s) {
        HashSet<char> window = new HashSet<char> ();
        int maxlen = 0;
        int left = 0;

        for(int right = 0; right < s.Length;right++){

            while(window.Contains(s[right])){
                window.Remove(s[left]);
                left++;
            }
            window.Add(s[right]);
            maxlen = Math.Max(maxlen , right - left + 1);
        }

        return maxlen;
    }
}
---

## 核心技巧

- 右指针扩展、左指针收缩
- 固定窗口 vs 可变窗口
- 用 Dictionary 统计窗口内字符/元素频率

---

> 📎 标签：`滑动窗口` `双指针` `子串`
