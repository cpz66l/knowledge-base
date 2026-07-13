# 矩阵

> 二维遍历 · 方向数组 · 螺旋/旋转 - 行列索引游戏

编写一个高效的算法来搜索 m x n 矩阵 matrix 中的一个目标值 target 。该矩阵具有以下特性：

每行的元素从左到右升序排列。
每列的元素从上到下升序排列。

public class Solution {
    public bool SearchMatrix(int[][] matrix, int target) {
        int m = matrix.Length;
        int n = matrix[0].Length;

        int i = m-1;
        int j = 0;
        while(j<n && i >=0){
            if(matrix[i][j]>target){
                i--;
            }
            else if(matrix[i][j]<target){
                j++;
            }
            else return true;
        }
        return false;
    }
}
---
## 题目列表

| 题目 | 难度 | 核心技巧 |
|------|------|----------|
| [矩阵置零](set-matrix-zeroes.md) | Medium | 原地标记、首行首列复用 |
| [螺旋矩阵](spiral-matrix.md) | Medium | 边界收缩、顺时针模拟 |
| [旋转图像](rotate-image.md) | Medium | 转置 + 翻转、原地旋转 |

---

## 核心技巧

- 方向数组 `int[][] dirs`
- 边界收缩法（螺旋遍历）
- 原地旋转：转置 + 翻转
- 行列标记法

---

> 📎 标签：`矩阵` `二维数组` `模拟`
