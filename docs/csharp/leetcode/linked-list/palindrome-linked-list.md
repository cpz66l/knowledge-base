# 回文链表

> [LeetCode 234. Palindrome Linked List](https://leetcode.cn/problems/palindrome-linked-list/) - Easy

!!! warning "回文判定 + 链表操作"
    看似简单，实则考察**链表基本功的组合**：找中点（快慢指针）+ 反转链表 + 双指针比较。方法一用数组取巧但浪费空间，方法二 O(1) 空间才是在考察"你真正理解链表操作"。本题是 LC 206 反转链表 和 LC 876 链表中点的综合应用。

判断一个单链表是否为回文链表——正着读和反着读值序列相同。

```
回文:  1 → 2 → 2 → 1 → null  ✅  (正: 1,2,2,1  反: 1,2,2,1)
回文:  1 → 2 → 1 → null      ✅  (正: 1,2,1    反: 1,2,1)
非回文: 1 → 2 → 3 → null     ❌  (正: 1,2,3    反: 3,2,1)
```

---

## 核心思路

单链表只能从头往后遍历，无法像数组那样双指针从两头往中间走。两种思路破局：

- **方法一**：把链表值拷进数组 → 数组双指针从两头往中间比 → O(n) 时间 / O(n) 空间
- **方法二**：快慢指针找中点 → 反转后半段 → 双指针从两端往中间比 → O(n) 时间 / O(1) 空间

---

## 方法一：数组 + 双指针（简单直观）

把链表值逐个存入 `List<int>`，然后用头尾双指针对撞比较。

```
链表:  1 → 2 → 2 → 1 → null

Step 1: 遍历链表，nums = [1, 2, 2, 1]
Step 2: 双指针比较:
         i=0,j=3 → nums[0]=1, nums[3]=1 ✓
         i=1,j=2 → nums[1]=2, nums[2]=2 ✓
         i=2,j=1 → i >= nums.Count/2(2)，停止
         全匹配 → true
```

```csharp
public class Solution
{
    public bool IsPalindrome(ListNode head)
    {
        // 用 List 而非普通数组——链表长度未知，List 自动扩容
        List<int> nums = new List<int>();

        // 第一遍：把链表值全部拷进数组
        ListNode p = head;
        while (p != null)
        {
            nums.Add(p.val);
            p = p.next;
        }

        // 第二遍：头尾双指针往中间走，有一对不相等就不是回文
        // 只遍历到 Count/2：奇数个时中间元素不用比（自己和自己是回文）
        for (int i = 0, j = nums.Count - 1; i < nums.Count / 2; i++, j--)
        {
            if (nums[i] != nums[j])
            {
                return false;   // 发现不对称，提前返回
            }
        }

        return true;   // 全部对称，是回文
    }
}
```

| 复杂度 | |
|--------|------|
| 时间 | O(n)，遍历链表一次 + 遍历数组半次 |
| 空间 | O(n)，额外数组存储全部 n 个值 |

---

## 方法二：快慢指针 + 反转后半段 ⭐

**三步走**：找中点 → 反转后半段 → 双指针从两端往中间比。比完可还原。

```
原始链表:  1 → 2 → 3 → 2 → 1 → null

Step 1: 快慢指针找前半段末尾
         slow 每次走 1 步，fast 每次走 2 步
         fast 走到尾时，slow 就在中间(奇数)或中间偏左(偶数)

         初始:  slow=1, fast=1
         第1步: slow=2, fast=3
         第2步: slow=3, fast=1(最后一个) → fast.next.next == null，停止
         结果:  firstHalfEnd = 3（奇数个时是正中间节点）

Step 2: 反转后半段（从 firstHalfEnd.next = 2 开始）
         反转后:  1 → 2 → 3 → 1 → 2 → null
                 前半段 ↑       后半段 ↑
                 head=1        secondHalfStart=1（注意：这是原链表尾节点）

Step 3: 双指针比较
         head=1 vs secondHalfStart=1 ✓ → head=2 vs secondHalfStart=2 ✓
         后半段走完 → 全匹配 → true

Step 4（可选）: 还原链表——再次反转后半段
```

```
偶数个节点的情况:

原始:  1 → 2 → 2 → 1 → null

Step 1: 快慢指针
         slow=1, fast=1 → slow=2, fast=2 → slow=2, fast=null(超出)，停止
         firstHalfEnd = 2（前半段最后一个）

Step 2: 反转后半段 [2,1] → [1,2]
         反转后:  1 → 2 → 1 → 2 → null
                 head=1    secondHalfStart=1

Step 3: 比较
         head=1 vs secondHalfStart=1 ✓ → head=2 vs secondHalfStart=2 ✓
         全匹配 → true
```

```csharp
public class Solution
{
    public bool IsPalindrome(ListNode head)
    {
        // 空链表或单节点——必然是回文
        if (head == null || head.next == null)
        {
            return true;
        }

        // Step 1：快慢指针找到前半段的末尾节点
        ListNode firstHalfEnd = EndOfFirstHalf(head);

        // Step 2：反转后半段链表
        ListNode secondHalfStart = ReverseList(firstHalfEnd.next);

        // Step 3：双指针从两端向中间比较
        ListNode p1 = head;               // 前半段从头开始
        ListNode p2 = secondHalfStart;    // 后半段从反转后的头开始

        bool isPalindrome = true;         // 标记变量，方便后续还原链表
        while (p2 != null)                // 后半段长度 ≤ 前半段，以后半段为准
        {
            if (p1.val != p2.val)
            {
                isPalindrome = false;
                break;                    // 发现不相等，立即退出比较
            }
            p1 = p1.next;
            p2 = p2.next;
        }

        // Step 4（可选但推荐）：还原链表——把后半段反转回去
        // 这道题不强制还原，但面试中这样做体现对数据完整性的考虑
        firstHalfEnd.next = ReverseList(secondHalfStart);

        return isPalindrome;
    }

    /// <summary>快慢指针找前半段的末尾节点</summary>
    /// <remarks>
    /// 偶数个节点（1,2,3,4）：slow 停在 2（前半段末尾）
    /// 奇数个节点（1,2,3,4,5）：slow 停在 3（正中间，不属于任何半段）
    ///
    /// 终止条件 fast.next != null && fast.next.next != null：
    ///   - 偶数个：fast 走到倒数第二个节点时，fast.next.next == null，停止
    ///   - 奇数个：fast 走到最后一个节点时，fast.next == null，停止
    /// </remarks>
    private ListNode EndOfFirstHalf(ListNode head)
    {
        ListNode fast = head;
        ListNode slow = head;

        // fast 一次两步，slow 一次一步
        // fast 走到不能走时，slow 正好在前半段末尾
        while (fast.next != null && fast.next.next != null)
        {
            fast = fast.next.next;
            slow = slow.next;
        }

        return slow;
    }

    /// <summary>反转链表（LC 206）——迭代版，O(1) 空间</summary>
    private ListNode ReverseList(ListNode head)
    {
        ListNode prev = null;    // 已反转部分的头
        ListNode cur = head;     // 当前要处理的节点

        while (cur != null)
        {
            ListNode temp = cur.next;   // 暂存下一个节点
            cur.next = prev;            // 当前节点指向前一个（掉头）
            prev = cur;                 // prev 前移
            cur = temp;                 // cur 前移
        }

        return prev;   // prev 是反转后的新头
    }
}
```

| 复杂度 | |
|--------|------|
| 时间 | O(n)，找中点 O(n/2) + 反转 O(n/2) + 比较 O(n/2) + 还原 O(n/2) |
| 空间 | O(1)，只用了几个指针变量 |

---

## 方法对比

| 方法 | 时间 | 空间 | 优势 | 劣势 |
|------|------|------|------|------|
| 数组 + 双指针 | O(n) | O(n) | 思路简单，三行核心逻辑 | 需要额外数组空间 |
| **快慢指针 + 反转** ⭐ | O(n) | O(1) | 空间最优，展示链表操作基本功 | 要写三个辅助方法，代码较长 |

!!! tip "快慢指针中点的选取"
    注意 `EndOfFirstHalf` 的循环条件是 `fast.next != null && fast.next.next != null`：
    
    - **偶数个**（1,2,3,4）：slow 停在 2（前半段末尾），后半段从 3 开始——完美平分
    - **奇数个**（1,2,3,4,5）：slow 停在 3（正中间），后半段从 4 开始——中间元素 3 不参与比较
    
    不要用 `fast != null && fast.next != null`（那是判环的走法），会得到不同的中点位置。

!!! tip "为什么要还原链表？"
    虽然 LeetCode 判题只看返回值，不检查链表是否被修改，但面试中**主动还原**能体现工程素养：调用者可能后续还要使用这个链表，悄无声息地改了它是 bug。代码中用 `isPalindrome` 标记而非直接 return，就是为了确保还原逻辑一定执行。

!!! tip "比较阶段为什么以后半段长度为准？"
    后半段长度 = ⌊n/2⌋，前半段长度 = ⌈n/2⌉。后半段永远 ≤ 前半段，所以以后半段为迭代终止条件不会越界。

---

> 📎 标签：`链表` `快慢指针` `反转` `双指针` `回文`
