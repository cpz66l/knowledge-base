# 除自身以外数组的乘积 ⭐ 重点

> [LeetCode 238. Product of Array Except Self](https://leetcode.cn/problems/product-of-array-except-self/) - Medium

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
  prefix[0] = 1                     -> prefix = [1,  _,  _,  _]
  prefix[1] = 2 × prefix[0] =  2    -> prefix = [1,  2,  _,  _]
  prefix[2] = 3 × prefix[1] =  6    -> prefix = [1,  2,  6,  _]
  prefix[3] = 4 × prefix[2] = 24    -> prefix = [1,  2,  6, 24]

第二步：构造后缀积 postfix[i] = nums[len-1-i .. len-1] 的乘积（从右往左累乘）
  postfix[0] = nums[3] = 4                  -> postfix = [ 4,  _,  _,  _]
  postfix[1] = nums[2] × postfix[0] = 12    -> postfix = [ 4, 12,  _,  _]
  postfix[2] = nums[1] × postfix[1] = 24    -> postfix = [ 4, 12, 24,  _]
  postfix[3] = nums[0] × postfix[2] = 24    -> postfix = [ 4, 12, 24, 24]

第三步：answer[i] = 左侧前缀积 × 右侧后缀积
  i=0 (最左):  左侧无(=1) × postfix[len-2]=postfix[2]=24        -> 24   (= 2×3×4)
  i=1:         prefix[0]=1 × postfix[len-2-1]=postfix[1]=12     -> 12   (= 1×3×4)
  i=2:         prefix[1]=2 × postfix[len-2-2]=postfix[0]=4      ->  8   (= 1×2×4)
  i=3 (最右):  prefix[len-2]=prefix[2]=6 × 右侧无(=1)           ->  6   (= 1×2×3)

answer = [24, 12, 8, 6]
```

## 方法一：前缀积 + 后缀积（O(n) 空间）

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

## 方法二：前缀积 + 滚动后缀积（O(1) 空间）⭐ 推荐

方法一用了两个辅助数组。观察到 `answer` 数组本身就是结果，可以**复用它**：先在 `answer` 里存好左侧前缀积，再从右往左用一个变量 `right` 滚动累乘右侧后缀积，直接乘进 `answer[i]`。这样省掉 `prefix` 和 `postfix` 两个数组，额外空间降到 O(1)。

```
nums = [1, 2, 3, 4]   (len = 4)

第一遍：从左到右，令 answer[i] = nums[0..i-1] 的前缀积（不含 nums[i]）
  answer[0] = 1                                   -> answer = [1, _, _, _]
  answer[1] = answer[0] × nums[0] = 1 × 1 = 1     -> answer = [1, 1, _, _]
  answer[2] = answer[1] × nums[1] = 1 × 2 = 2     -> answer = [1, 1, 2, _]
  answer[3] = answer[2] × nums[2] = 2 × 3 = 6     -> answer = [1, 1, 2, 6]
  此时 answer[i] 已是"左侧前缀积"

第二遍：从右到左，用 right 滚动累乘右侧后缀积，乘进 answer[i]
  right 初始 = 1（最右侧无元素，后缀积为 1）
  i=3: answer[3] = 6 × right(1)  = 6;  right = 1 × nums[3]=4        -> answer=[1,1,2,6]
  i=2: answer[2] = 2 × right(4)  = 8;  right = 4 × nums[2]=12       -> answer=[1,1,8,6]
  i=1: answer[1] = 1 × right(12) = 12; right = 12 × nums[1]=24      -> answer=[1,12,8,6]
  i=0: answer[0] = 1 × right(24) = 24; right = 24 × nums[0]=24      -> answer=[24,12,8,6]

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

## 两种方法对比

| | 方法一：双数组 | 方法二：滚动后缀积 ⭐ |
|------|------|------|
| **时间** | O(n) | O(n) |
| **空间** | O(n) | **O(1)** |
| **核心技巧** | 预处理前缀/后缀两张表 | `answer` 复用 + 单变量滚动累乘 |
| **可读性** | 直观，索引关系一目了然 | 更精炼，需理解滚动累乘思想 |

> **选择建议**：方法二是面试**标准最优解** -- 时间 O(n)、额外空间 O(1)，是题目进阶要求的标准答案。方法一更直观易懂，适合作为推导跳板。建议**先吃透方法一**理解前缀/后缀积的本质，**再过渡到方法二**掌握空间优化的复用技巧。
