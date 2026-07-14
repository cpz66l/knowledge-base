# 相交链表 ⭐ 重点

> [LeetCode 160. Intersection of Two Linked Lists](https://leetcode.cn/problems/intersection-of-two-linked-lists/) - Easy

!!! warning "高频重点"
    链表**结构性判断**的经典题。核心不在于找相同的"数值"，而是找相同的"节点引用"——两个指针指向内存中同一个 `ListNode` 对象。双指针法用 O(n) 时间、O(1) 空间优雅消除长度差，是面试必问解法。

给你两个单链表的头节点 `headA` 和 `headB`，请你找出并返回两个单链表相交的起始节点。如果两个链表不存在相交节点，返回 `null`。

---

## 核心思路

### 关键认知：相交在"节点"，不在"值"

```
链表 A:  a1 → a2 ↘
                    c1 → c2 → c3 → null
链表 B:  b1 → b2 → b3 ↗
```

入环节点 `c1` 是**同一个节点对象**（引用相同），不是值相等。所以哈希集合的类型是 `HashSet<ListNode>`，不是 `HashSet<int>`。

---

## 方法一：哈希集合

遍历链表 A，把所有节点存入 `HashSet<ListNode>`。再遍历链表 B，第一个在集合中出现的节点就是交点。

```
A = [4,1,8,4,5], B = [5,6,1,8,4,5], 交点 = 8

Step 1: 遍历 A，set = {4, 1, 8, 4(第二个), 5}
Step 2: 遍历 B，5 不在集合 → 6 不在 → 1 不在 → 8 在集合 ✓ 返回节点 8
```

```csharp
public ListNode GetIntersectionNode(ListNode headA, ListNode headB)
{
    // 集合存储 ListNode 引用，不是 int 值——判断"同一个节点对象"
    var set = new HashSet<ListNode>();

    // 第一遍：把链表 A 的所有节点存入集合
    while (headA != null)
    {
        set.Add(headA);
        headA = headA.next;
    }

    // 第二遍：遍历链表 B，找第一个在集合中的节点
    while (headB != null)
    {
        if (set.Contains(headB))   // 找到了——是同一个节点引用
        {
            return headB;
        }
        headB = headB.next;
    }

    return null;   // 遍历完 B 都没找到，说明不相交
}
```

| 复杂度 | |
|--------|------|
| 时间 | O(m + n)，分别遍历两个链表 |
| 空间 | O(m)，存储链表 A 所有节点 |

---

## 方法二：双指针（消除长度差）⭐

**精髓**：让两个指针走过相同的总路程，从而在没有交点时同时到达 `null`，在有交点时刚好相遇。

```
指针 pA 从 headA 出发，走完 A 后切到 headB 继续走
指针 pB 从 headB 出发，走完 B 后切到 headA 继续走

              A 独有段   公共段   B 独有段
链表 A:       ───a────  ──c──
链表 B:                 ──c──  ───b────

pA 路径: a → c → b → c（交点）
pB 路径: b → c → a → c（交点）
                 ↑
         pA 和 pB 走过的总路程都是 a + c + b
         所以它们会同时到达交点 c 的第一个节点
```

```
A = [4,1,8,4,5], B = [5,6,1,8,4,5]

pA: 4 → 1 → 8 → 4 → 5 → null → 5(B) → 6 → 1 → 8  ← 相遇!
pB: 5 → 6 → 1 → 8 → 4 → 5 → null → 4(A) → 1 → 8  ← 相遇!
                                                            ↑
pA 走了 9 步，pB 走了 9 步，同时在节点 8 相遇
```

**不相交的情况**：两个指针各自走完 `m + n` 步后会同时到达 `null`，返回 `null`。

```csharp
public class Solution
{
    public ListNode GetIntersectionNode(ListNode headA, ListNode headB)
    {
        // 边界：任一链表为空，不可能相交
        if (headA == null || headB == null)
        {
            return null;
        }

        ListNode pA = headA;   // 指针 A，从 headA 出发
        ListNode pB = headB;   // 指针 B，从 headB 出发

        // pA == pB 时有两种可能：
        //   1. 找到了交点（引用相同）
        //   2. 都为 null（不相交，走完了）
        while (pA != pB)
        {
            // pA 走完 A 就切到 B，否则继续走
            pA = pA == null ? headB : pA.next;
            // pB 走完 B 就切到 A，否则继续走
            pB = pB == null ? headA : pB.next;
        }

        return pA;   // 交点节点，或 null（不相交）
    }
}
```

| 复杂度 | |
|--------|------|
| 时间 | O(m + n)，每个指针最多走 m + n 步 |
| 空间 | O(1)，只用了两个指针 |

---

## 方法对比

| 方法 | 时间 | 空间 | 优势 | 劣势 |
|------|------|------|------|------|
| 哈希集合 | O(m + n) | O(m) | 思路直观，容易想到 | 需要额外空间 |
| **双指针（本解法）** | O(m + n) | O(1) | 空间最优，代码简洁 | 需要理解"消除长度差"的 trick |

!!! tip "双指针的核心直觉"
    如果不切换链表，两个指针会因为长度不同而错过交点。切换链表相当于"补上长度差"——pA 多走了 B 的独有段，pB 多走了 A 的独有段，最终两个指针走过的总路程相同。**不要在原 head 上直接操作**，必须用副本指针 `pA`、`pB`。

---

> 📎 标签：`链表` `双指针` `哈希集合` `相交`
