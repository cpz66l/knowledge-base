# 双指针

> 快慢指针 / 左右对撞 — 降 O(n²) 为 O(n)

---

## 题目列表

### 盛最多水的容器

> [LeetCode 11. Container With Most Water](https://leetcode.cn/problems/container-with-most-water/) — Medium

给定一个长度为 `n` 的整数数组 `height`，有 `n` 条垂线，第 `i` 条线的两个端点是 `(i, 0)` 和 `(i, height[i])`。找出其中的两条线，使得它们与 `x` 轴共同构成的容器可以容纳最多的水。返回容器可以储存的最大水量。

**核心思路：**

左右指针从两端向中间收敛。面积由**宽度 × 较矮高度**决定。每次移动**较矮**的那一侧 — 因为宽度一定在缩小，只有增加高度才有可能找到更大的面积。

```
   left →           ← right
    |                 |
    8                 7
    |                 |
    |    6     6      |
    |    |     |      |
    |    |  3  |  5   |
    |____|__|__|__|___|
          ← w →
    area = min(8,7) × w
```

哪个矮移哪个：`height[left] < height[right]` → `left++`，否则 `right--`。

```csharp
public class Solution
{
    public int MaxArea(int[] height)
    {
        // 1. 左右指针初始化：指向数组两端
        int left = 0;
        int right = height.Length - 1;
        int maxArea = 0;

        // 2. 指针相遇时结束（宽度为 0 没有意义）
        while (left < right)
        {
            // 计算当前容器的宽度和高度（取较矮的那条线）
            int width = right - left;
            int minHeight = height[left] < height[right] ? height[left] : height[right];
            int area = width * minHeight;

            // 更新最大面积
            if (area > maxArea) maxArea = area;

            // 3. 移动较矮一侧的指针（保留较高的那条，才有可能更大）
            if (height[left] < height[right])
                left++;
            else
                right--;
        }

        return maxArea;
    }
}
```

| 复杂度 | |
|--------|------|
| 时间 | O(n)，每个元素最多被访问一次 |
| 空间 | O(1)，只用了两个指针 |

---

### 三数之和

> [LeetCode 15. 3Sum](https://leetcode.cn/problems/3sum/) — Medium

给你一个整数数组 `nums`，判断是否存在三元组 `[nums[i], nums[j], nums[k]]` 满足 `i != j`、`i != k` 且 `j != k`，同时还满足 `nums[i] + nums[j] + nums[k] == 0`。返回所有和为 0 且不重复的三元组。

**核心思路：**

先排序，固定第一个数，然后在剩余区间用双指针做两数之和。关键：三个位置都需要**跳过重复值**，否则结果集会包含重复三元组。

```
排序后：[-4, -1, -1, 0, 1, 2]
         ↑    ↑            ↑
       固定   left        right

固定第一个 -1 时：left 指向 0，right 指向 2，和 = -1+0+2 = 1 → 大了 → right--
                left 指向 0，right 指向 1，和 = -1+0+1 = 0 ✓ → 记录 → left++, right--
                跳过 left 重复值 → left 指向 2，left >= right → 结束
```

```csharp
public class Solution
{
    public IList<IList<int>> ThreeSum(int[] nums)
    {
        List<IList<int>> result = new List<IList<int>>();

        // 1. 排序：让双指针策略可行
        Array.Sort(nums);

        // 2. 固定第一个数 a
        for (int i = 0; i < nums.Length - 2; i++)
        {
            // 如果最小的数都 > 0，后面不可能和为 0
            if (nums[i] > 0) break;

            // 跳过 a 的重复值（避免重复三元组）
            if (i > 0 && nums[i] == nums[i - 1]) continue;

            int a = nums[i];

            // 3. 左右双指针在剩余区间做两数之和
            int left = i + 1;
            int right = nums.Length - 1;

            while (left < right)
            {
                int sum = a + nums[left] + nums[right];

                if (sum < 0)
                    left++;          // 和太小 → 增大左指针的值
                else if (sum > 0)
                    right--;         // 和太大 → 减小右指针的值
                else
                {
                    // 找到一组解
                    result.Add(new List<int> { a, nums[left], nums[right] });

                    // 跳过 left 的重复值
                    while (left < right && nums[left] == nums[left + 1]) left++;
                    // 跳过 right 的重复值
                    while (left < right && nums[right] == nums[right - 1]) right--;

                    // 继续搜下一组
                    left++;
                    right--;
                }
            }
        }

        return result;
    }
}
```

| 复杂度 | |
|--------|------|
| 时间 | O(n²)，排序 O(n log n) + 外层 O(n) × 内层双指针 O(n) |
| 空间 | O(1)，不计结果集（排序可能额外 O(log n) 递归栈） |

---

### 移动零

> [LeetCode 283. Move Zeroes](https://leetcode.cn/problems/move-zeroes/) — Easy

给定一个数组 `nums`，将所有 0 移动到数组的末尾，同时保持非零元素的相对顺序。必须**原地**操作。

**核心思路：**

快慢指针（同向）。快指针扫描所有元素，遇到非零就换到慢指针位置，慢指针前进。扫描完后，慢指针到数组末尾全部填 0。

```
扫描过程示例：
[0, 1, 0, 3, 12]
 ↓s  ↓f           f 指向 0 → 跳过
[0, 1, 0, 3, 12]
 ↓s     ↓f        f 指向 1 → nums[s] = nums[f] → [1, 1, 0, 3, 12] → s++
[1, 1, 0, 3, 12]
    ↓s     ↓f     f 指向 0 → 跳过
[1, 1, 0, 3, 12]
    ↓s        ↓f  f 指向 3 → nums[s] = nums[f] → [1, 3, 0, 3, 12] → s++
...
```

```csharp
public class Solution
{
    public void MoveZeroes(int[] nums)
    {
        // 1. 慢指针：指向"下一个非零元素应该放置的位置"
        int slow = 0;

        // 2. 快指针：扫描整个数组
        for (int fast = 0; fast < nums.Length; fast++)
        {
            // 遇到非零数，交换到 slow 位置，然后 slow 前移
            if (nums[fast] != 0)
            {
                int temp = nums[slow];
                nums[slow] = nums[fast];
                nums[fast] = temp;
                slow++;
            }
            // 遇到 0 则跳过，fast 继续前进
        }
        // 循环结束后，slow 及其之后位置自然全为 0
    }
}
```

| 复杂度 | |
|--------|------|
| 时间 | O(n)，快指针遍历一次数组 |
| 空间 | O(1)，原地交换 |

---

## 双指针三种形态

| 形态 | 指针位置 | 典型题目 |
|------|----------|----------|
| **左右对撞** | 一头一尾向中间收 | 盛水容器、两数之和 II |
| **快慢指针** | 同向一快一慢 | 移动零、去重、环检测 |
| **固定 + 对撞** | 固定一个 + 剩余区间左右对撞 | 三数之和、四数之和 |

---

## 核心技巧

- 排序 + 双指针是处理"和/差"类问题的经典组合
- 移动较矮一侧（盛水） vs 移动值较小一侧（两数之和） — 口诀相似，逻辑不同
- 去重时先记录再跳过，别反过来（否则会漏解）
- 快慢指针的精髓：慢指针始终指向"已处理区间"的下一个位置

---

> 📎 标签：`双指针` `快慢指针` `对撞指针`
