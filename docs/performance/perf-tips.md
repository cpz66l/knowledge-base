# 优化小 Tips

> 开发中值得注意的性能小知识合集 - 持续补充

---

## 怎么用

每条都是一个**具体可操作**的小优化点，按场景分类。不是系统教程（深度内容见各专题页），而是日常开发的检查清单。

!!! warning "先测量再优化"
    优化前先用 Profiler 找瓶颈（见[性能优化](index.md)的验证原则），别盲目套用。下面的小 tips 是瓶颈定位后的具体手段，不是无脑全开。

---

## UI / UGUI

| 场景 / 坑 | 优化做法 |
|------|------|
| 纯装饰的 Image / Text 每帧参与射线检测 | 取消勾选 `Raycast Target`（详见 [Image](../unity/ugui/controls/image.md)）|
| Draw Call 过多 | 同图集 Sprite 合批，用 Sprite Atlas 打包图集 |
| 改一个 UI 属性触发整个 Canvas 重建 | 静态 UI 与频繁更新的动态 UI 拆到不同 Canvas（嵌套 Canvas 隔离重建范围）|
| 小规模背包 UI 需要同步数据 | 先用事件驱动全量重绘，量级上去再做脏标记和视图复用；项目案例见[背包 UI 与拖拽](../projects/backpack-survivor/inventory-ui-and-drag.md) |
| 矩形裁剪用 `Mask`（带 stencil）会打断合批 | 矩形区域改用 `RectMask2D` |
| Legacy Text 渲染差、重建多 | 换 TextMeshPro（SDF 渲染，详见 [TextMeshPro](../unity/ugui/controls/text-tmp.md)）|

---

## GC / 内存分配

| 场景 / 坑 | 优化做法 |
|------|------|
| Update / 循环里 `new` 对象产生 GC | 用对象池或复用字段（详见 [对象池](memory/object-pool.md)）|
| 字符串用 `+` / `+=` 拼接 | 用 `StringBuilder`，避免每次产生新字符串 |
| Update 里用 LINQ（Where / Select）| LINQ 产生中间集合 + 可能装箱，热路径别用 |
| 值类型被当 `object` 用（`List<object>`、enum 做 key 等）| 警惕装箱，详见 [装箱 - 性能杀手](../csharp/oop/value-vs-reference.md) |
| `foreach` 遍历 `List<T>` | 现代 Unity 已优化；不确定时热路径用 `for` 更稳 |

---

## 渲染 / GPU

| 场景 / 坑 | 优化做法 |
|------|------|
| 大量相同网格不同位置（树、草、敌人）| 开 GPU Instancing |
| 大量小静态物体 | 标记 Static 走静态批处理（Static Batching）|
| 远处仍用高精度模型浪费 | 配 LOD，远处用低精度模型 |
| 被遮挡的物体仍被渲染 | 开 Occlusion Culling 遮挡剔除 |
| 移动端用未压缩纹理 | 用 ASTC 纹理压缩格式 |
| 多余的 Camera | 关闭不用的 Camera，每个都有渲染开销 |

---

## 代码 / CPU

| 场景 / 坑 | 优化做法 |
|------|------|
| Update 里调 `GetComponent` | `Start` 里缓存成字段 |
| 频繁用 `this.transform` | 缓存 `transform` 到字段 |
| 运行时 `GameObject.Find` / `Transform.Find` | 启动时查找并缓存引用 |
| 空的 `Update()` / `Start()` | 删除不用的消息方法，避免 Unity 每帧进行无意义的脚本消息调用 |
| `Debug.Log` 在 Release 仍有开销 | 自定义日志方法加 `[Conditional("DEBUG")]`，Release 自动剔除调用 |
| 低频逻辑放 Update 里轮询 | 用协程 `WaitForSeconds`，按需触发 |
| 大量距离判断每帧开方 | 比较 `sqrMagnitude` 和半径平方；项目案例见[拾取与磁吸](../projects/backpack-survivor/pickup-and-magnet.md) |

---

## 物理 / 资源

| 场景 / 坑 | 优化做法 |
|------|------|
| 物理碰撞对过多 | Layer Collision Matrix 关闭不必要的碰撞对（如 UI 层 vs 玩家层）|
| 大量 Rigidbody | 减少物理对象数量，能 `isKinematic` 就别动态 |
| 高速投射物只检查离散位置，可能跨过薄 Collider | 检测旧位置到新位置的路径；项目案例见[自动武器与投射物](../projects/backpack-survivor/target-registry-and-auto-weapon.md) |
| 高频使用会返回新结果数组的物理查询 | 在 Profiler 证明分配是问题后，复用 NonAlloc 缓冲区；同时处理缓冲区满载、LayerMask 和 Trigger 规则 |
| 频繁播放音效卡顿 | 音频剪辑勾选 `Preload Audio Data`，预加载 |

---

## 一句话原则

- **控制热路径分配**：先测量，再减少 Update / 循环中不必要的 `new`、字符串拼接和 LINQ 临时结果
- **缓存一切频繁访问的引用**：`GetComponent`、`transform`、`Find` 结果
- **距离比较先避开开方**：只需要判断是否进入半径时，用平方距离比较
- **先测量再优化**：Profiler 给方向，小 tips 是手段

---

> 📎 标签：`性能优化` `小贴士` `Unity` `GC` `合批`
