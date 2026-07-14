# 反转链表 ⭐ 重点

> [LeetCode 206. Reverse Linked List](https://leetcode.cn/problems/reverse-linked-list/) - Easy

!!! warning "高频重点"
    链表操作的**入门根基**，面试出镜率极高。递归和迭代两种写法分别考察对"递归回溯修改指针"和"双指针原地翻转"的理解。所有链表题（反转部分链表、K 个一组反转、回文链表）都基于这题的思路延伸。

给你单链表的头节点 `head`，请你反转链表，并返回反转后的链表。

---

## 核心思路

反转的本质：把每个节点的 `next` 指针从指向"后一个"改为指向"前一个"。

```
原始:  1 → 2 → 3 → 4 → 5 → null
反转:  null ← 1 ← 2 ← 3 ← 4 ← 5

每个节点只改了一件事：next 指向从 → 变成了 ←
```

两种实现路径：
- **迭代**：用 `pre` 和 `cur` 双指针，一边遍历一边改指向——从头到尾
- **递归**：先一路递归到尾节点（新头），回溯时逐层改指向——从尾到头

---

## 方法一：递归（从尾到头）

```
递归过程（递）:
  ReverseList(1) → ReverseList(2) → ... → ReverseList(5)
                                                      ↑
                                              5.next == null，返回 5（新头）

回溯过程（归）：
  回到 ReverseList(4): head=4, newHead=5
    4.next.next = 4   即 5.next = 4    // 原来 4→5，改为 5→4
    4.next = null                       // 断开 4→5，避免成环
    返回 5

  回到 ReverseList(3): head=3, newHead=5
    3.next.next = 3   即 4.next = 3    // 原来 3→4，改为 4→3
    3.next = null
    返回 5

  依次回溯到 ReverseList(1)，最终：
    null ← 1 ← 2 ← 3 ← 4 ← 5，返回 5（新头）
```

```csharp
public class Solution
{
    public ListNode ReverseList(ListNode head)
    {
        // 终止条件：空链表 或 到达尾节点
        // 注意：head == null 必须放在前面，否则空链表 head.next 会空引用
        if (head == null || head.next == null)
        {
            return head;    // 尾节点就是反转后的新头，一路传回
        }

        // 递归到底：一直走到最后一个节点
        ListNode newHead = ReverseList(head.next);

        // 回溯阶段：修改指针方向
        head.next.next = head;   // 让后一个节点指回自己（反转方向）
        head.next = null;        // 断开当前指向前方的链接，避免循环链表

        return newHead;   // newHead 始终是原链表的尾节点，一路原样返回
    }
}
```

| 复杂度 | |
|--------|------|
| 时间 | O(n)，每个节点访问一次 |
| 空间 | O(n)，递归栈深度等于链表长度 |

---

## 方法二：迭代（双指针）⭐

**核心**：`pre` 始终指向"已反转部分"的头，`cur` 始终指向"待处理部分"的头。每步把 `cur` 的指针掉头指向 `pre`，然后两者同步前移。

```
pre = null, cur = 1

Step 1: cur=1, temp=2  →  1.next = null(pre)  →  pre=1, cur=2
Step 2: cur=2, temp=3  →  2.next = 1(pre)     →  pre=2, cur=3
Step 3: cur=3, temp=4  →  3.next = 2(pre)     →  pre=3, cur=4
Step 4: cur=4, temp=5  →  4.next = 3(pre)     →  pre=4, cur=5
Step 5: cur=5, temp=null → 5.next = 4(pre)     →  pre=5, cur=null

cur == null，退出循环。pre = 5 是反转后的新头 ✓

结果：1 ← 2 ← 3 ← 4 ← 5，返回 pre = 5
```

```csharp
public class Solution
{
    public ListNode ReverseList(ListNode head)
    {
        ListNode pre = null;    // 已反转部分的头节点（初始空）
        ListNode cur = head;    // 当前要处理的节点

        while (cur != null)
        {
            ListNode temp = cur.next;   // 暂存下一个节点，否则改了指针就找不到了

            cur.next = pre;   // 核心：把当前节点指向前一个（反转方向）

            pre = cur;        // pre 前移：当前节点成为已反转部分的新头
            cur = temp;       // cur 前移：处理下一个节点
        }

        return pre;   // pre 指向反转后的新头（原尾节点）
    }
}
```

| 复杂度 | |
|--------|------|
| 时间 | O(n)，每个节点访问一次 |
| 空间 | O(1)，只用了三个指针 |

---

## 方法对比

| 方法 | 时间 | 空间 | 优势 | 劣势 |
|------|------|------|------|------|
| **迭代（推荐）** | O(n) | O(1) | 空间最优，无栈溢出风险 | 指针操作容易写错 |
| 递归 | O(n) | O(n) | 代码简短，逻辑优雅 | 长链表可能栈溢出 |

!!! tip "递归的 null 判断顺序"
    `head == null || head.next == null` 中的顺序不能反——如果先判断 `head.next == null`，当 `head` 本身为 `null` 时会触发 `NullReferenceException`。`||` 的短路求值机制要求把 `head == null` 放前面。

!!! tip "递归也能 O(1) 空间吗？"
    不能——递归本质是利用函数调用栈存储每一层的 `head` 信息，n 个节点就需要 n 层调用栈。虽然代码层面没有显式分配空间，但调用栈本身就是空间开销。工程中更推荐迭代写法。

---

> 📎 标签：`链表` `反转` `递归` `双指针`
