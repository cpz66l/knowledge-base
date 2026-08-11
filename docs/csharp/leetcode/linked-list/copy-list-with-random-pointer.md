# 复制带随机指针的链表

> [LeetCode 138. Copy List with Random Pointer](https://leetcode.cn/problems/copy-list-with-random-pointer/) - Medium
>
> 学习状态：已完成 C++ 练习
>
> 练习日期：2026-08-09
>
> 本次实现：C++，哈希表递归 / 原地穿插迭代
>
> 验证状态：用户放入知识库前已完成练习；本次整理未重复运行 LeetCode 判题
>
> 证据归属：用户 `inbox/leetcode,8月9号.txt` 原始记录。原始文本中迭代法第二轮循环存在 `node s=` 转写笔误，本文按意图修正为 `node =`。

## 学习目标

- 理解“深拷贝”要求新链表节点不能指向原链表节点。
- 掌握随机指针链表的两种建图方式：哈希表映射和原地穿插。
- 分清 `node->random` 与 `node->random->next` 的含义。
- 练习 C++ 指针节点、`unordered_map<Node*, Node*>` 和空指针判断。

## 题意与核心思路

普通链表只需要沿 `next` 复制；本题多了 `random` 指针，可能指向任意旧节点，也可能为空。

关键不是“复制值”，而是建立旧节点到新节点的映射：

```text
oldA.random -> oldB
newA.random -> newB
```

因此每次看到一个旧节点，都要能找到它对应的新节点。常见做法有两类：

- 哈希表：`old -> copied`，空间换直观。
- 原地穿插：把复制节点插在旧节点后面，让 `old->next` 临时表示复制节点。

## 方法一：哈希表递归

递归把“复制当前节点、复制 next、复制 random”统一起来。哈希表用于避免重复复制同一个节点，也能处理 `random` 指回前面节点的情况。

```cpp
#include <unordered_map>

class Solution
{
private:
    std::unordered_map<Node*, Node*> cachedNode;

public:
    Node* copyRandomList(Node* head)
    {
        if (head == nullptr)
        {
            return nullptr;
        }

        if (!cachedNode.count(head))
        {
            Node* copied = new Node(head->val);
            cachedNode[head] = copied;
            copied->next = copyRandomList(head->next);
            copied->random = copyRandomList(head->random);
        }

        return cachedNode[head];
    }
};
```

### 为什么先写入缓存再递归

如果 `random` 指针形成回指，递归可能再次遇到当前节点。先把 `head -> copied` 放入缓存，再递归处理 `next` 和 `random`，可以让后续访问直接复用已创建的新节点。

## 方法二：原地穿插迭代

这个方法不用额外哈希表，分三步：

1. 复制每个节点并插入原节点后面：`A -> A' -> B -> B'`。
2. 用 `node->random->next` 找到随机指针对应的新节点。
3. 拆分旧链表和新链表。

```cpp
class Solution
{
public:
    Node* copyRandomList(Node* head)
    {
        if (head == nullptr)
        {
            return nullptr;
        }

        for (Node* node = head; node != nullptr; node = node->next->next)
        {
            Node* copied = new Node(node->val);
            copied->next = node->next;
            node->next = copied;
        }

        for (Node* node = head; node != nullptr; node = node->next->next)
        {
            Node* copied = node->next;
            copied->random = node->random != nullptr ? node->random->next : nullptr;
        }

        Node* newHead = head->next;
        for (Node* node = head; node != nullptr;)
        {
            Node* copied = node->next;
            Node* nextOriginal = copied->next;

            node->next = nextOriginal;
            copied->next = nextOriginal != nullptr ? nextOriginal->next : nullptr;

            node = nextOriginal;
        }

        return newHead;
    }
};
```

## 易错点

- `copied->random` 不能写成 `node->random`，否则新链表会指回旧链表。
- 正确写法是 `node->random != nullptr ? node->random->next : nullptr`。
- 拆链时要先保存 `nextOriginal`，否则改完 `node->next` 后容易丢失后续原节点。
- 原始链表必须恢复，否则题目虽然返回新链表，但副作用会污染输入结构。
- 原始记录中的 `node s= node->next->next` 是明显转写笔误，正式代码应写成 `node = node->next->next`。

## 复杂度

| 方法 | 时间 | 辅助空间 | 说明 |
|---|---:|---:|---|
| 哈希表递归 | O(n) | O(n) | 哈希表和递归栈都可能线性增长 |
| 原地穿插 | O(n) | O(1) | 不计返回新链表本身，只使用常数指针 |

两种方法都会创建 n 个新节点。返回链表本身不计入辅助空间时，原地穿插法空间最优。

## 如何验证

至少覆盖：

- 空链表：`head = null`。
- 单节点且 `random = null`。
- 单节点且 `random` 指向自己。
- 多节点随机指针向前、向后、为空混合。
- 复制后检查新链表节点地址与旧链表不同，且新链表 `random` 只指向新节点。

本次整理遵循 LeetCode Inbox 规则：用户主动放入题解默认视为放入前已完成练习；当前智能体没有重新创建 C++ 工程或提交 LeetCode 复测。

## 相关内容

- 专题：[链表](index.md)
- C++：[刷题模板与易错点](../../../cpp/leetcode/templates.md)

> 标签：`链表` `哈希表` `深拷贝` `随机指针` `C++`
