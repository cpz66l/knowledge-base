# 两两交换链表中的节点

> [LeetCode 24. Swap Nodes in Pairs](https://leetcode.cn/problems/swap-nodes-in-pairs/) - Medium
>
> 学习状态：已完成
>
> 练习日期：2026-07-24
>
> 本次实现：C# / C++，递归与迭代
>
> 验证状态：待确认
>
> 验证证据：C# 已编译并通过 6 组运行测试；C++ 已完成静态逻辑检查；原始记录未附 LeetCode Accepted 结果。

## 学习目标

- 在不修改节点值的前提下，通过重连 `next` 完成相邻节点交换。
- 理解递归写法中“先交换后续链表，再把当前两节点翻转”的返回关系。
- 用哨兵节点统一处理头节点被交换后的新入口。
- 掌握迭代版中 `prev`、`first`、`second` 三个指针的职责和赋值顺序。

## 题意与核心思路

题目要求每两个相邻节点为一组交换位置：

```text
1 -> 2 -> 3 -> 4

交换后：
2 -> 1 -> 4 -> 3
```

限制条件是不能只交换节点内部的 `val`，必须改变节点之间的连接关系。每一组实际要调整三条边：

```text
prev -> first -> second -> next

变为：
prev -> second -> first -> next
```

因此迭代写法要先保存 `first`、`second` 和 `second.next` 所在的剩余链表入口，再按顺序重连，避免丢失后续节点。

## 方法一：递归

递归函数返回“当前链表两两交换后的新头节点”。如果当前链表为空，或只剩一个节点，就不需要交换，直接返回当前头节点。

对于至少两个节点的链表：

1. `newHead = head.next`，交换后第二个节点会成为这一段的新头。
2. `head.next = SwapPairs(newHead.next)`，原第一个节点接上后续链表的交换结果。
3. `newHead.next = head`，把当前两个节点翻转。
4. 返回 `newHead`。

### C# 实现

```csharp
public class Solution
{
    public ListNode SwapPairs(ListNode head)
    {
        if (head == null || head.next == null)
        {
            return head;
        }

        ListNode newHead = head.next;
        head.next = SwapPairs(newHead.next);
        newHead.next = head;
        return newHead;
    }
}
```

### C++ 实现

```cpp
class Solution
{
public:
    ListNode* swapPairs(ListNode* head)
    {
        if (head == nullptr || head->next == nullptr)
        {
            return head;
        }

        ListNode* newHead = head->next;
        head->next = swapPairs(newHead->next);
        newHead->next = head;
        return newHead;
    }
};
```

| 复杂度 | 结果 |
|---|---|
| 时间 | O(n)，每个节点处理一次 |
| 额外空间 | O(n)，递归调用栈最坏覆盖所有节点 |

## 方法二：迭代

迭代版显式维护每一组的前驱 `prev`。哨兵节点放在原头节点前面，这样第一组交换后也能通过 `dummy.next` 拿到新的头节点。

每次循环只在后面至少还有两个节点时执行：

```text
prev -> first -> second -> next
```

重连顺序：

```text
first.next = second.next
second.next = first
prev.next = second
prev = first
```

最后一步 `prev = first` 很关键：交换后 `first` 已经变成这一组的尾节点，下一组的前驱正是它。

### C# 实现

```csharp
public class Solution
{
    public ListNode SwapPairs(ListNode head)
    {
        ListNode dummy = new ListNode(0, head);
        ListNode prev = dummy;

        while (prev.next != null && prev.next.next != null)
        {
            ListNode first = prev.next;
            ListNode second = prev.next.next;

            first.next = second.next;
            second.next = first;
            prev.next = second;
            prev = first;
        }

        return dummy.next;
    }
}
```

### C++ 实现

```cpp
class Solution
{
public:
    ListNode* swapPairs(ListNode* head)
    {
        ListNode dummy(0, head);
        ListNode* prev = &dummy;

        while (prev->next != nullptr && prev->next->next != nullptr)
        {
            ListNode* first = prev->next;
            ListNode* second = prev->next->next;

            first->next = second->next;
            second->next = first;
            prev->next = second;
            prev = first;
        }

        return dummy.next;
    }
};
```

原始 C++ 迭代记录使用 `new ListNode(0, head)` 创建哨兵，并在空链表时提前 `return head`。如果先分配堆上哨兵再提前返回，就会跳过 `delete`。正式笔记改为栈上 `ListNode dummy(0, head)`，无需手动释放，也不需要为空链表单独分支。

| 复杂度 | 结果 |
|---|---|
| 时间 | O(n)，每两个节点交换一次 |
| 额外空间 | O(1)，只使用固定数量的指针 |

## 方法对比

| 方法 | 优点 | 代价 |
|---|---|---|
| 递归 | 代码短，直接表达“当前一组 + 后续结果” | 长链表可能导致调用栈过深 |
| 迭代 | O(1) 额外空间，更接近工程写法 | 必须小心保存节点和重连顺序 |

面试中两种都值得掌握；工程里如果链表长度不可控，优先使用迭代版。

## C# 与 C++ 写法对照

| 含义 | C# | C++ |
|---|---|---|
| 空引用 / 空指针 | `null` | `nullptr` |
| 访问下一节点 | `node.next` | `node->next` |
| 临时哨兵 | `new ListNode(0, head)`，由 GC 管理 | `ListNode dummy(0, head)`，栈上自动结束生命周期 |
| 当前组前驱 | `ListNode prev` | `ListNode* prev` |
| 返回新头节点 | `dummy.next` | `dummy.next` |

## 常见错误

- 直接交换节点值，违背题目“只能进行节点交换”的要求。
- 没有先保存 `second`，改完 `first.next` 后丢失当前组第二个节点。
- 忘记把 `first.next` 接到 `second.next`，导致后续链表断开。
- 交换后让 `prev` 移动到 `second`，下一轮会从错误位置继续。
- 递归版写成 `head.next = SwapPairs(head.next)`，会把当前组的第二个节点再次传入递归。
- C++ 用 `new` 创建临时哨兵后提前返回或忘记 `delete`。

## 如何验证

至少覆盖：

- 空链表：`[]` -> `[]`。
- 单节点：`[1]` -> `[1]`。
- 两个节点：`[1,2]` -> `[2,1]`。
- 奇数长度：`[1,2,3]` -> `[2,1,3]`。
- 偶数长度：`[1,2,3,4]` -> `[2,1,4,3]`。
- 奇数长链表：`[1,2,3,4,5]` -> `[2,1,4,3,5]`。

本知识库环境已编译运行 C# 递归版和迭代版，以上 6 组用例全部通过。当前环境没有 `g++` 或 `clang++`，因此 C++ 版本只完成指针保存、重连顺序和哨兵生命周期的静态检查。原始资料未附 LeetCode Accepted 截图或明确判题结果，判题状态仍标记为待确认。

## 相关内容

- 专题：[链表](index.md)
- 相关基础：[合并两个有序链表](merge-two-sorted-lists.md)
- 相关技巧：[删除链表的倒数第 N 个结点](remove-nth-node-from-end-of-list.md)
- C++：[刷题模板与易错点](../../../cpp/leetcode/templates.md)

> 📎 标签：`链表` `哨兵节点` `递归` `迭代` `C#` `C++`
