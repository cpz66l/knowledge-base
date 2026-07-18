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

- 已使用模板：链表哨兵节点与尾指针拼接
- 已验证题目：[LC 21 合并两个有序链表](../../csharp/leetcode/linked-list/merge-two-sorted-lists.md)
- 待整理问题：其他容器和算法模板等待实际练习后补充
