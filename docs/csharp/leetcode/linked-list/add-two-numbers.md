# 两数相加

> [LeetCode 2. Add Two Numbers](https://leetcode.cn/problems/add-two-numbers/) - Medium
>
> 学习状态：已练习
>
> 练习日期：2026-07-22
>
> 本次实现：C# / C++，逐位模拟加法
>
> 验证状态：C# 已编译并通过 5 组运行测试；C++ 已完成静态逻辑检查；原始记录未附 LeetCode Accepted 结果

## 学习目标

- 理解逆序链表为什么可以从头到尾直接模拟竖式加法。
- 用进位 `carry` 统一处理两个链表长度不同和最高位进位。
- 使用哨兵节点简化结果链表的头节点创建。
- 区分算法的辅助空间与返回结果本身占用的空间。
- 对比 C# 引用与 C++ 指针、GC 与显式所有权的写法差异。

## 题意与核心思路

每个节点保存一位数字，而且最低位在链表头部。例如：

```text
2 → 4 → 3  表示 342
5 → 6 → 4  表示 465

逐位相加：
2 + 5 = 7
4 + 6 = 10，当前位写 0，向下一位进 1
3 + 4 + 1 = 8

结果：7 → 0 → 8，表示 807
```

这恰好与手算加法“从最低位向最高位处理”的顺序一致。因此同时遍历两个链表，在每一位计算：

```text
sum = 当前 l1 数字 + 当前 l2 数字 + carry
当前结果数字 = sum % 10
下一位进位 = sum / 10
```

某个链表提前结束时，把该位数字视为 0。循环条件把 `carry` 也包含进去，就不需要在循环结束后单独追加最高位进位。

## 循环不变量

进入每轮循环前：

- `dummy.next` 到 `tail` 已经保存所有处理完的低位结果；
- `l1` 和 `l2` 指向下一位尚未处理的节点，或已经为 `null` / `nullptr`；
- `carry` 是上一位产生、需要加入当前位的进位。

当前轮追加 `sum % 10` 后，再把 `carry` 更新为 `sum / 10`，不变量继续成立。两个链表和进位都处理完时，结果链表就是完整的和。

## C# 实现

```csharp
public class Solution
{
    public ListNode AddTwoNumbers(ListNode l1, ListNode l2)
    {
        ListNode dummy = new ListNode(0);
        ListNode tail = dummy;
        int carry = 0;

        while (l1 != null || l2 != null || carry != 0)
        {
            int value1 = l1 != null ? l1.val : 0;
            int value2 = l2 != null ? l2.val : 0;
            int sum = value1 + value2 + carry;

            carry = sum / 10;
            tail.next = new ListNode(sum % 10);
            tail = tail.next;

            if (l1 != null)
            {
                l1 = l1.next;
            }

            if (l2 != null)
            {
                l2 = l2.next;
            }
        }

        return dummy.next;
    }
}
```

原始实现把最终进位放在循环之后单独判断，同样正确。本文把 `carry != 0` 加入循环条件，让“每一位都走同一套逻辑”，分支更少。

## C++ 实现

```cpp
class Solution
{
public:
    ListNode* addTwoNumbers(ListNode* l1, ListNode* l2)
    {
        ListNode dummy(0);
        ListNode* tail = &dummy;
        int carry = 0;

        while (l1 != nullptr || l2 != nullptr || carry != 0)
        {
            int value1 = l1 != nullptr ? l1->val : 0;
            int value2 = l2 != nullptr ? l2->val : 0;
            int sum = value1 + value2 + carry;

            carry = sum / 10;
            tail->next = new ListNode(sum % 10);
            tail = tail->next;

            if (l1 != nullptr)
            {
                l1 = l1->next;
            }

            if (l2 != nullptr)
            {
                l2 = l2->next;
            }
        }

        return dummy.next;
    }
};
```

原始 C++ 代码使用 `new ListNode(0)` 创建哨兵，却只返回 `head->next`，没有释放哨兵节点。在 LeetCode 的短生命周期判题进程中可能不明显，但在普通 C++ 工程中属于泄漏。这里改成栈上哨兵 `ListNode dummy(0)`；真正属于结果链表的数字节点仍在堆上创建，其所有权随返回链表交给调用方。

## 复杂度

设两个输入链表长度分别为 `m` 和 `n`：

| 指标 | 复杂度 | 说明 |
|---|---|---|
| 时间 | O(max(m, n)) | 每个输入节点最多访问一次，最后可能再处理一个进位 |
| 辅助空间 | O(1) | 不计返回结果时，只使用哨兵、尾指针、当前和与进位 |
| 返回结果空间 | O(max(m, n)) | 结果最多包含 `max(m, n) + 1` 个新节点 |

不能只写“空间 O(1)”而不说明是否排除输出链表。算法额外工作状态是常数，但题目要求创建的新结果本身会占用线性空间。

## C# 与 C++ 语言差异

| 含义 | C# | C++ |
|---|---|---|
| 节点变量 | `ListNode node` | `ListNode* node` |
| 空值 | `null` | `nullptr` |
| 访问成员 | `node.next` / `node.val` | `node->next` / `node->val` |
| 哨兵节点 | `new ListNode(0)`，由 GC 管理 | `ListNode dummy(0)`，栈上自动结束生命周期 |
| 结果节点 | `new ListNode(value)`，由 GC 管理 | `new ListNode(value)`，返回链表需要明确所有权 |

两种语言的算法、循环条件和进位计算完全一致，主要差异来自引用/指针语法和内存生命周期。用户原始观察“相同的方法可以直接迁移到两种语言”在本题成立；迁移时仍不能忽略 C++ 哨兵和结果节点的所有权。

## 常见错误

- 只在 `l1 != null && l2 != null` 时循环，导致较长链表的剩余节点丢失。
- 忘记把上一位的 `carry` 加入当前 `sum`。
- 忘记处理最后的 `carry`，例如 `9 + 1` 应得到 `0 → 1`。
- 直接把 `sum` 存入节点，没有使用 `sum % 10` 保证每个节点只保存一位。
- 追加节点后忘记移动 `tail`，后续不断覆盖同一个 `next`。
- 返回 `dummy` 而不是 `dummy.next`，把哨兵值带入结果。
- C++ 用 `new` 创建临时哨兵却没有释放；临时哨兵优先放在栈上。
- 把总空间笼统写成 O(1)，忽略返回链表需要新节点。

## 如何验证

至少覆盖：

- 普通情况：`[2,4,3] + [5,6,4] = [7,0,8]`。
- 长度不同：`[9,9,9,9,9,9,9] + [9,9,9,9] = [8,9,9,9,0,0,0,1]`。
- 产生最高位进位：`[9] + [1] = [0,1]`。
- 没有进位：`[1,2] + [3,4] = [4,6]`。
- 两个零：`[0] + [0] = [0]`。
- 检查输入链表没有被修改，结果节点数量不超过 `max(m, n) + 1`。

本知识库环境已编译运行 C# 版本，以上 5 组用例全部通过。当前环境没有 C++ 编译器，因此 C++ 版本只完成指针、进位和内存所有权的静态检查。原始资料未附 LeetCode Accepted 截图或明确判题结果，判题状态仍标记为待确认。

## 相关内容

- 专题：[链表](index.md)
- 相关技巧：[合并两个有序链表](merge-two-sorted-lists.md)
- C++：[刷题模板与易错点](../../../cpp/leetcode/templates.md)

> 📎 标签：`链表` `模拟` `进位` `哨兵节点` `C#` `C++`
