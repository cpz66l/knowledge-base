# 子串

> 子串问题套路 — 前缀和、KMP、动态规划

---

## 题目列表

### 和为 K 的子数组

> [LeetCode 560. Subarray Sum Equals K](https://leetcode.cn/problems/subarray-sum-equals-k/) — Medium

给你一个整数数组 `nums` 和一个整数 `k`，请你统计并返回该数组中**和为 `k` 的子数组的个数**。子数组是数组中元素的连续非空序列。

**核心思路：**

子数组和问题，先想**前缀和**。定义 `preSum[i]` 为 `nums[0..i-1]` 的累加和，则任意子数组 `[i, j]` 的和 = `preSum[j+1] - preSum[i]`。要找 `preSum[j+1] - preSum[i] == k`，即 `preSum[i] == preSum[j+1] - k`。遍历时用哈希表记录每个前缀和出现的次数，到位置 `j` 时查 `preSum[j+1] - k` 之前出现过几次，就找到了几个满足条件的子数组。

### 方法一：暴力枚举（O(n²)）

从左到右枚举子数组起点，对每个起点向右累加，遇到和为 `k` 就计数。思路直观但效率低，适合面试时先说出来再优化。

```csharp
public class Solution
{
    public int SubarraySum(int[] nums, int k)
    {
        // 边界：空数组没有子数组
        if (nums.Length == 0) return 0;

        int count = 0;

        // 枚举子数组起点
        for (int left = 0; left < nums.Length; left++)
        {
            int sum = 0;
            // 从起点向右扩展，累加过程中遇到 k 就计数
            for (int right = left; right < nums.Length; right++)
            {
                sum += nums[right];
                if (sum == k) count++;
            }
        }

        return count;
    }
}
```

| 复杂度 | |
|--------|------|
| 时间 | O(n²)，两重循环枚举所有子数组 |
| 空间 | O(1)，只用了几个变量 |

### 方法二：前缀和 + 哈希表（O(n)）⭐ 推荐

一边遍历一边维护前缀和与哈希表。哈希表的 key 是前缀和值，value 是该前缀和出现的次数。走到每个位置时，查 `当前前缀和 - k` 在哈希表中出现过多少次，就说明有多少个子数组以当前位置结尾且和为 `k`。

```
nums = [1, 1, 1], k = 2

遍历过程（preSum = 当前前缀和, map 记录每个前缀和出现次数）：
i=0, num=1:  preSum=1, 查 map[1-2=-1] → 0次, map[1]=1, count=0
i=1, num=1:  preSum=2, 查 map[2-2=0]  → 1次（初始化 map[0]=1）, map[2]=1, count=1 ← [0,1]
i=2, num=1:  preSum=3, 查 map[3-2=1]  → 1次, map[3]=1, count=2            ← [1,2]
结果为 2
```

```csharp
public class Solution
{
    public int SubarraySum(int[] nums, int k)
    {
        // key: 前缀和  value: 该前缀和出现的次数
        Dictionary<int, int> map = new Dictionary<int, int>();
        // 初始化：前缀和为 0 出现 1 次（处理子数组从下标 0 开始的情况）
        map[0] = 1;

        int count = 0;       // 满足条件的子数组个数
        int curSum = 0;      // 当前前缀和

        foreach (int num in nums)
        {
            // 1. 更新前缀和
            curSum += num;

            // 2. 查找有多少个前缀和等于 curSum - k
            //    这些前缀和对应的位置到当前位置之间，子数组和就是 k
            int target = curSum - k;
            if (map.ContainsKey(target))
            {
                count += map[target];
            }

            // 3. 将当前前缀和记录到 map（可能已存在，累加次数）
            if (map.ContainsKey(curSum))
            {
                map[curSum]++;
            }
            else
            {
                map[curSum] = 1;
            }
        }

        return count;
    }
}
```

| 复杂度 | |
|--------|------|
| 时间 | O(n)，只遍历一次数组，每次哈希表查插 O(1) |
| 空间 | O(n)，哈希表最多存 n 个不同的前缀和 |

### 两种方法对比

| | 方法一：暴力枚举 | 方法二：前缀和 + 哈希表 |
|------|------|------|
| **时间** | O(n²) | O(n) |
| **空间** | O(1) | O(n) |
| **适用场景** | 快速验证、小数据量 | 面试/生产环境标准解法 |
| **核心技巧** | 枚举所有子数组 | 前缀和差 + 哈希表计数 |

> **选择建议**：面试时先说暴力法展示思考过程，然后引出前缀和优化。前缀和 + 哈希表是子数组和问题的**核心套路**，同类题还有"和可被 K 整除的子数组"等。
---

## 核心技巧

- 前缀和 + 哈希表
- 回文子串：中心扩展 / DP
- KMP 字符串匹配（了解思想即可，面试低频）

---

> 📎 标签：`子串` `前缀和` `回文`
