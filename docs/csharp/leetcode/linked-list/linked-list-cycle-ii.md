# 环形链表 II

> [LeetCode 142. Linked List Cycle II](https://leetcode.cn/problems/linked-list-cycle-ii/) - Medium

## 页面状态

> 学习状态：已练习
>
> 练习日期：2026-07-17
>
> 本次实现：C# 快慢指针；C++ 哈希集合与快慢指针
>
> 验证状态：代码已完成静态检查；原始记录未附 LeetCode 提交结果，判题状态待确认

## 学习目标

- 判断链表是否有环，并返回开始入环的第一个节点。
- 理解 Floyd 快慢指针为什么能从相遇点推导出入环点。
- 对比哈希集合和快慢指针的空间开销。
- 熟悉 C# 节点引用与 C++ 节点指针的对应写法。

## 题意澄清

题目给出的 `pos` 只用于描述链表尾部连接到哪个位置，并不是传给函数的参数。解法只能通过 `head` 和节点的 `next` 关系判断环的位置，而且不能修改链表。

## 方法一：哈希集合

从头遍历并保存已经访问过的节点。第一次再次遇到的节点就是入环点，因为它是沿 `next` 路径重复访问的第一个节点。

本次原始记录给出了 C++ 实现：

```cpp
#include <unordered_set>

class Solution
{
public:
    ListNode* detectCycle(ListNode* head)
    {
        std::unordered_set<ListNode*> visited;
        ListNode* current = head;

        while (current != nullptr)
        {
            if (visited.find(current) != visited.end())
            {
                return current;
            }

            visited.insert(current);
            current = current->next;
        }

        return nullptr;
    }
};
```

注意集合中保存的是节点本身，而不是节点的值。不同节点完全可能拥有相同的 `val`，用节点值判重会产生误判。

| 复杂度 | 结果 |
|---|---|
| 时间 | O(n)，每个不同节点最多访问一次 |
| 空间 | O(n)，最坏需要保存所有不同节点 |

## 方法二：Floyd 快慢指针

### 第一步：判断是否有环

`slow` 每次走一步，`fast` 每次走两步：

- 无环时，`fast` 或 `fast.next` 最终会到达 `null`。
- 有环时，两个指针最终会在环内相遇。

### 第二步：寻找入环点

设：

- 从链表头到入环点的距离为 `a`；
- 从入环点到第一次相遇点的距离为 `b`；
- 从相遇点继续走回入环点的距离为 `c`；
- 环长为 `L = b + c`。

相遇时慢指针走了 `a + b`，快指针走过的距离是慢指针的两倍，因此：

```text
2(a + b) = a + b + kL
a + b = kL
a = kL - b = (k - 1)L + c
```

所以，一个指针从链表头出发，另一个从相遇点出发，两者每次都走一步，最终会在入环点相遇。

### C# 实现

```csharp
public class Solution
{
    public ListNode DetectCycle(ListNode head)
    {
        if (head == null || head.next == null)
        {
            return null;
        }

        ListNode slow = head;
        ListNode fast = head;

        while (fast != null && fast.next != null)
        {
            slow = slow.next;
            fast = fast.next.next;

            if (slow == fast)
            {
                ListNode fromHead = head;
                while (fromHead != slow)
                {
                    fromHead = fromHead.next;
                    slow = slow.next;
                }

                return fromHead;
            }
        }

        return null;
    }
}
```

### C++ 实现

```cpp
class Solution
{
public:
    ListNode* detectCycle(ListNode* head)
    {
        if (head == nullptr || head->next == nullptr)
        {
            return nullptr;
        }

        ListNode* slow = head;
        ListNode* fast = head;

        while (fast != nullptr && fast->next != nullptr)
        {
            slow = slow->next;
            fast = fast->next->next;

            if (slow == fast)
            {
                ListNode* fromHead = head;
                while (fromHead != slow)
                {
                    fromHead = fromHead->next;
                    slow = slow->next;
                }

                return fromHead;
            }
        }

        return nullptr;
    }
};
```

| 复杂度 | 结果 |
|---|---|
| 时间 | O(n) |
| 空间 | O(1)，只使用固定数量的节点引用或指针 |

## C# 与 C++ 写法对照

| 含义 | C# | C++ |
|---|---|---|
| 节点变量 | `ListNode node` | `ListNode* node` |
| 空引用 / 空指针 | `null` | `nullptr` |
| 访问下一个节点 | `node.next` | `node->next` |
| 节点集合 | `HashSet<ListNode>` | `std::unordered_set<ListNode*>` |
| 判断同一节点 | 引用相等 | 指针地址相等 |

两种语言中的 Floyd 算法步骤和渐进复杂度完全相同，差别主要来自引用、指针及标准容器的语法。

## 本次性能观察

原始学习记录认为几次练习中 C++ 的快慢指针提交耗时更短。这个现象可以作为个人观察保留，但不能据此得出“C++ 实现一定更快”的结论：LeetCode 单次运行时间会受测试批次、服务器负载、编译器和运行时预热等因素影响。

如果要比较语言性能，应使用相同测试数据重复运行，并同时观察耗时分布与内存占用。本题在算法层面，两种实现都是 O(n) 时间和 O(1) 额外空间。

## 常见错误

- 返回快慢指针第一次相遇的节点。相遇点通常不是入环点，还需要执行第二阶段。
- 用节点值代替节点身份判重；相同值不代表同一个节点。
- 第二阶段仍让一个指针每次走两步。寻找入口时两个指针都必须每次走一步。
- 忘记检查 `fast` 和 `fast.next`，导致无环链表发生空引用或空指针访问。
- 误把题目描述中的 `pos` 当成函数参数。

## 如何验证

至少覆盖以下情况：

- 空链表：返回 `null`。
- 单节点无环：返回 `null`。
- 单节点指向自身：返回该节点。
- 入环点就是头节点：第二阶段应在头节点相遇。
- 入环点在链表中间：返回对应节点，而不是第一次相遇点。
- 多个节点值相同但无环：不能因为值重复而误判。

## 相关内容

- 前置：[环形链表（LC 141）](linked-list-cycle.md)
- 相关技巧：[链表专题](index.md)

> 📎 标签：`链表` `快慢指针` `Floyd` `哈希集合` `C#` `C++`
