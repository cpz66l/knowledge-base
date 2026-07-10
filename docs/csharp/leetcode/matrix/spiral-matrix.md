# 螺旋矩阵 ⭐ 重点

> [LeetCode 54. Spiral Matrix](https://leetcode.cn/problems/spiral-matrix/) - Medium

!!! warning "高频重点"
    矩阵**模拟**的经典题，"边界收缩法"的代表。面试高频，思路直接迁移到"螺旋矩阵 II（生成）"、"顺时针旋转图像"等同类题。务必掌握四边界收缩 + 单行/单列特判的写法。

给你一个 `m` 行 `n` 列的矩阵 `matrix`，请按照**顺时针螺旋顺序**，返回矩阵中的所有元素。

**核心思路：**

用四个边界变量圈定当前还没遍历的"圈"：`topRow`、`bottomRow`、`leftCol`、`rightCol`。按 **右 → 下 → 左 → 上** 顺时针走一圈，每走完一边就把对应边界向内收缩一格。关键细节：**每走完一边要检查是否只剩一行/一列**，若是则立即 `break`，避免把同一行/列重复遍历。

```
matrix = [[1, 2, 3],
          [4, 5, 6],
          [7, 8, 9]]   (3x3)

初始边界：top=0, bottom=2, left=0, right=2

第 1 圈：
  -> 左到右（top 行）：1 2 3        走完 top++  -> top=1
  ↓  上到下（right 列）：6 9         走完 right-- -> right=1
  <- 右到左（bottom 行）：8 7       走完 bottom-- -> bottom=1
  ↑  下到上（left 列）：4            走完 left++  -> left=1
  已收集：1 2 3 6 9 8 7 4

第 2 圈：
  -> 左到右（top=1 行）：5           走完 top++ 后 top(2) == bottom(1)? 其实走完即检查 -> 只剩一行 break
  已收集：1 2 3 6 9 8 7 4 5

结果 = [1, 2, 3, 6, 9, 8, 7, 4, 5]
```

```csharp
public class Solution
{
    public IList<int> SpiralOrder(int[][] matrix)
    {
        List<int> res = new List<int>();
        int topRow = 0;
        int bottomRow = matrix.Length - 1;
        int leftCol = 0;
        int rightCol = matrix[0].Length - 1;

        while (true)
        {
            // 1. 左到右：遍历当前最上面一行
            for (int i = leftCol; i <= rightCol; i++)
            {
                res.Add(matrix[topRow][i]);
            }
            if (topRow == bottomRow) break;   // 只剩一行，走完即结束
            topRow++;

            // 2. 上到下：遍历当前最右边一列
            for (int i = topRow; i <= bottomRow; i++)
            {
                res.Add(matrix[i][rightCol]);
            }
            if (leftCol == rightCol) break;   // 只剩一列，走完即结束
            rightCol--;

            // 3. 右到左：遍历当前最下面一行
            for (int i = rightCol; i >= leftCol; i--)
            {
                res.Add(matrix[bottomRow][i]);
            }
            if (topRow == bottomRow) break;   // 上下边界相遇，结束
            bottomRow--;

            // 4. 下到上：遍历当前最左边一列
            for (int i = bottomRow; i >= topRow; i--)
            {
                res.Add(matrix[i][leftCol]);
            }
            if (leftCol == rightCol) break;   // 左右边界相遇，结束
            leftCol++;
        }

        return res;
    }
}
```

| 复杂度 | |
|--------|------|
| 时间 | O(m·n)，每个元素恰好被访问一次 |
| 空间 | O(1)，不计结果列表（结果列表 O(m·n)） |

!!! tip "边界收缩法的通用性"
    同一套四边界收缩思路可用于：**螺旋矩阵 II**（生成 n×n 螺旋矩阵，把"读"改成"写"）、**顺时针旋转图像**（先转置再每行翻转）。另一种等价写法是用**方向数组** `dirs = [(0,1),(1,0),(0,-1),(-1,0)]` + `visited` 标记，碰到边界或已访问就转向 -- 思路不同但复杂度一致。

---

> 📎 标签：`矩阵` `螺旋遍历` `边界收缩` `模拟`
