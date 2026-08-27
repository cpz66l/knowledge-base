# 矩阵

> 二维遍历 · 方向数组 · 螺旋/旋转 - 行列索引游戏

## 题目列表

| 题目 | 难度 | 核心技巧 |
|------|------|----------|
| [矩阵置零](set-matrix-zeroes.md) | Medium | 原地标记、首行首列复用 |
| [螺旋矩阵](spiral-matrix.md) | Medium | 边界收缩、顺时针模拟 |
| [旋转图像](rotate-image.md) | Medium | 转置 + 翻转、原地旋转 |
| [搜索二维矩阵 II](search-a-2d-matrix-ii.md) | Medium | Z 字查找、搜索空间缩减 |

相关二分题：[搜索二维矩阵 I（LC74）](../binary-search/search-a-2d-matrix.md) 属于“整张矩阵可按行展开为一维有序数组”的全局二分题，主索引放在[二分查找](../binary-search/index.md)。

---

## 核心技巧

- 方向数组 `int[][] dirs`
- 边界收缩法（螺旋遍历）
- 原地旋转：转置 + 翻转
- 行列标记法

---

> 📎 标签：`矩阵` `二维数组` `模拟`
