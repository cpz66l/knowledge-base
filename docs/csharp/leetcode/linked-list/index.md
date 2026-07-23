# 链表

> 反转 · 合并 · 环检测 — 指针操作基本功

---

## 题目列表

| 题目 | 难度 | 核心技巧 |
|------|------|----------|
| [合并两个有序链表](merge-two-sorted-lists.md) | Easy | 哨兵节点、链表拼接、递归、C# / C++ 对照 |
| [两数相加](add-two-numbers.md) | Medium | 逐位模拟、进位、哨兵节点、C# / C++ 对照 |
| [删除链表的倒数第 N 个结点](remove-nth-node-from-end-of-list.md) | Medium | 哨兵节点、栈、双指针、C# / C++ 对照 |
| [相交链表](intersection-of-two-linked-lists.md) | Easy | 双指针、哈希集合 |
| [反转链表](reverse-linked-list.md) | Easy | 递归、迭代双指针 |
| [回文链表](palindrome-linked-list.md) | Easy | 数组双指针、快慢指针+反转 |
| [环形链表](linked-list-cycle.md) | Easy | 哈希表、快慢指针判环 |
| [环形链表 II](linked-list-cycle-ii.md) | Medium | 哈希集合、Floyd 找入环点、C# / C++ 对照 |

---

## 核心技巧

- 哨兵节点（Dummy Node）
- 双链表归并与尾指针移动
- 快慢指针找中点、判环
- 递归反转 vs 迭代反转
- 多链表合并用堆
- 逆序数字链表可以从头到尾模拟竖式加法，用 `carry` 传递进位
- 删除节点时优先思考“目标节点的前驱”，哨兵节点可以统一删除头节点和中间节点的写法

---

> 📎 标签：`链表` `快慢指针` `递归`
