# 双指针

> 快慢指针 / 左右对撞 — 降 O(n²) 为 O(n)

---

## 题目列表

### 盛最多水的容器

> [LeetCode 11. Container With Most Water](https://leetcode.cn/problems/container-with-most-water/) — Medium

给定一个长度为 `n` 的整数数组 `height`，有 `n` 条垂线，第 `i` 条线的两个端点是 `(i, 0)` 和 `(i, height[i])`。找出其中的两条线，使得它们与 `x` 轴共同构成的容器可以容纳最多的水。返回容器可以储存的最大水量。

**核心思路：**

左右指针从两端向中间收敛。面积由**宽度 × 较矮高度**决定。每次移动**较矮**的那一侧 — 因为宽度一定在缩小，只有增加高度才有可能找到更大的面积。两个指针相遇时结束。

```csharp
public class Solution
{
    public int MaxArea(int[] height)
    {
        // 左指针从数组最左边出发
        int left = 0;
        // 右指针从数组最右边出发
        int right = height.Length - 1;
        // 记录全局最大水量
        int max = 0;

        // 左右指针相遇时停止（宽度为 0 没有意义）
        while (left < right)
        {
            // 当前容器的宽度 = 右下标 - 左下标
            int width = right - left;
            // 容器高度由较矮的那条线决定（短板效应）
            int minHeight = height[left] < height[right] ? height[left] : height[right];
            // 当前水量 = 宽 × 高
            int capacity = width * minHeight;
            // 更新最大值
            if (capacity > max) max = capacity;

            // 核心贪心：移动较矮一侧的指针
            // 宽度每轮一定在缩小，只有增加高度才可能更大
            if (height[left] < height[right])
                left++;   // 左边较矮 → 左指针右移，尝试找更高的线
            else
                right--;  // 右边较矮 → 右指针左移，尝试找更高的线
        }

        return max;
    }
}
```

| 复杂度 | |
|--------|------|
| 时间 | O(n)，每个元素最多被访问一次 |
| 空间 | O(1)，只用了两个指针变量 |

---

## 核心技巧

- 快慢指针：环检测、链表中点、去重
- 左右指针：对撞、有序数组两数之和
- 三指针：三数之和、接雨水

---

> 📎 标签：`双指针` `快慢指针` `对撞指针`
