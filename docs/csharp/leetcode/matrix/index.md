# 矩阵

> 二维遍历 · 方向数组 · 螺旋/旋转 - 行列索引游戏

---
给你一个 m 行 n 列的矩阵 matrix ，请按照 顺时针螺旋顺序 ，返回矩阵中的所有元素。
public class Solution {
    public IList<int> SpiralOrder(int[][] matrix) {
        List<int> res = new List<int>();
        int topRow = 0;
        int bottomRow = matrix.Length-1;
        int leftCol = 0;
        int rightCol = matrix[0].Length-1;

        while(true)
        {
            //左到右
            for(int i = leftCol;i <= rightCol;i++){
                res.Add(matrix[topRow][i]);
            }
            if(topRow == bottomRow) break;
            topRow++;
            //上到下
            for(int i = topRow;i<=bottomRow;i++){
                res.Add(matrix[i][rightCol]);
            }
            if(leftCol == rightCol) break;
            rightCol--;
            //右到左
            for(int i = rightCol ;i>=leftCol ;i--){
                res.Add(matrix[bottomRow][i]);
            }
            if(topRow == bottomRow) break;
            bottomRow--;
            //下到上
            for(int i = bottomRow;i>=topRow;i--){
                res.Add(matrix[i][leftCol]);
            }
            if(leftCol == rightCol) break;
            leftCol++;
        }

        return res;
    }
}
## 题目列表

| 题目 | 难度 | 核心技巧 |
|------|------|----------|
| [矩阵置零](set-matrix-zeroes.md) | Medium | 原地标记、首行首列复用 |

---

## 核心技巧

- 方向数组 `int[][] dirs`
- 边界收缩法（螺旋遍历）
- 原地旋转：转置 + 翻转
- 行列标记法

---

> 📎 标签：`矩阵` `二维数组` `模拟`
