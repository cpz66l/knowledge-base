# 滑动窗口

> 窗口伸缩 - 子数组/子串满足条件的最优解

---

## 题目列表

| 题目 | 难度 | 核心技巧 |
|------|------|----------|
| [无重复字符的最长子串](longest-substring-without-repeating-characters.md) | Medium | 可变窗口、HashSet 判重 |
| [找到字符串中所有字母异位词](find-all-anagrams-in-a-string.md) | Medium | 固定窗口、频率统计 |

---

## 核心技巧

- 右指针扩展、左指针收缩
- 固定窗口 vs 可变窗口
- 用 Dictionary 统计窗口内字符/元素频率
- 小写字母场景用 `int[26]` 替代 Dictionary，常数级优化

---

> 📎 标签：`滑动窗口` `双指针` `子串`
