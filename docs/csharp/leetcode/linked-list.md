# 链表

> 反转 · 合并 · 环检测 — 指针操作基本功

---

## 题目列表

<!-- TODO: 添加题目 -->

给你两个单链表的头节点 headA 和 headB ，请你找出并返回两个单链表相交的起始节点。如果两个链表不存在相交节点，返回 null 。
思路一：哈希集合
public ListNode GetIntersectionNode(ListNode headA, ListNode headB)
{
    var set = new HashSet<ListNode>();
    while (headA != null)
    {
        set.Add(headA);
        headA = headA.next;
    }

    while (headB != null)
    {
        if (set.Contains(headB))
        {
            return headB;
        }
        headB = headB.next;
    }
        return null;
}

思考：为什么使用哈希集合，在遍历时只要找到的第一个相同的就可以直接返回。
这里主要考察对链表的理解，我们在定义hash集合时用的是new HashSet<ListNode>()，集合类型是ListNode而不是int,表面上查的是相同的数字，但实际上查的是在内存中相同位置的链表节点，若是相同位置链表节点，则是后续都在同一个链表中。


思路二：双指针法
public class Solution {
    public ListNode GetIntersectionNode(ListNode headA, ListNode headB) {
        if(headA == null || headB == null){
            return null;
        }

        ListNode pA = headA;
        ListNode pB = headB;

        while(pA != pB){
            pA = pA == null ? headB : pA.next;
            pB = pB == null ? headA : pB.next;
        }

        return pA;
    }
}
注意：不要在head上直接操作

---

## 核心技巧

- 哨兵节点（Dummy Node）
- 快慢指针找中点、判环
- 递归反转 vs 迭代反转
- 多链表合并用堆

---

> 📎 标签：`链表` `快慢指针` `递归`
