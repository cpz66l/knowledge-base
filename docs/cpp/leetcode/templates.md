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

## 成对交换链表节点：先保存再重连

在 [LC 24 两两交换链表中的节点](../../csharp/leetcode/linked-list/swap-nodes-in-pairs.md)中已经使用：

```cpp
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
```

- 交换节点不能只改 `val`，需要修改节点之间的 `next` 连接。
- 先保存 `first` 和 `second`，再改 `first->next`，否则容易丢失当前组第二个节点。
- 交换后 `first` 变成当前组尾节点，下一轮的前驱应移动到 `first`。
- 临时哨兵放在栈上即可；如果用 `new` 创建哨兵，空链表提前返回时也要避免泄漏。

## 随机指针链表深拷贝：旧节点映射到新节点

在 [LC 138 复制带随机指针的链表](../../csharp/leetcode/linked-list/copy-list-with-random-pointer.md)中已经使用：

```cpp
std::unordered_map<Node*, Node*> cachedNode;

Node* copied = new Node(head->val);
cachedNode[head] = copied;
copied->next = copyRandomList(head->next);
copied->random = copyRandomList(head->random);
```

- `unordered_map<Node*, Node*>` 可以把旧节点地址映射到新节点地址。
- 必须先写入缓存再递归处理 `next` 和 `random`，否则随机指针回指时可能重复创建节点。
- 原地穿插写法中，复制节点临时放在旧节点后面，所以旧节点 `node` 对应的新节点是 `node->next`。
- 设置随机指针时应写 `copied->random = node->random ? node->random->next : nullptr`，不能直接指向 `node->random`。

## 链表归并排序：半开区间切分

在 [LC 148 排序链表](../../csharp/leetcode/linked-list/sort-list.md)中已经使用：

```cpp
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

    return merge(sortList(head, slow), sortList(slow, tail));
}
```

- `[head, tail)` 半开区间能避免额外扫描前驱节点来断链。
- 单节点区间要执行 `head->next = nullptr`，让递归返回的子链表真正独立。
- 每次找最小节点再递归排序是 O(n²)，链表排序优先考虑归并。

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

## 二叉树 DFS：递归结果用引用承接

在 [LC 94 二叉树的中序遍历](../../csharp/leetcode/binary-tree/binary-tree-inorder-traversal.md)中已经使用：

```cpp
void inorder(TreeNode* root, std::vector<int>& result)
{
    if (root == nullptr)
    {
        return;
    }

    inorder(root->left, result);
    result.push_back(root->val);
    inorder(root->right, result);
}
```

- 递归辅助函数如果写成 `std::vector<int> result`，会复制一份结果数组，外层不会收到修改。
- 中序遍历是左 -> 中 -> 右；前序是中 -> 左 -> 右；后序是左 -> 右 -> 中。
- 显式栈写法中，先一路向左压栈，弹出访问后再转向右子树。
- 前序迭代要先压右节点再压左节点；后序可先求中 -> 右 -> 左，再整体反转。

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

- 已使用模板：链表哨兵节点、尾指针拼接、新结果链表构造、删除节点前驱定位、相邻节点重连、随机指针深拷贝、链表归并排序、二叉树 DFS、`std::stack`
- 已验证题目：[LC 2 两数相加](../../csharp/leetcode/linked-list/add-two-numbers.md)、[LC 19 删除链表的倒数第 N 个结点](../../csharp/leetcode/linked-list/remove-nth-node-from-end-of-list.md)、[LC 21 合并两个有序链表](../../csharp/leetcode/linked-list/merge-two-sorted-lists.md)、[LC 24 两两交换链表中的节点](../../csharp/leetcode/linked-list/swap-nodes-in-pairs.md)、[LC 94 二叉树的中序遍历](../../csharp/leetcode/binary-tree/binary-tree-inorder-traversal.md)、[LC 138 复制带随机指针的链表](../../csharp/leetcode/linked-list/copy-list-with-random-pointer.md)、[LC 148 排序链表](../../csharp/leetcode/linked-list/sort-list.md)
- 待整理问题：其他容器和算法模板等待实际练习后补充
