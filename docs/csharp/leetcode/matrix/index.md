# 矩阵

> 二维遍历 · 方向数组 · 螺旋/旋转 - 行列索引游戏

---
给定一个 n × n 的二维矩阵 matrix 表示一个图像。请你将图像顺时针旋转 90 度。

你必须在 原地 旋转图像，这意味着你需要直接修改输入的二维矩阵。请不要 使用另一个矩阵来旋转图像。

顺时针90°:先主对角线转置，再每行左右交换
public class Solution {
    public void Rotate(int[][] matrix) {
        int n = matrix.Length;

        for(int i = 0 ;i<n ; i++){
            for(int j = i+1 ; j<n;j++){
                int temp = matrix[i][j];
                matrix[i][j] = matrix[j][i];
                matrix[j][i] = temp;
            }
        }

        for(int i = 0;i<n ;i++){
            int l = 0;
            int r = n-1;
            while(l<r){
                int temp = matrix[i][l];
                matrix[i][l] = matrix[i][r];
                matrix[i][r] = temp;
                l++;
                r--;
            }

        }
    }
}

其他旋转方向：
逆时针90°：先每行左右交换，再主对角线转置；
旋转180°：主对角线转置，再副对角线转置。(或者左右+上下翻转)
主要是考察矩阵旋转的数学表达对应的代码的实现。
## 题目列表

| 题目 | 难度 | 核心技巧 |
|------|------|----------|
| [矩阵置零](set-matrix-zeroes.md) | Medium | 原地标记、首行首列复用 |
| [螺旋矩阵](spiral-matrix.md) | Medium | 边界收缩、顺时针模拟 |

---

## 核心技巧

- 方向数组 `int[][] dirs`
- 边界收缩法（螺旋遍历）
- 原地旋转：转置 + 翻转
- 行列标记法

---

> 📎 标签：`矩阵` `二维数组` `模拟`
