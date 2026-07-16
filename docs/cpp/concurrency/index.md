# 并发与内存模型

> 线程只是入口；真正的核心是共享状态、同步关系、对象生命周期与 C++ 内存模型。

!!! warning "先正确，再追求无锁"
    并发错误往往偶发、难复现，并且会被编译器优化放大。第一阶段应熟练使用 RAII 锁、条件变量和任务队列，不要一开始就写无锁容器。

---

## 1. 线程生命周期

```cpp
#include <thread>

void work() {
    // 后台任务
}

int main() {
    std::thread worker(work);
    worker.join();
}
```

- `join()`：等待线程结束并回收关联资源
- `detach()`：线程独立运行，之后更难保证引用对象的生命周期，应谨慎使用
- joinable 的 `std::thread` 析构时会调用 `std::terminate()`
- C++20 可优先考虑 `std::jthread`，它支持停止令牌并在析构时 join

```cpp
#include <stop_token>
#include <thread>

std::jthread worker([](std::stop_token token) {
    while (!token.stop_requested()) {
        // 可协作取消的任务
    }
});
```

---

## 2. mutex 与 RAII 加锁

```cpp
#include <mutex>

std::mutex mutex;
int score = 0;

void add_score(int value) {
    std::lock_guard lock(mutex);
    score += value;
}
```

优先使用：

- `std::lock_guard`：作用域内持锁，简单可靠
- `std::unique_lock`：需要延迟加锁、手动解锁或配合条件变量时使用
- `std::scoped_lock`：一次锁多个 mutex，可降低死锁风险

避免：

- 手写 `lock()` 后在多个分支中手写 `unlock()`
- 持锁期间做耗时 IO、等待主线程或调用未知回调
- 不同路径以不同顺序获取多把锁

---

## 3. 条件变量与生产者/消费者

条件变量用于“等待某个状态成立”，不是用来保存状态：

```cpp
#include <condition_variable>
#include <mutex>
#include <queue>

std::mutex mutex;
std::condition_variable cv;
std::queue<int> jobs;
bool stopping = false;

void consume() {
    while (true) {
        std::unique_lock lock(mutex);
        cv.wait(lock, [] { return stopping || !jobs.empty(); });

        if (stopping && jobs.empty()) {
            return;
        }

        int job = jobs.front();
        jobs.pop();
        lock.unlock();

        // 在锁外处理任务
        (void)job;
    }
}
```

`wait` 必须搭配谓词，因为可能发生虚假唤醒，也可能在开始等待前通知已经发生。

---

## 4. future、promise 与 async

```cpp
#include <future>

auto future = std::async(std::launch::async, [] {
    return 42;
});

int result = future.get();
```

- `future` 表示稍后取得的结果或异常
- `promise` 负责写入结果，`future` 负责读取
- 明确传入 `std::launch::async`，否则实现可能选择延迟执行
- 大量短任务更适合线程池/Job System，而不是每个任务创建一个线程

---

## 5. 数据竞争、原子与内存序

当多个线程并发访问同一内存位置，至少一个是写操作，且没有正确同步时，就会发生数据竞争；在 C++ 中这属于未定义行为。

```cpp
#include <atomic>

std::atomic<int> completed{0};

void finish_job() {
    completed.fetch_add(1, std::memory_order_relaxed);
}
```

常见内存序：

| 内存序 | 用途 |
|--------|------|
| `memory_order_seq_cst` | 默认且最容易推理，先保证正确 |
| `memory_order_relaxed` | 只需要原子性，不建立跨变量顺序 |
| acquire / release | 建立生产者发布、消费者读取的同步关系 |

!!! danger "atomic 不等于线程安全"
    把单个字段改成 `atomic`，不会自动保护多个字段之间的不变量。`shared_ptr` 的引用计数可安全地在不同实例间并发变化，也不代表它指向的对象可以无锁并发读写。

---

## 6. 游戏引擎中的并发关注点

- 主线程、渲染线程、资源 IO 线程之间的数据所有权
- Job System：把大任务拆成有依赖关系的小任务，由固定工作线程执行
- 双缓冲/命令队列：一端写入、另一端消费，减少直接共享可变状态
- False Sharing：不同线程频繁写入同一缓存行中的不同变量，也可能严重拖慢性能
- 帧生命周期：任务引用的场景对象、组件或原生缓冲区是否在任务结束前仍有效
- Unity C# Job System/Burst 的数据约束，与 C++ 数据导向并发设计有相通之处

---

## 面试检查清单

- 进程与线程、并发与并行有什么区别？
- `join` 和 `detach` 的差异是什么？`std::thread` 析构有什么风险？
- 死锁的常见条件是什么？怎样统一锁顺序？
- 条件变量为什么要使用谓词循环？
- 数据竞争为什么是未定义行为？
- mutex 与 atomic 如何选择？CAS 是什么？
- acquire/release 建立了什么同步关系？
- 线程池相对“每任务一线程”有什么优势？

---

## 推荐练习

1. 实现线程安全队列（先用 mutex + condition_variable）
2. 实现固定工作线程数量的线程池
3. 为线程池加入停止、清空任务与异常传递
4. 使用 ThreadSanitizer 或平台工具检测一个故意制造的数据竞争

---

## 参考资料

- [C++ Core Guidelines：Concurrency and parallelism](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines#S-concurrency)
- [cppreference：Concurrency support library](https://en.cppreference.com/w/cpp/thread.html)
- [cppreference：Memory model](https://en.cppreference.com/w/cpp/language/memory_model.html)

> 📎 标签：`C++` `并发` `线程` `mutex` `atomic` `内存模型`
