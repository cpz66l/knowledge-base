# 哈希

> Dictionary / HashSet — 空间换时间，O(1) 查找

---
## 哈希原理（C# / .NET）

### 底层结构：数组 + 改良链地址法

**数组** — 存储键值对。输入 key 经哈希函数映射到桶数组下标 `f(key)`，通过下标获取桶内对应的值 value。

**哈希冲突** — 哈希函数将较大的输入空间映射到较小的输出空间，根据鸽巢原理，必然有多个 key 映射到同一桶索引，造成冲突。

冲突的两种主流解决策略：

| 策略 | 代表语言 | 核心做法 |
|------|---------|----------|
| 链地址法 | Java / C# / Go / C++ | 每个桶挂一个链表，冲突元素链在后面 |
| 开放寻址法 | Python / Rust | 冲突时按规则找下一个空位（线性探测 / 平方探测 / 多次哈希） |

> JS 的哈希实现较复杂，现代 V8 采用混合策略，大致接近开放寻址方向。

### .NET 的改良链地址法

底层两个数组紧密配合：

- **`buckets`** — 桶数组，每个位置存的是 entry 下标（链表头指针），不是值本身
- **`entries`** — 连续存储所有键值对实体，通过每个 entry 的 `next` 字段串联同桶冲突元素

```
buckets: [3, -1, 1, ...]           ← 存 entry 下标，-1 表示空桶
           ↓       ↓
entries: [entry0] [entry1] [entry2] [entry3] ...
                     ↓next=2         ↓next=-1（链表尾）
```

没有独立的 `LinkedListNode` 对象，所有数据在 `entries` 数组里连续布局，内存更紧凑，CPU 缓存更友好。

- **桶数组长度取质数**（非 2 的幂），每次扩容找下一个更大的质数 — 质数取模让哈希分布更均匀
- **负载因子约 0.72 触发扩容** — 当 `count > buckets.Length × 0.72` 时自动扩容并重新哈希

### 链地址法 vs 开放寻址法

=== 链地址法（Java / C# / Go / C++）===

| ✅ 优势 | ❌ 劣势 |
|---------|---------|
| 负载因子容忍度高（可 > 1） | 链表指针产生额外内存开销 |
| 插入删除简单，删除不破坏探测链 | 长链表导致缓存失效，退化为 O(n) |
| 适合大数据量、频繁增删场景 | |

=== 开放寻址法（Python / Rust）===

| ✅ 优势 | ❌ 劣势 |
|---------|---------|
| 全部数据在连续数组，CPU 缓存命中率极高 | 负载因子不能超过 1 |
| 无链表指针，零额外内存浪费 | 删除需特殊标记（逻辑删除） |
| | 高冲突下探测链变长，性能暴跌 |

### 各语言实现差异

| 语言 | 策略 | 备注 |
|------|------|------|
| Java | 链地址法 | 链表 + 红黑树（链表长 ≥ 8 时转树） |
| C# | 改良链地址法 | entries 数组连续存储，无独立链表对象 |
| Go | 链地址法 | 每个桶存 8 个键值对，溢出时链额外桶 |
| C++ | 标准链地址 | 桶位挂单向链表，无红黑树；`max_load_factor` 默认 1.0 |
| Python | 开放寻址法 | 伪随机探测序列，删除用标记位 |
| Rust | 开放寻址法 | Robin Hood 哈希，高负载下性能稳定 |

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
