# 删除链表的倒数第 N 个结点

> [LeetCode 19. Remove Nth Node From End of List](https://leetcode.cn/problems/remove-nth-node-from-end-of-list/) - Medium
>
> 学习状态：已练习
>
> 练习日期：2026-07-23
>
> 本次实现：C# / C++，栈与双指针
>
> 验证状态：C# 已编译并通过 5 组运行测试；C++ 已完成静态逻辑检查；原始记录未附 LeetCode Accepted 结果

## 学习目标

- 用哨兵节点统一删除头节点和中间节点的写法。
- 理解删除链表节点时真正需要修改的是“目标节点的前驱节点”。
- 掌握栈解法和双指针解法的空间差异。
- 对比 C# `Stack<T>` 与 C++ `std::stack<T>` 的常用操作。

## 题意与核心思路

题目要求删除倒数第 `n` 个节点并返回新的头节点。真正执行删除时，不能只找到要删除的节点，还要找到它的前驱：

```text
1 -> 2 -> 3 -> 4 -> 5, n = 2
          prev  target

删除 target = 4：
prev.next = target.next
结果：1 -> 2 -> 3 -> 5
```

当删除的是原头节点时，原链表没有自然前驱。因此先加一个哨兵节点：

```text
dummy -> 1 -> 2 -> 3
```

这样无论删除头节点还是中间节点，都可以统一成“找到前驱节点，然后改前驱的 `next`”。

## 方法一：栈

先从 `dummy` 开始把所有节点压栈。栈顶是链表尾部，弹出 `n` 个节点后，新的栈顶就是待删除节点的前驱。

### C# 实现

```csharp
public class Solution
{
    public ListNode RemoveNthFromEnd(ListNode head, int n)
    {
        ListNode dummy = new ListNode(0, head);
        Stack<ListNode> stack = new Stack<ListNode>();
        ListNode current = dummy;

        while (current != null)
        {
            stack.Push(current);
            current = current.next;
        }

        for (int i = 0; i < n; i++)
        {
            stack.Pop();
        }

        ListNode previous = stack.Peek();
        previous.next = previous.next.next;
        return dummy.next;
    }
}
```

### C++ 实现

```cpp
#include <stack>

class Solution
{
public:
    ListNode* removeNthFromEnd(ListNode* head, int n)
    {
        ListNode dummy(0, head);
        std::stack<ListNode*> stack;
        ListNode* current = &dummy;

        while (current != nullptr)
        {
            stack.push(current);
            current = current->next;
        }

        for (int i = 0; i < n; i++)
        {
            stack.pop();
        }

        ListNode* previous = stack.top();
        previous->next = previous->next->next;
        return dummy.next;
    }
};
```

原始 C++ 代码用 `new ListNode(0, head)` 创建哨兵，最后手动 `delete dummy`。这可以避免哨兵泄漏，但没有必要承担堆分配和手动释放成本；临时哨兵放在栈上更简单。

| 复杂度 | 结果 |
|---|---|
| 时间 | O(n)，链表遍历一次，栈再弹出 `n` 次 |
| 额外空间 | O(n)，栈保存所有节点指针或引用 |

## 方法二：双指针

双指针目标是让 `fast` 先走 `n` 步，然后 `slow` 从 `dummy` 出发一起走。等 `fast` 到达链表尾后面的空位置时，`slow` 正好停在待删除节点的前驱。

```text
dummy -> 1 -> 2 -> 3 -> 4 -> 5, n = 2

fast 先从 head 走 2 步到 3
slow 从 dummy 出发

一起走到 fast == null：
slow 停在 3，slow.next 是要删除的 4
```

这个版本只需要固定数量的指针，是面试中更推荐的写法。

### C# 实现

```csharp
public class Solution
{
    public ListNode RemoveNthFromEnd(ListNode head, int n)
    {
        ListNode dummy = new ListNode(0, head);
        ListNode fast = head;
        ListNode slow = dummy;

        for (int i = 0; i < n; i++)
        {
            fast = fast.next;
        }

        while (fast != null)
        {
            fast = fast.next;
            slow = slow.next;
        }

        slow.next = slow.next.next;
        return dummy.next;
    }
}
```

### C++ 实现

```cpp
class Solution
{
public:
    ListNode* removeNthFromEnd(ListNode* head, int n)
    {
        ListNode dummy(0, head);
        ListNode* fast = head;
        ListNode* slow = &dummy;

        for (int i = 0; i < n; i++)
        {
            fast = fast->next;
        }

        while (fast != nullptr)
        {
            fast = fast->next;
            slow = slow->next;
        }

        slow->next = slow->next->next;
        return dummy.next;
    }
};
```

| 复杂度 | 结果 |
|---|---|
| 时间 | O(n)，`fast` 和 `slow` 总共线性移动 |
| 额外空间 | O(1)，只使用哨兵和两个移动指针 |

## C# 与 C++ 写法对照

| 含义 | C# | C++ |
|---|---|---|
| 栈类型 | `Stack<ListNode>` | `std::stack<ListNode*>` |
| 入栈 | `stack.Push(node)` | `stack.push(node)` |
| 出栈 | `stack.Pop()` | `stack.pop()` |
| 查看栈顶 | `stack.Peek()` | `stack.top()` |
| 元素数量 | `stack.Count` 属性 | `stack.size()` 函数 |
| 判断为空 | `stack.Count == 0` | `stack.empty()` |
| 哨兵节点 | `new ListNode(0, head)`，由 GC 管理 | `ListNode dummy(0, head)`，栈上自动结束生命周期 |

用户原始记录里踩到的语言差异主要来自命名风格：C# 的 `Stack<T>` 类型名首字母大写，方法是 `Push` / `Pop` / `Peek`；C++ 的 `std::stack` 类型和方法名通常小写，但查看栈顶是 `top()`。

## 常见错误

- 不加哨兵节点，删除头节点时需要单独分支。
- 找到倒数第 `n` 个节点后直接丢失前驱，无法修改链表连接。
- 双指针里让 `fast` 和 `slow` 都从 `head` 出发，最后停在目标节点而不是前驱。
- C++ 用 `new` 创建临时哨兵后忘记释放；临时哨兵优先放在栈上。
- C# 写成 `stack.peek()` 或 `stack.push()`；方法名大小写与 C++ 不同。
- 题目保证 `1 <= n <= 链表长度`，但普通工程里仍应考虑非法 `n` 的输入防御。

## 如何验证

至少覆盖：

- 删除中间节点：`[1,2,3,4,5], n = 2` → `[1,2,3,5]`。
- 删除头节点：`[1,2], n = 2` → `[2]`。
- 删除尾节点：`[1,2], n = 1` → `[1]`。
- 单节点链表：`[1], n = 1` → `[]`。
- 三节点删除中间：`[1,2,3], n = 2` → `[1,3]`。

本知识库环境已编译运行 C# 双指针版本，以上 5 组用例全部通过。当前环境没有 `g++` 或 `clang++`，因此 C++ 版本只完成指针移动、哨兵生命周期和栈操作语法的静态检查。原始资料未附 LeetCode Accepted 截图或明确判题结果，判题状态仍标记为待确认。

## 相关内容

- 专题：[链表](index.md)
- 前置：[合并两个有序链表](merge-two-sorted-lists.md)
- C++：[刷题模板与易错点](../../../cpp/leetcode/templates.md)

> 📎 标签：`链表` `哨兵节点` `栈` `双指针` `C#` `C++`
