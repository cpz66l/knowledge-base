# 数组

> 遍历 · 原地操作 · 前缀后缀 — 最基础也最常考的数据结构

---

## 题目列表

### 最大子数组和 ⭐ 重点

> [LeetCode 53. Maximum Subarray](https://leetcode.cn/problems/maximum-subarray/) — Medium

!!! warning "高频重点"
    这道题是动态规划的**入门必刷题**，Kadane 算法的经典应用。同类题还有"环形子数组的最大和"、"乘积最大子数组"。面试出现频率极高，**务必彻底掌握。**

给你一个整数数组 `nums`，请你找出一个具有最大和的连续子数组（子数组最少包含一个元素），返回其最大和。子数组是数组中的一个连续部分。

**核心思路：**

Kadane 算法 — 遍历数组，在每个位置做选择：要么把当前元素**接到前面**的子数组后面（`nums[i] + curMax`），要么**另起炉灶**从当前元素开始新子数组（`nums[i]`）。取两者较大值作为以当前位置结尾的最大子数组和，再和全局最大值比较。

```
nums = [-2, 1, -3, 4, -1, 2, 1, -5, 4]

遍历过程（curMax = 以当前位置结尾的最大子数组和, maxSum = 全局最大值）：
i=0, nums[0]=-2:  curMax = -2（起步）,            maxSum = -2
i=1, nums[1]= 1:  curMax = max(1, 1+(-2)) = 1,  maxSum = 1  ← 另起炉灶
i=2, nums[2]=-3:  curMax = max(-3, -3+1) = -2,  maxSum = 1
i=3, nums[3]= 4:  curMax = max(4, 4+(-2)) = 4,  maxSum = 4  ← 另起炉灶
i=4, nums[4]=-1:  curMax = max(-1, -1+4) = 3,   maxSum = 4
i=5, nums[5]= 2:  curMax = max(2, 2+3) = 5,     maxSum = 5
i=6, nums[6]= 1:  curMax = max(1, 1+5) = 6,     maxSum = 6  ← 全局最大 [4,-1,2,1]
i=7, nums[7]=-5:  curMax = max(-5, -5+6) = 1,   maxSum = 6
i=8, nums[8]= 4:  curMax = max(4, 4+1) = 5,     maxSum = 6
结果为 6（子数组 [4, -1, 2, 1]）
```

```csharp
public class Solution
{
    public int MaxSubArray(int[] nums)
    {
        // 边界：数组为空（题目保证最少一个元素，但防御性写上）
        if (nums.Length == 0) return 0;

        // curMax：以当前位置结尾的最大子数组和
        int curMax = nums[0];
        // maxSum：全局最大子数组和
        int maxSum = nums[0];

        // 从第二个元素开始遍历
        for (int i = 1; i < nums.Length; i++)
        {
            // 核心选择：接上前面的子数组 vs 另起炉灶
            // 如果 curMax 是负数，接上去只会拖后腿 → 不如从当前元素重新开始
            curMax = Math.Max(nums[i], nums[i] + curMax);//状态转移方程
            // 更新全局最大值
            maxSum = Math.Max(maxSum, curMax);
        }
        return maxSum;
    }
}
```

| 复杂度 | |
|--------|------|
| 时间 | O(n)，遍历一次数组 |
| 空间 | O(1)，只用了两个变量 |

### 方法二：分治法（O(n log n)）

面试中有时会追问分治解法。将数组从中间分成左右两半，最大子数组要么在**左半**、要么在**右半**、要么**跨越中点**。跨越中点的部分从中点向两侧延伸求和。三种情况取最大值即可。

```csharp
public class Solution
{
    public int MaxSubArray(int[] nums)
    {
        return DivideAndConquer(nums, 0, nums.Length - 1);
    }

    private int DivideAndConquer(int[] nums, int left, int right)
    {
        // 递归终止：只有一个元素
        if (left == right) return nums[left];

        int mid = left + (right - left) / 2;

        // 1. 左半部分的最大子数组和
        int leftMax = DivideAndConquer(nums, left, mid);

        // 2. 右半部分的最大子数组和
        int rightMax = DivideAndConquer(nums, mid + 1, right);

        // 3. 跨越中点的最大子数组和
        int crossMax = CrossSum(nums, left, right, mid);

        // 三种情况取最大
        return Math.Max(Math.Max(leftMax, rightMax), crossMax);
    }

    // 计算跨越中点的最大子数组和
    private int CrossSum(int[] nums, int left, int right, int mid)
    {
        // 从中点向左延伸，找最大累加和
        int leftSum = int.MinValue;
        int sum = 0;
        for (int i = mid; i >= left; i--)
        {
            sum += nums[i];
            leftSum = Math.Max(leftSum, sum);
        }

        // 从中点+1向右延伸，找最大累加和
        int rightSum = int.MinValue;
        sum = 0;
        for (int i = mid + 1; i <= right; i++)
        {
            sum += nums[i];
            rightSum = Math.Max(rightSum, sum);
        }

        // 跨越中点的最大值 = 左半最大 + 右半最大
        return leftSum + rightSum;
    }
}
```

| 复杂度 | |
|--------|------|
| 时间 | O(n log n)，递归树深度 log n，每层合并 O(n) |
| 空间 | O(log n)，递归调用栈深度 |

### 两种方法对比

| | 方法一：Kadane（DP）| 方法二：分治法 |
|------|------|------|
| **时间** | O(n) | O(n log n) |
| **空间** | O(1) | O(log n) |
| **核心技巧** | 动态规划，贪心选择 | 二分递归，跨越中点 |
| **适用场景** | 面试/生产标准解法 | 面试追问、理解分治思想 |

> **选择建议**：Kadane 算法是这题的**标准解法**，O(n) 时间 O(1) 空间已是最优。分治法虽然慢一些，但体现了"最大子数组"问题的分治本质。

---

### 合并区间 ⭐ 重点

> [LeetCode 56. Merge Intervals](https://leetcode.cn/problems/merge-intervals/) — Medium

!!! warning "高频重点"
    区间类问题的**模板题**。掌握"排序 + 贪心合并"这一套路后，可秒杀"插入区间"、"用最少数量的箭引爆气球"、"无重叠区间"等一整套变体题。面试出现频率极高。

以数组 `intervals` 表示若干个区间的集合，其中单个区间为 `intervals[i] = [starti, endi]`。请你合并所有重叠的区间，并返回一个不重叠的区间数组，该数组需恰好覆盖输入中的所有区间。

**核心思路：**

排序 + 贪心。先把所有区间按**左端点升序**排序，这样能合并的区间一定相邻。遍历排序后的区间，维护结果集 `res`：取结果集中最后一个区间 `last` 与当前区间 `current` 比较 —— 若 `last` 的右端点 `>= current` 的左端点，说明重叠，把 `last` 的右端点更新为两者右端点的较大值（合并）；否则不重叠，把 `current` 直接加入结果集。

```
intervals = [[1,3],[2,6],[8,10],[15,18]]

排序后（按左端点）：[[1,3],[2,6],[8,10],[15,18]]  （本题已有序）

遍历过程（res = 结果集，last = res 中最后一个区间）：
i=0, [1,3]:  res 为空 → 直接加入              res = [[1,3]]
i=1, [2,6]:  last=[1,3], last[1]=3 >= current[0]=2 → 重叠！
             last[1] = max(3, 6) = 6            res = [[1,6]]
i=2, [8,10]: last=[1,6], last[1]=6 < current[0]=8 → 不重叠
             直接加入                            res = [[1,6],[8,10]]
i=3, [15,18]:last=[8,10],last[1]=10 < current[0]=15 → 不重叠
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
                // 重叠：合并 —— 右端点取两者较大值
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
    排序后区间按左端点递增，结果集中最后一个区间 `last` 的左端点 ≤ 所有未处理区间的左端点。所以能与后续区间重叠的，**只可能是 `last`** —— 它是当前右端点最大的已合并区间。新区间要么被 `last` 吞并（重叠），要么自成一段（不重叠），无需回看更早的区间。

---

### 除自身以外数组的乘积 ⭐ 重点

> [LeetCode 238. Product of Array Except Self](https://leetcode.cn/problems/product-of-array-except-self/) — Medium

!!! warning "高频重点"
    前缀积/后缀积思想的**代表题**，Facebook/Google 等大厂高频面试题。题目明确要求**不用除法、O(n) 时间**，强制考察对"前缀后缀"的灵活运用。务必理解透，变体题很多。

给你一个整数数组 `nums`，返回数组 `answer`，其中 `answer[i]` 等于 `nums` 中除了 `nums[i]` 之外其余各元素的乘积。

题目数据**保证**数组 `nums` 之中任意元素的全部前缀元素和后缀的乘积都在 32 位整数范围内。

**请不要使用除法**，且在 **O(n) 时间复杂度**内完成此题。

**核心思路：**

`answer[i]` = `nums[i]` 左侧所有元素的乘积 × 右侧所有元素的乘积。所以预先构造两张表：

- `prefix[i]` = `nums[0] × nums[1] × ... × nums[i]`（从左到右的**前缀积**，含 `nums[i]`）
- `postfix[i]` = `nums[len-1-i] × ... × nums[len-1]`（从右到左的**后缀积**，含末尾 `i+1` 个元素）

然后 `answer[i] = 左侧前缀积(prefix[i-1]) × 右侧后缀积(postfix[len-2-i])`，首尾两个位置单独处理（一侧无元素，乘积视为 1）。

```
nums = [1, 2, 3, 4]   (len = 4)

第一步：构造前缀积 prefix[i] = nums[0..i] 的乘积（从左往右累乘）
  prefix[0] = 1                     → prefix = [1,  _,  _,  _]
  prefix[1] = 2 × prefix[0] =  2    → prefix = [1,  2,  _,  _]
  prefix[2] = 3 × prefix[1] =  6    → prefix = [1,  2,  6,  _]
  prefix[3] = 4 × prefix[2] = 24    → prefix = [1,  2,  6, 24]

第二步：构造后缀积 postfix[i] = nums[len-1-i .. len-1] 的乘积（从右往左累乘）
  postfix[0] = nums[3] = 4                  → postfix = [ 4,  _,  _,  _]
  postfix[1] = nums[2] × postfix[0] = 12    → postfix = [ 4, 12,  _,  _]
  postfix[2] = nums[1] × postfix[1] = 24    → postfix = [ 4, 12, 24,  _]
  postfix[3] = nums[0] × postfix[2] = 24    → postfix = [ 4, 12, 24, 24]

第三步：answer[i] = 左侧前缀积 × 右侧后缀积
  i=0 (最左):  左侧无(=1) × postfix[len-2]=postfix[2]=24        → 24   (= 2×3×4)
  i=1:         prefix[0]=1 × postfix[len-2-1]=postfix[1]=12     → 12   (= 1×3×4)
  i=2:         prefix[1]=2 × postfix[len-2-2]=postfix[0]=4      →  8   (= 1×2×4)
  i=3 (最右):  prefix[len-2]=prefix[2]=6 × 右侧无(=1)           →  6   (= 1×2×3)

answer = [24, 12, 8, 6]
```

### 方法一：前缀积 + 后缀积（O(n) 空间）

```csharp
public class Solution
{
    public int[] ProductExceptSelf(int[] nums)
    {
        int len = nums.Length;
        int[] answer = new int[len];

        // prefix[i] = nums[0] × ... × nums[i]   （左侧前缀积，含 nums[i]）
        int[] prefix = new int[len];
        // postfix[i] = nums[len-1-i] × ... × nums[len-1]  （右侧后缀积，含末尾 i+1 个元素）
        int[] postfix = new int[len];

        // 初始：前缀积首元素 = nums[0]；后缀积首元素 = 最后一个元素
        prefix[0] = nums[0];
        postfix[0] = nums[len - 1];

        // 正向累乘构造 prefix，反向累乘构造 postfix
        for (int i = 1; i < len; i++)
        {
            prefix[i] = nums[i] * prefix[i - 1];
            postfix[i] = nums[len - 1 - i] * postfix[i - 1];
        }

        // answer[i] = 左侧前缀积(nums[0..i-1]) × 右侧后缀积(nums[i+1..len-1])
        for (int i = 0; i < len; i++)
        {
            if (i == 0)
            {
                // 最左侧：左侧无元素（视为 1），answer[0] = 右侧后缀积 = postfix[len-2]
                answer[i] = postfix[len - 2];
            }
            else if (i == len - 1)
            {
                // 最右侧：右侧无元素（视为 1），answer[len-1] = 左侧前缀积 = prefix[len-2]
                answer[i] = prefix[len - 2];
            }
            else
            {
                // 中间：左侧 = prefix[i-1]，右侧 = postfix[len-2-i]
                answer[i] = prefix[i - 1] * postfix[len - i - 2];
            }
        }

        return answer;
    }
}
```

| 复杂度 | |
|--------|------|
| 时间 | O(n)，两次遍历构造前缀/后缀积，一次遍历填 answer |
| 空间 | O(n)，额外用了 `prefix` 和 `postfix` 两个数组 |

### 方法二：前缀积 + 滚动后缀积（O(1) 空间）⭐ 推荐

方法一用了两个辅助数组。观察到 `answer` 数组本身就是结果，可以**复用它**：先在 `answer` 里存好左侧前缀积，再从右往左用一个变量 `right` 滚动累乘右侧后缀积，直接乘进 `answer[i]`。这样省掉 `prefix` 和 `postfix` 两个数组，额外空间降到 O(1)。

```
nums = [1, 2, 3, 4]   (len = 4)

第一遍：从左到右，令 answer[i] = nums[0..i-1] 的前缀积（不含 nums[i]）
  answer[0] = 1                                   → answer = [1, _, _, _]
  answer[1] = answer[0] × nums[0] = 1 × 1 = 1     → answer = [1, 1, _, _]
  answer[2] = answer[1] × nums[1] = 1 × 2 = 2     → answer = [1, 1, 2, _]
  answer[3] = answer[2] × nums[2] = 2 × 3 = 6     → answer = [1, 1, 2, 6]
  此时 answer[i] 已是"左侧前缀积"

第二遍：从右到左，用 right 滚动累乘右侧后缀积，乘进 answer[i]
  right 初始 = 1（最右侧无元素，后缀积为 1）
  i=3: answer[3] = 6 × right(1)  = 6;  right = 1 × nums[3]=4        → answer=[1,1,2,6]
  i=2: answer[2] = 2 × right(4)  = 8;  right = 4 × nums[2]=12       → answer=[1,1,8,6]
  i=1: answer[1] = 1 × right(12) = 12; right = 12 × nums[1]=24      → answer=[1,12,8,6]
  i=0: answer[0] = 1 × right(24) = 24; right = 24 × nums[0]=24      → answer=[24,12,8,6]

answer = [24, 12, 8, 6]   与方法一结果一致
```

```csharp
public class Solution {
    public int[] ProductExceptSelf(int[] nums) {
        int len = nums.Length;
        int[] answer = new int[len];
        // 第一遍：从左到右，prefix 始终 = nums[0..i-1] 的前缀积（不含 nums[i]）
        int prefix = 1;
        for(int i=0;i<len;i++){
            answer[i] = prefix;   // 先存入当前位置的左侧前缀积
            prefix *= nums[i];    // 再更新 prefix，为下一个（右侧）位置做准备
        }
        // 第二遍：从右到左，suffix 始终 = nums[i+1..len-1] 的后缀积（不含 nums[i]）
        int suffix = 1;
        for(int i =len-1;i>=0;i--){
            answer[i] *= suffix;  // 左前缀积 × 右后缀积 = 最终结果
            suffix *= nums[i];    // 更新 suffix，为下一个（更左的）位置做准备
        }

        return answer;
    }
}
```

| 复杂度 | |
|--------|------|
| 时间 | O(n)，从左到右一次 + 从右到左一次，共两次遍历 |
| 空间 | **O(1)**，仅用 `right` 一个变量（`answer` 是结果数组，不计入额外空间） |

### 两种方法对比

| | 方法一：双数组 | 方法二：滚动后缀积 ⭐ |
|------|------|------|
| **时间** | O(n) | O(n) |
| **空间** | O(n) | **O(1)** |
| **核心技巧** | 预处理前缀/后缀两张表 | `answer` 复用 + 单变量滚动累乘 |
| **可读性** | 直观，索引关系一目了然 | 更精炼，需理解滚动累乘思想 |

> **选择建议**：方法二是面试**标准最优解** —— 时间 O(n)、额外空间 O(1)，是题目进阶要求的标准答案。方法一更直观易懂，适合作为推导跳板。建议**先吃透方法一**理解前缀/后缀积的本质，**再过渡到方法二**掌握空间优化的复用技巧。

---
## 核心技巧

- 动态规划
- 原地修改（in-place）
- 前缀和 / 后缀和
- 差分数组
- 合并、轮转、去重

---

> 📎 标签：`数组` `前缀和` `差分`
