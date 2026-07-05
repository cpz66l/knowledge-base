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
            curMax = Math.Max(nums[i], nums[i] + curMax);//核心：状态转移方程
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

> **选择建议**：Kadane 算法是这题的**标准解法**，O(n) 时间 O(1) 空间已是最优。分治法虽然慢一些，但体现了"最大子数组"问题的分治本质，面试官可能会追问了解你的算法广度。

---

## 核心技巧

- 动态规划
- 原地修改（in-place）
- 前缀和 / 后缀和
- 差分数组
- 合并、轮转、去重

---

> 📎 标签：`数组` `前缀和` `差分`
