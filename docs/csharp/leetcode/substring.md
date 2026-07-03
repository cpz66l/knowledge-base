# 子串

> 子串问题套路 — 前缀和、KMP、动态规划

---

## 题目列表

<!-- TODO: 添加题目 -->
给你一个整数数组 nums 和一个整数 k ，请你统计并返回 该数组中和为 k 的子数组的个数。
子数组是数组中元素的连续非空序列。
1.双指针暴力解法
public class Solution {
    public int SubarraySum(int[] nums, int k) {
        if(nums.Length == 0) return 0 ;
        int N = 0;
        int left = 0;
        while(left<nums.Length){
            int sum = 0;
            for(int right = left;right<nums.Length;right++){
                sum+=nums[right];
                if(sum == k) N++;
            }
            left++;
        }
        return N;
    }
}

2.前缀和 + 哈希表
public class Solution {
    public int SubarraySum(int[] nums, int k) {
        Dictionary<int, int> map = new Dictionary<int, int>();
        map[0] = 1;
        int count = 0;
        int curSum = 0;
        foreach(int num in nums){
            curSum +=  num;
            int target = curSum - k;
            if(map.ContainsKey(target)){
                count += map[target];
            }
            if(map.ContainsKey(curSum)){
                map[curSum]++;
            }
            else map[curSum] = 1;
        }
        return count ;
    }
}
---

## 核心技巧

- 前缀和 + 哈希表
- 回文子串：中心扩展 / DP
- KMP 字符串匹配（了解思想即可，面试低频）

---

> 📎 标签：`子串` `前缀和` `回文`
