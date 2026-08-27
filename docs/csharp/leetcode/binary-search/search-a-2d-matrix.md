# 搜索二维矩阵

> [LeetCode 74. Search a 2D Matrix](https://leetcode.cn/problems/search-a-2d-matrix/) - Medium
>
> 学习状态：已完成 C++ 练习
>
> 练习日期：2026-08-27
>
> 本次实现：C++，二维矩阵全局二分
>
> 验证状态：用户放入知识库前已完成练习；本次整理未重复运行 LeetCode 判题
>
> 证据归属：用户 `inbox/8月27号leetcode.txt` 原始记录

## 学习目标

- 识别 LC74 的矩阵不是普通“行列有序”，而是整张表可以串成一个升序数组。
- 掌握二维下标和一维下标之间的映射：`row = mid / n`，`col = mid % n`。
- 用一次二分达到 O(log(m * n))。

## 题意与核心思路

矩阵满足两条性质：

```text
每一行从左到右非严格递增
每一行第一个元素 > 前一行最后一个元素
```

这意味着把矩阵按行展开后，整体就是一个有序数组：

```text
matrix = [[1, 3, 5],
          [7, 9, 11]]

展开后 = [1, 3, 5, 7, 9, 11]
```

因此可以在 `[0, m * n - 1]` 这个一维下标区间上做二分，每次再映射回矩阵坐标。

## 推荐写法：一次全局二分

```cpp
class Solution
{
public:
    bool searchMatrix(vector<vector<int>>& matrix, int target)
    {
        int m = static_cast<int>(matrix.size());
        int n = static_cast<int>(matrix[0].size());
        int left = 0;
        int right = m * n - 1;

        while (left <= right)
        {
            int mid = left + (right - left) / 2;
            int value = matrix[mid / n][mid % n];

            if (value == target)
            {
                return true;
            }

            if (value < target)
            {
                left = mid + 1;
            }
            else
            {
                right = mid - 1;
            }
        }

        return false;
    }
};
```

这里的关键不是二维遍历，而是把二维坐标当成一维有序序列的视图：

| 一维下标 | 行 | 列 |
|---:|---:|---:|
| `mid` | `mid / n` | `mid % n` |

## 方法对比

| 方法 | 时间 | 空间 | 说明 |
|---|---:|---:|---|
| 一次全局二分 | O(log(m * n)) | O(1) | 直接利用整张矩阵全局有序，是本题推荐写法 |
| 先找行再行内二分 | O(log m + log n) | O(1) | 也可行，但边界更多，代码更容易写散 |
| 逐行扫描 / 暴力 | O(mn) | O(1) | 没用上题目要求的对数复杂度 |

## 与 LC240 的区别

LC74 和 [搜索二维矩阵 II](../matrix/search-a-2d-matrix-ii.md) 很像，但有一个关键差异：

| 题目 | 矩阵性质 | 推荐解法 |
|---|---|---|
| LC74 | 每行有序，且下一行首元素大于上一行尾元素 | 全局二分 O(log(mn)) |
| LC240 | 每行有序，每列有序，但行与行不能串成一维全局有序 | 右上 / 左下 Z 字查找 O(m+n) |

## 常见错误

- 把 LC74 当成 LC240，使用 Z 字查找虽然能做部分有序矩阵题，但没有体现本题 O(log(mn)) 目标。
- 二维映射写反：列数是 `n`，所以行是 `mid / n`，列是 `mid % n`。
- `right = m * n - 1` 前没有确认矩阵非空；LeetCode 约束通常保证非空，普通工程应额外防御。
- `mid = (left + right) / 2` 在极端下标下可能溢出，优先写 `left + (right - left) / 2`。

## 如何验证

至少覆盖：

- 命中：`[[1,3,5,7],[10,11,16,20],[23,30,34,60]], target = 3 -> true`。
- 不存在：同一矩阵中 `target = 13 -> false`。
- 小于最小值：`target = 0 -> false`。
- 大于最大值：`target = 61 -> false`。
- 单行、单列和单元素矩阵。

本次整理遵循 LeetCode Inbox 规则：用户主动放入题解默认视为放入前已完成练习；当前智能体没有重新创建 C++ 工程或提交 LeetCode 复测。

## 相关内容

- 专题：[二分查找](index.md)
- 对比题：[搜索二维矩阵 II](../matrix/search-a-2d-matrix-ii.md)
- C++：[刷题模板与易错点](../../../cpp/leetcode/templates.md)

> 标签：`二分查找` `矩阵` `二维映射` `C++`
