# 合并两个有序链表

> [LeetCode 21. Merge Two Sorted Lists](https://leetcode.cn/problems/merge-two-sorted-lists/) - Easy
>
> 学习状态：已完成
>
> 练习日期：2026-07-18
>
> 本次实现：C# / C++，迭代与递归
>
> 验证状态：待确认
>
> 验证证据：代码已完成静态检查；原始记录未附 LeetCode 提交结果。

## 学习目标

- 使用哨兵节点简化合并后链表的头节点处理。
- 理解移动局部指针变量不会破坏已经建立的链表连接。
- 区分修改 `tail` 与修改 `tail.next` / `tail->next`。
- 比较迭代与递归实现的空间开销。

## 当前理解

两个链表已经各自升序，因此只需要反复比较当前头节点：把较小节点接到结果链表尾部，再向前移动对应链表的指针。

实现并不会为每个值创建新节点，而是重新连接原链表节点的 `next`。返回的是新的头节点，但输入链表的连接关系会被修改；如果调用方还需要保留原结构，就必须先复制节点。

## 方法一：迭代

### 指针为什么不会破坏已有链表

以 C++ 为例：

```cpp
tail->next = list1;
list1 = list1->next;
tail = tail->next;
```

三行代码分别承担不同职责：

1. `tail->next = list1` 修改当前尾节点的 `next` 成员，真正建立连接。
2. `list1 = list1->next` 只让局部变量 `list1` 指向输入链表的下一个节点。
3. `tail = tail->next` 只让局部变量 `tail` 移动到结果链表的新尾部。

节点之间的关系存放在节点的 `next` 成员中。重新给 `tail` 这个局部指针变量赋值，不会撤销之前写入的 `tail->next`，所以从哨兵节点出发仍然能访问已经拼接的整条链表。

### C++ 实现

```cpp
class Solution
{
public:
    ListNode* mergeTwoLists(ListNode* list1, ListNode* list2)
    {
        ListNode dummy(-1);
        ListNode* tail = &dummy;

        while (list1 != nullptr && list2 != nullptr)
        {
            if (list1->val <= list2->val)
            {
                tail->next = list1;
                list1 = list1->next;
            }
            else
            {
                tail->next = list2;
                list2 = list2->next;
            }

            tail = tail->next;
        }

        tail->next = list1 != nullptr ? list1 : list2;
        return dummy.next;
    }
};
```

这里使用栈上的 `dummy`，返回的 `dummy.next` 指向输入链表中的节点，不依赖哨兵节点本身的生命周期。原始记录使用 `new ListNode(-1)` 创建哨兵但没有 `delete`，在普通 C++ 工程中会造成哨兵节点泄漏。

### C# 实现

```csharp
public class Solution
{
    public ListNode MergeTwoLists(ListNode list1, ListNode list2)
    {
        ListNode dummy = new ListNode(-1);
        ListNode tail = dummy;

        while (list1 != null && list2 != null)
        {
            if (list1.val <= list2.val)
            {
                tail.next = list1;
                list1 = list1.next;
            }
            else
            {
                tail.next = list2;
                list2 = list2.next;
            }

            tail = tail.next;
        }

        tail.next = list1 != null ? list1 : list2;
        return dummy.next;
    }
}
```

| 复杂度 | 结果 |
|---|---|
| 时间 | O(m + n)，两个链表的节点最多各处理一次 |
| 额外空间 | O(1)，哨兵和移动指针数量固定 |

## 方法二：递归

递归函数返回“当前两个链表能够合并出的头节点”。每次选择较小的当前节点，把它的 `next` 连接到剩余链表的递归结果。

### C++ 实现

```cpp
class Solution
{
public:
    ListNode* mergeTwoLists(ListNode* list1, ListNode* list2)
    {
        if (list1 == nullptr)
        {
            return list2;
        }

        if (list2 == nullptr)
        {
            return list1;
        }

        if (list1->val <= list2->val)
        {
            list1->next = mergeTwoLists(list1->next, list2);
            return list1;
        }

        list2->next = mergeTwoLists(list1, list2->next);
        return list2;
    }
};
```

### C# 实现

```csharp
public class Solution
{
    public ListNode MergeTwoLists(ListNode list1, ListNode list2)
    {
        if (list1 == null)
        {
            return list2;
        }

        if (list2 == null)
        {
            return list1;
        }

        if (list1.val <= list2.val)
        {
            list1.next = MergeTwoLists(list1.next, list2);
            return list1;
        }

        list2.next = MergeTwoLists(list1, list2.next);
        return list2;
    }
}
```

| 复杂度 | 结果 |
|---|---|
| 时间 | O(m + n) |
| 额外空间 | O(m + n)，最坏情况下递归调用栈包含所有节点 |

## 方法对比

| 方法 | 优点 | 代价 |
|---|---|---|
| 迭代 | O(1) 额外空间，不受递归深度限制 | 需要维护哨兵和尾指针 |
| 递归 | 代码直接表达“选择当前节点，再合并剩余部分” | 长链表可能导致调用栈过深 |

实际工程和面试中优先使用迭代版本；递归版本适合理解链表问题的递归结构。

## C# 与 C++ 写法对照

| 含义 | C# | C++ |
|---|---|---|
| 空引用 / 空指针 | `null` | `nullptr` |
| 访问节点成员 | `node.next` | `node->next` |
| 哨兵节点 | `new ListNode(-1)`，由 GC 管理 | `ListNode dummy(-1)`，栈上自动释放 |
| 移动局部变量 | `tail = tail.next` | `tail = tail->next` |
| 修改链表连接 | `tail.next = list1` | `tail->next = list1` |

原始代码在相等值时，C++ 选择 `list1`，C# 选择 `list2`。两者都能保持结果升序；本文统一使用 `<=` 优先选择 `list1`，让两种语言的行为一致。

## 常见错误

- 忘记在每次拼接后移动 `tail`，导致不断覆盖同一个 `next`。
- 返回哨兵节点本身，而不是 `dummy.next`。
- 循环结束后忘记连接尚未遍历完的链表。
- 把“移动指针变量”误认为“修改节点成员”；只有对 `next` 赋值才会改变链表连接。
- C++ 使用 `new` 创建哨兵后直接返回 `dummy->next`，却没有释放哨兵。
- 用 `list1->val - list2->val` 判断大小；在更一般的数据范围中可能发生整数溢出，直接比较更清晰。
- 对很长的链表使用递归，忽略调用栈深度。

## 如何验证

至少覆盖以下情况：

- 两个链表都为空：返回空。
- 其中一个链表为空：直接返回另一个链表。
- 两个链表长度不同：循环结束后正确接上剩余部分。
- 包含重复值：例如 `[1, 2, 2]` 与 `[1, 2, 3]`。
- 一个链表的所有值都小于另一个链表。
- 合并结果节点数量等于两个输入链表节点数量之和，没有丢失或形成环。

## 相关内容

- 专题：[链表](index.md)
- 相关技巧：[反转链表](reverse-linked-list.md)

> 📎 标签：`链表` `哨兵节点` `迭代` `递归` `C#` `C++`
