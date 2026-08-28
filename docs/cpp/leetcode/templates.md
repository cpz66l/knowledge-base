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

## BST 验证：上下界 / 中序严格递增

在 [LC 98 验证二叉搜索树](../../csharp/leetcode/binary-tree/validate-binary-search-tree.md)中已经使用：

```cpp
bool IsValid(TreeNode* root, long lower, long upper)
{
    if (root == nullptr)
    {
        return true;
    }

    if (root->val <= lower || root->val >= upper)
    {
        return false;
    }

    return IsValid(root->left, lower, root->val)
        && IsValid(root->right, root->val, upper);
}
```

- BST 验证不能只比较当前节点和直接左右孩子，要保证整棵左子树 / 右子树都满足根节点约束。
- 上下界使用 `long` 配合 `LONG_MIN / LONG_MAX`，避免节点值刚好等于 `INT_MIN / INT_MAX` 时边界冲突。
- 中序遍历写法中，合法 BST 的访问序列必须严格递增；重复值也应返回 false。
- 显式栈中序遍历时，先把当前非空节点 `push`，再移动到左子树，不要把空指针压栈。

## 二叉树最大深度：DFS 返回高度 / BFS 固定层大小

在 [LC 104 二叉树的最大深度](../../csharp/leetcode/binary-tree/maximum-depth-of-binary-tree.md)中已经使用：

```cpp
int maxDepth(TreeNode* root)
{
    if (root == nullptr)
    {
        return 0;
    }

    return std::max(maxDepth(root->left), maxDepth(root->right)) + 1;
}
```

- 递归函数返回“当前子树高度”，空树高度为 0。
- 非空节点的高度是左右子树较大值再加当前节点这一层。
- 如果题目要求按层处理，则 BFS 需要先保存当前层节点数：

```cpp
std::queue<TreeNode*> queue;
queue.push(root);
int depth = 0;

while (!queue.empty())
{
    int levelSize = static_cast<int>(queue.size());
    while (levelSize > 0)
    {
        TreeNode* node = queue.front();
        queue.pop();
        if (node->left != nullptr) queue.push(node->left);
        if (node->right != nullptr) queue.push(node->right);
        levelSize--;
    }
    depth++;
}
```

- `queue.size()` 必须在处理本层前固定下来；循环中新增的是下一层节点，不能混入当前层计数。
- DFS 辅助空间取决于树高 `h`；BFS 辅助空间取决于最大层宽 `w`。

## 二叉树层序输出：外层结果要先创建当前层

在 [LC 102 二叉树的层序遍历](../../csharp/leetcode/binary-tree/binary-tree-level-order-traversal.md)中已经使用：

```cpp
std::vector<std::vector<int>> result;
std::queue<TreeNode*> queue;
queue.push(root);

while (!queue.empty())
{
    int levelSize = static_cast<int>(queue.size());
    result.push_back(std::vector<int>());

    for (int i = 0; i < levelSize; i++)
    {
        TreeNode* node = queue.front();
        queue.pop();
        result.back().push_back(node->val);

        if (node->left != nullptr) queue.push(node->left);
        if (node->right != nullptr) queue.push(node->right);
    }
}
```

- 外层 `std::vector<std::vector<int>>` 创建后，内层 `vector<int>` 不会自动存在。
- 每处理一层前先 `result.push_back(std::vector<int>())`，再用 `result.back()` 写当前层。
- 左右孩子入队前先判空，避免下一轮访问空指针。

## 有序数组建平衡 BST：中点切分

在 [LC 108 将有序数组转换为二叉搜索树](../../csharp/leetcode/binary-tree/convert-sorted-array-to-binary-search-tree.md)中已经使用：

```cpp
TreeNode* build(std::vector<int>& nums, int left, int right)
{
    if (left > right)
    {
        return nullptr;
    }

    int mid = left + (right - left) / 2;
    TreeNode* root = new TreeNode(nums[mid]);
    root->left = build(nums, left, mid - 1);
    root->right = build(nums, mid + 1, right);
    return root;
}
```

- 有序数组中点天然适合作为 BST 根节点；左半边进左子树，右半边进右子树。
- 终止条件是 `left > right`，单元素区间仍要创建节点。
- `left + (right - left) / 2` 是更稳妥的中点写法。
- LeetCode 建树时可以返回裸指针；普通工程中要额外设计整棵树的释放责任。

