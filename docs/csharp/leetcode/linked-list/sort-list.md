# 排序链表

> [LeetCode 148. Sort List](https://leetcode.cn/problems/sort-list/) - Medium
>
> 学习状态：已完成 C++ 练习
>
> 练习日期：2026-08-10
>
> 本次实现：C++，自顶向下归并排序
>
> 验证状态：用户放入知识库前已完成练习；本次整理未重复运行 LeetCode 判题
>
> 证据归属：用户 `inbox/leetcode,8月10号.txt` 原始记录。原始记录保留了先尝试递归找最小值导致超时，再改为归并排序的过程。

## 学习目标

- 理解链表排序不能直接依赖数组下标随机访问。
- 识别“每次找最小节点”的递归写法为什么会退化到 O(n²)。
- 掌握快慢指针切分链表和归并两个有序链表。
- 练习 C++ 链表半开区间 `[head, tail)` 的递归边界。

## 题意与核心思路

题目要求对链表升序排序，并尽量达到 O(n log n) 时间复杂度。

链表没有随机访问能力，适合使用归并排序：

```text
1. 用快慢指针找到中点，把链表拆成两段。
2. 递归排序左右两段。
3. 合并两个已经有序的链表。
```

这和数组归并排序的思想一致，但链表合并只需要改 `next` 指针，不需要额外数组。

## 踩坑记录：递归找最小值会超时

原始尝试的自然想法是：每轮扫描整条链表找最小节点，把最小节点放到前面，再递归处理剩余链表。

这个思路正确性容易理解，但复杂度是：

```text
n + (n - 1) + (n - 2) + ... + 1 = O(n²)
```

链表长度一大就会超时，因此需要换成每层 O(n)、总共 O(log n) 层的归并排序。

## C++ 实现：自顶向下归并排序

```cpp
class Solution
{
public:
    ListNode* sortList(ListNode* head)
    {
        return sortList(head, nullptr);
    }

private:
    ListNode* sortList(ListNode* head, ListNode* tail)
    {
        if (head == tail)
        {
            return nullptr;
        }

        if (head->next == tail)
        {
            head->next = nullptr;
            return head;
        }

        ListNode* slow = head;
        ListNode* fast = head;

        while (fast != tail && fast->next != tail)
        {
            slow = slow->next;
            fast = fast->next->next;
        }

        ListNode* mid = slow;
        ListNode* left = sortList(head, mid);
        ListNode* right = sortList(mid, tail);

        return merge(left, right);
    }

    ListNode* merge(ListNode* head1, ListNode* head2)
    {
        ListNode dummy(0);
        ListNode* tail = &dummy;

        while (head1 != nullptr && head2 != nullptr)
        {
            if (head1->val <= head2->val)
            {
                tail->next = head1;
                head1 = head1->next;
            }
            else
            {
                tail->next = head2;
                head2 = head2->next;
            }

            tail = tail->next;
        }

        tail->next = head1 != nullptr ? head1 : head2;
        return dummy.next;
    }
};
```

## 边界解释

递归函数处理的是半开区间 `[head, tail)`：

- `head == tail`：空区间，返回空链表。
- `head->next == tail`：只有一个节点，需要把 `head->next` 断开，返回该节点。
- 多节点：用快慢指针找到 `mid`，拆成 `[head, mid)` 和 `[mid, tail)`。

单节点时必须执行 `head->next = nullptr`。否则合并阶段可能把旧链表的后续节点继续挂在当前单节点后面，破坏“左右子链表已经独立”的前提。

## 复杂度

| 指标 | 复杂度 | 说明 |
|---|---:|---|
| 时间 | O(n log n) | 每层合并访问所有节点，共 O(log n) 层 |
| 辅助空间 | O(log n) | 自顶向下递归栈；不计链表节点本身 |

如果改成自底向上归并，可以把递归栈空间优化到 O(1)，但实现边界更复杂。

## 常见错误

- 每次找最小节点排序，复杂度 O(n²)，容易超时。
- 快慢指针切分后没有断开单节点尾部，导致合并时串回旧链表。
- 合并两个链表后忘记移动 `tail`。
- 使用堆上哨兵 `new ListNode(0)` 后忘记 `delete`；临时哨兵优先放在栈上。
- 忽略空链表和单节点链表。

## 如何验证

至少覆盖：

- 普通乱序：`4 -> 2 -> 1 -> 3`。
- 含负数：`-1 -> 5 -> 3 -> 4 -> 0`。
- 已排序链表。
- 逆序链表。
- 重复值链表。
- 空链表和单节点链表。

本次整理遵循 LeetCode Inbox 规则：用户主动放入题解默认视为放入前已完成练习；当前智能体没有重新创建 C++ 工程或提交 LeetCode 复测。

## 相关内容

- 专题：[链表](index.md)
- 相关技巧：[合并两个有序链表](merge-two-sorted-lists.md)
- C++：[刷题模板与易错点](../../../cpp/leetcode/templates.md)

> 标签：`链表` `排序` `归并排序` `快慢指针` `C++`
