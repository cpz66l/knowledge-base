# 环形链表

> [LeetCode 141. Linked List Cycle](https://leetcode.cn/problems/linked-list-cycle/) - Easy

!!! warning "快慢指针的经典入门"
    判环是 Floyd 龟兔赛跑算法（Floyd's Cycle Detection）的最基础应用。快慢指针的**步长差为 1** 是确保必然相遇的关键——如果步长差更大（如 2 和 4），可能永远错过。本题是 LC 142 环形链表 II（找入环点）的前置题。

判断链表中是否有环——某个节点的 `next` 指回了之前的节点，形成一个循环。

```
有环:  1 → 2 → 3 → 4
                 ↖   ↓
                  6 ← 5      返回 true

无环:  1 → 2 → 3 → 4 → null  返回 false
```

---

## 核心思路

如果有环，遍历链表永远不会碰到 `null`——会无限循环。判断方法：

- **方法一（哈希表）**：记录走过的节点，如果再次遇到同一个节点对象，说明有环。O(n) / O(n)
- **方法二（快慢指针）**：快指针追慢指针。如果有环，快指针迟早从后面追上——因为每次多走一步，差距缩小 1。O(n) / O(1)

---

## 方法一：哈希表（记录路过节点）

每走一步，检查当前节点是否在 `HashSet<ListNode>` 中。如果在，说明回到老地方了——有环。

```
链表: 1 → 2 → 3 → 4 → 5 → 3(回到节点3)

Step 1: p=1, set={},      加入set → set={1}
Step 2: p=2, set={1},     加入set → set={1,2}
Step 3: p=3, set={1,2},   加入set → set={1,2,3}
Step 4: p=4, set={1,2,3}, 加入set → set={1,2,3,4}
Step 5: p=5, set={...},   加入set → set={1,2,3,4,5}
Step 6: p=3, set={...},   发现 3 已在集合中 → 有环 ✓
```

```csharp
public class Solution
{
    public bool HasCycle(ListNode head)
    {
        // 用 HashSet<ListNode> 存储节点引用，不是存 int 值
        // 因为不同节点可能有相同的值，但引用唯一
        HashSet<ListNode> set = new HashSet<ListNode>();

        ListNode p = head;
        while (p != null)
        {
            if (set.Contains(p))    // 这个节点之前见过 → 有环
            {
                return true;
            }
            else
            {
                set.Add(p);         // 记录路过节点
            }
            p = p.next;
        }

        return false;   // 走到 null 了，没环
    }
}
```

| 复杂度 | |
|--------|------|
| 时间 | O(n)，遍历每个节点最多一次 |
| 空间 | O(n)，最坏情况存储所有节点 |

---

## 方法二：快慢指针（Floyd 判环）⭐

**核心直觉**：操场跑圈。慢的每次跑 1 米，快的每次跑 2 米。如果跑道是环形，快的总会从后面追上慢的；如果跑道是直线，快的先到终点。

```
slow 每次走 1 步，fast 每次走 2 步

无环时:
  1 → 2 → 3 → 4 → null
  s=1,f=2 → s=2,f=4 → s=3,f=null → fast 到头，退出

有环时:
  1 → 2 → 3 → 4
            ↖   ↓
             6 ← 5

  slow: 1 → 2 → 3 → 4 → 5 → 6 → 3  ...
  fast: 2 → 4 → 6 → 4 → 6 → 4 → 6  ...
                  ↑
            fast 和 slow 在节点 6 相遇 ✓
```

**为什么步长差 1 保证相遇？** 一旦 slow 进环，fast 已经在内圈。fast 每次比 slow 多走 1 步——差距每步缩小 1。如果进环时 fast 落后 slow 的距离是 `d`，最多 `d` 步后必然追上。步长差如果是 2，可能跳过不碰面。

```csharp
public class Solution
{
    public bool HasCycle(ListNode head)
    {
        // 边界：空链表或单节点无环——根本谈不上环
        if (head == null || head.next == null)
        {
            return false;
        }

        ListNode slow = head;
        ListNode fast = head.next;   // 初始让 fast 先走一步，避免 while 一开始就 slow==fast

        // slow == fast 时说明追上了——有环
        while (slow != fast)
        {
            // fast 或 fast.next 为 null 说明到终点了——无环
            // 因为 fast 一次两步，必须检查两个位置
            if (fast == null || fast.next == null)
            {
                return false;
            }

            slow = slow.next;          // 慢的走 1 步
            fast = fast.next.next;     // 快的走 2 步
        }

        return true;   // slow == fast，追上了，有环
    }
}
```

| 复杂度 | |
|--------|------|
| 时间 | O(n)，有环时快慢指针在环内最多追逐一轮 |
| 空间 | O(1)，只用了两个指针 |

---

## 方法二变体：快慢指针同起点出发

`fast = head.next` 的写法会多一次初始错位。更常见的写法是快慢都从 `head` 出发：

```csharp
public bool HasCycle(ListNode head)
{
    ListNode slow = head;
    ListNode fast = head;

    while (fast != null && fast.next != null)
    {
        slow = slow.next;
        fast = fast.next.next;
        if (slow == fast)          // 先走再比
        {
            return true;
        }
    }

    return false;
}
```

| 写法 | 初始化 | 循环条件 | 判断时机 |
|------|--------|----------|----------|
| 你的写法 | `fast = head.next` | `slow != fast` | while 条件本身就是判断 |
| 同起点写法 | `fast = head` | `fast != null && fast.next != null` | 先走一步再比，在循环体内判断 |

两种写法等价，区别仅在于比不比较初始位置。

---

## 方法对比

| 方法 | 时间 | 空间 | 优势 | 劣势 |
|------|------|------|------|------|
| 哈希表 | O(n) | O(n) | 思路直观，一步到位 | 需要额外空间 |
| **快慢指针** ⭐ | O(n) | O(1) | 空间 O(1)，经典算法 | 需要理解追逐逻辑 |

!!! tip "步长差必须是 1 吗？"
    不一定是 1，但**差 1 保证必然相遇**。如果 slow 走 1 步、fast 走 3 步（差为 2），在某些环长下可能永远错过。所以快慢指针的标准配置就是 1 和 2——差为 1，100% 相遇。

!!! tip "为什么不用 `HashSet<int>`？"
    因为环判断的是"同一个节点对象"，不是"相同的值"。链表 `1 → 2 → 1 → null` 中有两个值为 1 的节点，它们是不同的对象。用 `HashSet<int>` 会把第二个 1 误判为环。必须存节点引用 `HashSet<ListNode>`——参照 LC 160 相交链表的相同原则。

---

> 📎 标签：`链表` `快慢指针` `哈希集合` `判环`
