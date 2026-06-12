# 对象池模式 (Object Pool)

> 用空间换时间，用复用换稳定 —— 游戏开发中最常用的优化模式之一

---

## 为什么需要对象池？

在游戏中，有些对象被频繁地创建和销毁：

- 子弹（一秒几十发）
- 粒子特效
- 音效实例
- 敌人 / NPC
- UI 列表项

每次 `new` / `delete` 有两个代价：

1. **内存分配耗时**：堆分配需要找空闲块，频繁调用会卡顿
2. **内存碎片**：分配大小不一的对象 → 堆碎片化 → 大块连续内存越来越难找
3. **GC 压力**（C#/Java）：频繁分配 → GC 频繁触发 → **帧率抖动**

对象池的思路很简单：**用完后不销毁，放回去下次直接用。**

---

## 核心实现

### 最简版本

```cpp
template<typename T>
class ObjectPool {
public:
    T* Acquire() {
        if (m_inactive.empty()) {
            return new T();
        }
        T* obj = m_inactive.back();
        m_inactive.pop_back();
        return obj;
    }

    void Release(T* obj) {
        obj->Reset();
        m_inactive.push_back(obj);
    }

private:
    std::vector<T*> m_inactive;
};
```

### 改进：预分配 + 索引管理

```cpp
template<typename T, size_t PoolSize = 256>
class FixedObjectPool {
public:
    FixedObjectPool() {
        for (size_t i = 0; i < PoolSize; ++i) {
            m_inactive.push(i);
        }
    }

    std::optional<size_t> Acquire() {
        if (m_inactive.empty()) return std::nullopt;
        size_t idx = m_inactive.front();
        m_inactive.pop();
        m_active.insert(idx);
        return idx;
    }

    void Release(size_t idx) {
        m_active.erase(idx);
        m_pool[idx].Reset();
        m_inactive.push(idx);
    }

    T& Get(size_t idx) { return m_pool[idx]; }

private:
    std::array<T, PoolSize> m_pool;     // 连续内存，cache 友好
    std::queue<size_t>     m_inactive;   // 空闲索引队列
    std::set<size_t>       m_active;     // 使用中索引（调试用）
};
```

---

## 在游戏中的应用

### 子弹系统

```cpp
class BulletPool {
public:
    Bullet* Fire(const FVector& Origin, const FVector& Direction) {
        Bullet* bullet = m_pool.Acquire();
        if (!bullet) {
            bullet = m_pool.ForceAcquire();
        }
        bullet->Init(Origin, Direction);
        return bullet;
    }

    void Recycle(Bullet* bullet) {
        bullet->Deactivate();
        m_pool.Release(bullet);
    }

private:
    ObjectPool<Bullet> m_pool;
};
```

---

## 注意事项

| 问题 | 解决 |
|------|------|
| `Reset()` 忘写导致状态污染 | 在 `Release()` 里强制调用 `Reset()` |
| 池子大小不够 | 运行时动态扩容，或设上限 + 复用最老的 |
| 外部持有已回收对象的指针 | 用索引代替指针，加 generation 校验 |
| 多线程安全 | 加锁，或使用无锁队列 |

---

## 项目中的实际效果

在 FPS Demo 中，将子弹从 `new/delete` 改为对象池后：

```
优化前：GC spike 每帧 ~2ms
优化后：GC spike = 0ms，Acquire/Release < 0.01ms
```

---

## 延伸阅读

- 《Game Programming Patterns》第 3 章 —— Robert Nystrom
- Unreal Engine 源码：`UObject` 的内存管理机制
- Unity DOTS：`EntityManager` 的 Chunk 分配策略
