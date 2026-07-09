# 矩阵

> 二维遍历 · 方向数组 · 螺旋/旋转 — 行列索引游戏

---

## 题目列表

<!-- TODO: 添加题目 -->
给定一个 m x n 的矩阵，如果一个元素为 0 ，则将其所在行和列的所有元素都设为 0 。请使用 原地 算法。

易想方法：
public class Solution {
    public void SetZeroes(int[][] matrix) {
        int m = matrix.Length;
        int[][] copy = new int[m][];
        int n = matrix[0].Length;
        for(int i =0;i<m;i++){
            copy[i] = new int[n];
            Array.Copy(matrix[i],copy[i],n);
        }

        for(int i=0;i<m;i++){
            for(int j=0;j<n;j++){
                if(matrix[i][j] == 0){
                    for(int row=0;row<m;row++){
                        copy[row][j] = 0;
                    }
                    for(int col=0;col<n;col++){
                        copy[i][col] = 0;
                    }
                }
            }
        }

        for(int i=0;i<m;i++){
            Array.Copy(copy[i],matrix[i],n);
        }
    }
}

进阶方法
---

## 核心技巧

- 方向数组 `int[][] dirs`
- 边界收缩法（螺旋遍历）
- 原地旋转：转置 + 翻转
- 行列标记法

---

> 📎 标签：`矩阵` `二维数组` `模拟`
