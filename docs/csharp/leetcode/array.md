# 数组

> 遍历 · 原地操作 · 前缀后缀 — 最基础也最常考的数据结构

---

## 题目列表

<!-- TODO: 添加题目 -->
给你一个整数数组 nums ，请你找出一个具有最大和的连续子数组（子数组最少包含一个元素），返回其最大和。

子数组是数组中的一个连续部分。

public class Solution {
    public int MaxSubArray(int[] nums) {
        int currentMax = nums[0];
        int maxSum = nums[0];
        for(int i=1;i<nums.Length;i++){
            currentMax = Math.Max(nums[i],nums[i]+currentMax);
            maxSum = Math.Max(maxSum,currentMax);
        }
        return maxSum;
    }
}
---

## 核心技巧

- 动态规划
- 原地修改（in-place）
- 前缀和 / 后缀和
- 差分数组
- 合并、轮转、去重

---

> 📎 标签：`数组` `前缀和` `差分`