## 二分查找：第一个大于等于目标的位置

在 [LC 35 搜索插入位置](../../csharp/leetcode/binary-search/search-insert-position.md)中已经使用：

```cpp
int left = 0;
int right = static_cast<int>(nums.size()) - 1;
int answer = static_cast<int>(nums.size());

while (left <= right)
{
    int mid = left + (right - left) / 2;

    if (nums[mid] >= target)
    {
        answer = mid;
        right = mid - 1;
    }
    else
    {
        left = mid + 1;
    }
}
```

- `answer = nums.size()` 可以覆盖目标值大于所有元素、插入到末尾的情况。
- 当 `nums[mid] >= target` 时，`mid` 是候选答案，但左边可能还有更早位置，所以继续向左找。
- 中点优先写 `left + (right - left) / 2`，避免极端下标下 `left + right` 溢出。
- 这类题不要只记“找到就返回”，要先判断题目问的是任意位置、左边界、右边界还是插入位置。

## 二分查找：重复元素区间的左右边界

在 [LC 34 在排序数组中查找元素的第一个和最后一个位置](../../csharp/leetcode/binary-search/find-first-and-last-position-of-element-in-sorted-array.md)中已经使用：

```cpp
int binarySearch(vector<int>& nums, int target, bool lower)
{
    int left = 0;
    int right = static_cast<int>(nums.size()) - 1;
    int answer = static_cast<int>(nums.size());

    while (left <= right)
    {
        int mid = left + (right - left) / 2;

        if (nums[mid] > target || (lower && nums[mid] >= target))
        {
            answer = mid;
            right = mid - 1;
        }
        else
        {
            left = mid + 1;
        }
    }

    return answer;
}
```

- 左端点是第一个 `>= target` 的位置。
- 右端点是第一个 `> target` 的位置减一。
- 目标不存在时必须重新校验 `nums[leftIdx]` 和 `nums[rightIdx]` 是否真的等于 `target`。
- 优先避免用 `target + 1` 来找右边界，因为 `target == INT_MAX` 时有溢出风险。
- 如果找到一个命中点后再向左右扫描，最坏会退化为 O(n)，不满足题目 O(log n) 要求。

## 二维矩阵二分：一维下标映射

在 [LC 74 搜索二维矩阵](../../csharp/leetcode/binary-search/search-a-2d-matrix.md)中已经使用：

```cpp
int m = static_cast<int>(matrix.size());
int n = static_cast<int>(matrix[0].size());
int left = 0;
int right = m * n - 1;

while (left <= right)
{
    int mid = left + (right - left) / 2;
    int value = matrix[mid / n][mid % n];

    if (value == target) return true;
    if (value < target) left = mid + 1;
    else right = mid - 1;
}
```

- 当矩阵满足“下一行首元素大于上一行尾元素”时，可以按行展开成一维有序数组。
- 列数是 `n`，所以一维下标映射为 `row = mid / n`、`col = mid % n`。
- LC74 适合全局二分；LC240 只有行列分别有序，不能按行展开成全局有序数组。

## 二叉树翻转：先保存再交换

在 [LC 226 翻转二叉树](../../csharp/leetcode/binary-tree/invert-binary-tree.md)中已经使用：

```cpp
TreeNode* invertTree(TreeNode* root)
{
    if (root == nullptr)
    {
        return nullptr;
    }

    TreeNode* left = invertTree(root->left);
    root->left = invertTree(root->right);
    root->right = left;
    return root;
}
```

- 空节点先返回，避免访问空指针。
- 如果先覆盖 `root->left`，必须提前保存原左子树或翻转后的左子树。
- 翻转二叉树会修改树结构；判断对称二叉树只比较镜像关系，不应该修改节点连接。

## 对称二叉树：镜像位置成对比较

在 [LC 101 对称二叉树](../../csharp/leetcode/binary-tree/symmetric-tree.md)中已经使用：

```cpp
bool isMirror(TreeNode* left, TreeNode* right)
{
    if (left == nullptr && right == nullptr)
    {
        return true;
    }

    if (left == nullptr || right == nullptr)
    {
        return false;
    }

    return left->val == right->val
        && isMirror(left->left, right->right)
        && isMirror(left->right, right->left);
}
```

