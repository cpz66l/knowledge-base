# 链表

> 反转 · 合并 · 环检测 — 指针操作基本功

---

## 题目列表

| 题目 | 难度 | 核心技巧 |
|------|------|----------|
| [相交链表](intersection-of-two-linked-lists.md) | Easy | 双指针、哈希集合 |

---

给你单链表的头节点 head ，请你反转链表，并返回反转后的链表。
方法一：递归
public class Solution {
    public ListNode ReverseList(ListNode head) {
        if(head == null || head.next == null){
//注意应当将"head == null"放在或逻辑前，避免head为空仍访问head.next导致报错空引用异常若head == null，则不会再判断head.next。
            return head;
        }
        ListNode newHead = ReverseList(head.next);//一直递归直到找到newhead
        head.next.next = head;//操作递归过程中的节点，更改地址指向
        head.next = null;//避免出现循环链表
        return newHead;
    }
}

方法二：迭代（双指针）

public class Solution{
    public ListNode ReverseList(ListNode head){
        ListNode pre = null;
        ListNode cur = head;
        while(cur != null){
            ListNode temp = cur.next;
            cur.next = pre;//修改指针地址方向
            pre = cur;//更新新目标节点
            cur = temp;
        }
        return pre;
    }
}

## 核心技巧

- 哨兵节点（Dummy Node）
- 快慢指针找中点、判环
- 递归反转 vs 迭代反转
- 多链表合并用堆

---

> 📎 标签：`链表` `快慢指针` `递归`
