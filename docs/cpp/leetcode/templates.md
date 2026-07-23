# C++ 刷题模板与易错点

> 状态：学习中。只记录已经在题目中实际使用过的 C++ 写法。

## 链表拼接：指针变量与节点成员

在 [LC 21 合并两个有序链表](../../csharp/leetcode/linked-list/merge-two-sorted-lists.md)中已经验证：

```cpp
tail->next = list1;  // 修改节点成员变量，建立真实连接
tail = tail->next;   // 只移动局部指针变量
```

- `tail->next` 是当前尾节点中保存下一节点地址的成员。
- 给 `tail->next` 赋值会改变链表结构。
- 给 `tail` 重新赋值只改变局部变量指向，不会撤销已经建立的连接。
- 临时哨兵优先写成 `ListNode dummy(-1)`；如果使用 `new`，必须明确释放责任。

## 构造新链表：哨兵与尾指针

在 [LC 2 两数相加](../../csharp/leetcode/linked-list/add-two-numbers.md)中已经使用：

```cpp
ListNode dummy(0);
ListNode* tail = &dummy;

tail->next = new ListNode(value);
tail = tail->next;

return dummy.next;
```

- `dummy` 只是临时入口，放在栈上，不属于返回链表。
- `tail->next` 创建并连接真正的结果节点，`tail = tail->next` 再移动尾指针。
- 返回 `dummy.next` 后，结果节点仍在堆上；普通 C++ 工程中应由调用方或拥有者负责释放整条结果链表。
- C# 中同样使用 `new ListNode(value)`，但节点由 GC 管理；算法一致，所有权模型不同。

## 删除链表节点：先找前驱

在 [LC 19 删除链表的倒数第 N 个结点](../../csharp/leetcode/linked-list/remove-nth-node-from-end-of-list.md)中已经使用：

```cpp
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
```

- 删除节点时真正需要修改的是前驱节点的 `next`。
- 哨兵节点让删除头节点和删除中间节点使用同一段逻辑。
- 临时哨兵用栈对象即可；如果写成 `new ListNode(0, head)`，必须手动 `delete`。

## std::stack 最小用法

在 [LC 19 删除链表的倒数第 N 个结点](../../csharp/leetcode/linked-list/remove-nth-node-from-end-of-list.md)中已经对照：

```cpp
#include <stack>

std::stack<ListNode*> stack;
stack.push(node);      // 入栈
stack.pop();           // 出栈，无返回值
ListNode* top = stack.top();

bool isEmpty = stack.empty();
size_t count = stack.size();
```

- C++ 查看栈顶是 `top()`；C# 是 `Peek()`。
- C++ 判空优先用 `empty()`；C# 常写 `stack.Count == 0`。
- C++ `pop()` 不返回元素，需要先 `top()` 再 `pop()`。

## 计划整理内容

- 常用头文件和命名空间
- vector、string、unordered_map、queue、stack、priority_queue
- 排序、比较器和二分
- DFS、BFS 和回溯
- 引用传参、返回值和生命周期
- 溢出、下标、迭代器失效和空容器

## 每次新增模板时记录

- 适用题型：
- 最小代码：
- 容易写错的地方：
- 自己验证过的题目：
- 仍未理解：

## 当前状态

- 已使用模板：链表哨兵节点、尾指针拼接、新结果链表构造、删除节点前驱定位、`std::stack`
- 已验证题目：[LC 2 两数相加](../../csharp/leetcode/linked-list/add-two-numbers.md)、[LC 19 删除链表的倒数第 N 个结点](../../csharp/leetcode/linked-list/remove-nth-node-from-end-of-list.md)、[LC 21 合并两个有序链表](../../csharp/leetcode/linked-list/merge-two-sorted-lists.md)
- 待整理问题：其他容器和算法模板等待实际练习后补充