- 镜像比较不是同向比较：左子树的左侧要对右子树的右侧。
- 队列写法中，入队也要保持成对顺序：`left->left/right->right`，再 `left->right/right->left`。
- 两个节点都为空时表示这一对镜像位置通过；只有一个为空时才失败。

## 二叉树直径：返回深度，更新全局答案

在 [LC 543 二叉树的直径](../../csharp/leetcode/binary-tree/diameter-of-binary-tree.md)中已经使用：

```cpp
int depth(TreeNode* root)
{
    if (root == nullptr)
    {
        return 0;
    }

    int leftDepth = depth(root->left);
    int rightDepth = depth(root->right);
    maxNodeCount = std::max(maxNodeCount, leftDepth + rightDepth + 1);
    return std::max(leftDepth, rightDepth) + 1;
}
```

- `depth()` 返回给父节点的是当前子树高度，不是直径。
- 全局答案需要在每个节点更新一次，因为最长路径可能不经过根节点。
- 题目要求返回边数；如果全局记录的是节点数，最后要减 1。
- 入口函数要初始化全局状态，避免多组测试之间残留。

## 计划整理内容

- 常用头文件和命名空间
- vector、string、unordered_map、queue、stack、priority_queue
- 排序、比较器、二分变体和二分答案
- 回溯
- 引用传参、返回值和生命周期
- 溢出、下标、迭代器失效和空容器

## 每次新增模板时记录

- 适用题型：
- 最小代码：
- 容易写错的地方：
- 自己验证过的题目：
- 仍未理解：

## 当前状态

- 已使用模板：链表哨兵节点、尾指针拼接、新结果链表构造、删除节点前驱定位、相邻节点重连、随机指针深拷贝、链表归并排序、二叉树 DFS、BST 上下界验证、二叉树 BFS 层序、二叉树层序输出数组、递归中点建树、`std::stack`、`std::queue`、二分左边界、二分右边界、二维矩阵一维下标映射
- 已验证题目：[LC 2 两数相加](../../csharp/leetcode/linked-list/add-two-numbers.md)、[LC 19 删除链表的倒数第 N 个结点](../../csharp/leetcode/linked-list/remove-nth-node-from-end-of-list.md)、[LC 21 合并两个有序链表](../../csharp/leetcode/linked-list/merge-two-sorted-lists.md)、[LC 24 两两交换链表中的节点](../../csharp/leetcode/linked-list/swap-nodes-in-pairs.md)、[LC 35 搜索插入位置](../../csharp/leetcode/binary-search/search-insert-position.md)、[LC 74 搜索二维矩阵](../../csharp/leetcode/binary-search/search-a-2d-matrix.md)、[LC 34 在排序数组中查找元素的第一个和最后一个位置](../../csharp/leetcode/binary-search/find-first-and-last-position-of-element-in-sorted-array.md)、[LC 94 二叉树的中序遍历](../../csharp/leetcode/binary-tree/binary-tree-inorder-traversal.md)、[LC 98 验证二叉搜索树](../../csharp/leetcode/binary-tree/validate-binary-search-tree.md)、[LC 101 对称二叉树](../../csharp/leetcode/binary-tree/symmetric-tree.md)、[LC 102 二叉树的层序遍历](../../csharp/leetcode/binary-tree/binary-tree-level-order-traversal.md)、[LC 104 二叉树的最大深度](../../csharp/leetcode/binary-tree/maximum-depth-of-binary-tree.md)、[LC 108 将有序数组转换为二叉搜索树](../../csharp/leetcode/binary-tree/convert-sorted-array-to-binary-search-tree.md)、[LC 138 复制带随机指针的链表](../../csharp/leetcode/linked-list/copy-list-with-random-pointer.md)、[LC 148 排序链表](../../csharp/leetcode/linked-list/sort-list.md)、[LC 226 翻转二叉树](../../csharp/leetcode/binary-tree/invert-binary-tree.md)、[LC 543 二叉树的直径](../../csharp/leetcode/binary-tree/diameter-of-binary-tree.md)
- 待整理问题：其他容器和算法模板等待实际练习后补充
