# 链表

> 反转 · 合并 · 环检测 — 指针操作基本功

---

## 题目列表

| 题目 | 难度 | 核心技巧 |
|------|------|----------|
| [相交链表](intersection-of-two-linked-lists.md) | Easy | 双指针、哈希集合 |
| [反转链表](reverse-linked-list.md) | Easy | 递归、迭代双指针 |

---
给你一个单链表的头节点 head ，请你判断该链表是否为回文链表。如果是，返回 true ；否则，返回 false 。

方法一：放进数组列表，然后使用双指针判定。
public class Solution {
    public bool IsPalindrome(ListNode head) {
        List<int> nums = new List<int>();//使用列表数组而不是普通数组是因为长度不确定

        ListNode P = head;

        while(P != null){
            nums.Add(P.val);
            P = P.next;
        }
            
        for(int i = 0 ,j = nums.Count-1 ; i<nums.Count/2 ; i++,j--){
            if(nums[i] != nums[j]){
                return false;
            }
        }
        return true;
    }
}

方法二：快慢指针+链表反转

public class Solution {
    public bool IsPalindrome(ListNode head) {
        
        ListNode firstHalfEnd = EndOfFirstHalf(head);
        ListNode secondHalfStart = ReverseList(firstHalfEnd.next);//反转右半边链表

        //判断回文
        while(secondHalfStart != null){
            if(head.val != secondHalfStart.val){
                return false;
            }
            head = head.next;
            secondHalfStart = secondHalfStart.next;
        }

        //还原链表
        ReverseList(firstHalfEnd.next);

        return true;
    }


    //获取前半部分链表的末尾节点
    public ListNode EndOfFirstHalf(ListNode head){
        ListNode fast = head;
        ListNode slow = head;
        while(fast.next != null && fast.next.next != null){
            fast = fast.next.next;
            slow = slow.next;
        }
        return slow;
    }

    //反转链表
    public ListNode ReverseList(ListNode head){
        ListNode cur = head;
        ListNode prev = null;

        while(cur != null){
            ListNode temp = cur.next;
            cur.next = prev;
            prev = cur;
            cur = temp;
        }
        return prev;
    }
}


## 核心技巧

- 哨兵节点（Dummy Node）
- 快慢指针找中点、判环
- 递归反转 vs 迭代反转
- 多链表合并用堆

---

> 📎 标签：`链表` `快慢指针` `递归`
