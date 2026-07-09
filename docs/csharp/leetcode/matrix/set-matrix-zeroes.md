# 矩阵置零 ⭐ 重点

> [LeetCode 73. Set Matrix Zeroes](https://leetcode.cn/problems/set-matrix-zeroes/) - Medium

!!! warning "高频重点"
    矩阵**原地操作**的经典题，"标记法"的代表。LeetCode 明确进阶要求 **O(1) 额外空间**，是面试高频追问点。掌握从 O(mn) 到 O(1) 的三段式空间优化思路，可迁移到所有"先记录再统一处理"的题型。

给定一个 `m x n` 的矩阵，如果一个元素为 `0`，则将其所在行和列的所有元素都设为 `0`。要求使用**原地**算法。

**核心思路：**

难点在于**不能边遍历边置 0** -- 否则后填的 0 会污染后续判断，把不该清的也清了。所以必须先"记录"哪些行、哪些列需要清零，再统一处理。记录方式的空间优化就是本题的进阶核心：

- **O(mn)**：复制整个矩阵作副本（方法一，你的易想方法）
- **O(m+n)**：用两个标记数组分别记录要清零的行和列
- **O(1)**：把这两个标记数组直接塞进矩阵的**首行**和**首列**（方法二，进阶）

## 方法一：复制矩阵（O(mn) 空间）

开一个矩阵副本，遍历原矩阵发现 0 就在副本上清零对应整行整列，最后把副本拷回原矩阵。副本隔离了"读原矩阵"和"写副本"，避免污染。

```csharp
public class Solution
{
    public void SetZeroes(int[][] matrix)
    {
        int m = matrix.Length;
        int n = matrix[0].Length;

        // 1. 复制整个矩阵作为"写"副本，与原矩阵隔离，避免边写边读的污染
        int[][] copy = new int[m][];
        for (int i = 0; i < m; i++)
        {
            copy[i] = new int[n];
            Array.Copy(matrix[i], copy[i], n);
        }

        // 2. 遍历原矩阵，发现 0 就在副本上把对应整行整列清零
        for (int i = 0; i < m; i++)
        {
            for (int j = 0; j < n; j++)
            {
                if (matrix[i][j] == 0)
                {
                    // 把第 j 列全部清零
                    for (int row = 0; row < m; row++)
                    {
                        copy[row][j] = 0;
                    }
                    // 把第 i 行全部清零
                    for (int col = 0; col < n; col++)
                    {
                        copy[i][col] = 0;
                    }
                }
            }
        }

        // 3. 把副本拷回原矩阵（原地写出结果）
        for (int i = 0; i < m; i++)
        {
            Array.Copy(copy[i], matrix[i], n);
        }
    }
}
```

| 复杂度 | |
|--------|------|
| 时间 | O(m·n·(m+n))，每遇一个 0 清整行整列；最坏全 0 时 O(mn(m+n)) |
| 空间 | O(m·n)，额外开了一个同样大小的副本矩阵 |

## 方法二：首行首列作标记（O(1) 空间）⭐ 推荐

观察到方法一（以及 O(m+n) 标记数组法）的本质都是"记录哪些行、哪些列要清零"。把这两个标记数组**复用进矩阵的首行和首列**即可实现 O(1) 额外空间。但首行首列本身也可能含 0、需要被清零，所以先用两个布尔变量 `firstRowZero` / `firstColZero` 单独记录它们自身是否要清零，最后再单独处理。

```
matrix = [[1,1,1],
          [1,0,1],
          [1,1,1]]   (m=3, n=3)

步骤 1：首行无 0 -> firstRowZero=false；首列无 0 -> firstColZero=false

步骤 2：用首行/首列标记其余区域（i≥1, j≥1）：
   遇 matrix[1][1]=0 -> 标记 matrix[1][0]=0（第1行要清）、matrix[0][1]=0（第1列要清）
   matrix = [[1,0,1],
             [0,0,1],   ← 首列[1]=0、首行[1]=0 都是标记，不是真清零
             [1,1,1]]

步骤 3：依标记清零其余区域：
   matrix[1][0]=0 -> 清 matrix[1][1]、matrix[1][2]
   matrix[0][1]=0 -> 清 matrix[2][1]
   matrix = [[1,0,1],
             [0,0,0],
             [1,0,1]]

步骤 4：firstRowZero/firstColZero 均为 false，首行首列不单独清零
结果 = [[1,0,1],[0,0,0],[1,0,1]]
```

```csharp
public class Solution
{
    public void SetZeroes(int[][] matrix)
    {
        int m = matrix.Length;
        int n = matrix[0].Length;

        // 1. 先记录首行、首列自身是否含 0（稍后单独处理，避免与标记混淆）
        bool firstRowZero = false;
        bool firstColZero = false;
        for (int j = 0; j < n; j++) if (matrix[0][j] == 0) firstRowZero = true;
        for (int i = 0; i < m; i++) if (matrix[i][0] == 0) firstColZero = true;

        // 2. 用首行/首列作为"标记数组"，记录其余区域哪些行/列要清零
        for (int i = 1; i < m; i++)
        {
            for (int j = 1; j < n; j++)
            {
                if (matrix[i][j] == 0)
                {
                    matrix[i][0] = 0;  // 标记第 i 行要清零
                    matrix[0][j] = 0;  // 标记第 j 列要清零
                }
            }
        }

        // 3. 根据首行/首列的标记，清零其余区域
        for (int i = 1; i < m; i++)
        {
            for (int j = 1; j < n; j++)
            {
                if (matrix[i][0] == 0 || matrix[0][j] == 0)
                {
                    matrix[i][j] = 0;
                }
            }
        }

        // 4. 最后单独清零首行、首列（必须在步骤 3 之后，否则标记会被提前破坏）
        if (firstRowZero)
        {
            for (int j = 0; j < n; j++) matrix[0][j] = 0;
        }
        if (firstColZero)
        {
            for (int i = 0; i < m; i++) matrix[i][0] = 0;
        }
    }
}
```

| 复杂度 | |
|--------|------|
| 时间 | O(m·n)，两次完整遍历矩阵 |
| 空间 | **O(1)**，仅用 `firstRowZero`、`firstColZero` 两个布尔变量 |

!!! tip "为什么步骤 4 必须在最后？"
    首行首列同时承担"标记数组"和"待清零数据"两个职责。若先清零首行首列，步骤 2 写入的标记会被抹掉，步骤 3 就无法判断哪些行列该清。所以必须**先用标记清完其余区域，最后再清首行首列**。

## 两种方法对比

| | 方法一：复制矩阵 | 方法二：首行首列标记 ⭐ |
|------|------|------|
| **时间** | O(mn(m+n)) 最坏 | **O(mn)** |
| **空间** | O(mn) | **O(1)** |
| **核心技巧** | 副本隔离读写 | 复用首行首列作标记数组 |
| **可读性** | 直观，逻辑最简单 | 需理解标记复用 + 首行首列单独处理 |

> **选择建议**：方法二是 LeetCode 进阶要求（O(1) 空间）的**标准答案**，面试必会。方法一适合作为推导起点，先理解"为什么不能边遍历边清零"。建议从方法一入手体会隔离的必要性，再过渡到方法二掌握空间优化的复用技巧。
