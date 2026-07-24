# 拾取与磁吸

> 项目：[Backpack Survivor](index.md)
>
> 状态：用户课程记录描述已实现；本环境完成静态审阅与文档验证，未重新运行 Unity
>
> 日期：2026-07-24
>
> 阶段：V0.2 掉落与背包构筑 · 第 8 课

## 学习目标

- 把掉落物从“超时回收的奖品”推进到“可被玩家收取的物品”。
- 用两态状态机表达 Idle 与 Attracted，避免磁吸逻辑散落在 `DropItem` 中。
- 用静态事件作为临时收货口，让掉落物不直接依赖背包系统。
- 处理对象池复用下的速度、状态机、计时器和事件订阅重置。

## 交付范围

| 模块 | 当前职责 |
|---|---|
| `PickUpMagnet` | 磁吸状态机，检测玩家距离，进入吸附状态后加速飞向玩家 |
| `DropItem` | 保存 `LootEntry` 身份，提供 `Collect()`，广播 `OnCollected` 后回池 |
| `PickupLogger` | 临时订阅者，用日志验证拾取事件，第 9 课由背包替换 |
| `BasicEnemyLoot.asset` | 补齐掉落条目的 `dropPrefab` 引用，让掉落物有可识别身份 |

原始记录描述的完整链路是：

```text
DropItem 从池中取出
  ↓
OnGetFromPool：清零 survivalTimer，重置 PickUpMagnet
  ↓
Idle：原地自转并检查玩家水平距离
  ↓
进入 attractRange
  ↓
Attracted：速度随时间累加，朝玩家移动
  ↓
进入 collectRange
  ↓
DropItem.Collect()
  ↓
OnCollected?.Invoke(lootEntry)
  ↓
Recycle() 回池
```

本页将这条链路记录为用户项目实践。当前知识库环境没有完整 Unity 工程、Prefab、`.meta`、场景、输入数据或 Profiler 记录，因此只声明完成静态审阅与文档构建验证，不声称本次亲自在 Unity 中运行通过。

## 状态机拆分

磁吸逻辑独立为 `PickUpMagnet`，而不是继续塞进 `DropItem`。这样 `DropItem` 负责“我是谁、如何被收取、如何回池”，`PickUpMagnet` 负责“我何时飞向玩家、如何飞过去”。

```csharp
private enum MagnetState
{
    Idle,
    Attracted,
}
```

最小状态切换：

```text
Idle
  └─ 玩家进入 attractRange → Attracted
Attracted
  └─ 玩家进入 collectRange → Collect
```

这种拆分留下了复用入口：未来全屏磁铁道具可以遍历场上掉落物，对每个 `PickUpMagnet` 调用 `StartAttract()`，不用改 `DropItem`。

## 磁吸移动

原始实现使用平方距离比较，避免每帧开方：

```csharp
Vector3 direction = playerHealth.Position - transform.position;
direction.y = 0f;
float sqrDistance = direction.sqrMagnitude;

if (sqrDistance < attractRange * attractRange)
{
    StartAttract();
}
```

进入吸附状态后，速度随时间累加并封顶：

```csharp
private void MoveTowardsPlayer()
{
    currentSpeed += acceleration * Time.deltaTime;
    currentSpeed = Mathf.Min(currentSpeed, maxSpeed);
    transform.position += direction.normalized * currentSpeed * Time.deltaTime;
}
```

这比匀速移动更有“被吸过去”的手感。需要注意的是，`direction.normalized` 在距离极小时可能接近零向量；当前代码先用 `collectRange` 判定收取，通常能避开这个问题，但正式工程仍应把“极小距离直接收取”作为边界测试。

## 收货口事件

第 8 课把 `DropItem` 从“只有稀有度颜色”升级成“保存完整 `LootEntry` 身份”的掉落物：

```csharp
public static event Action<LootEntry> OnCollected;

public void Initialize(LootEntry lootEntry)
{
    this.lootEntry = lootEntry;
    // 根据 lootEntry.rarity 设置表现
}

public void Collect()
{
    OnCollected?.Invoke(lootEntry);
    Recycle();
}
```

`Collect()` 和 `Recycle()` 要分清：

- `Collect()` 表示玩家收取，应该广播物品身份，再回池。
- `Recycle()` 只表示生命周期结束或超时消失，不应该发货。

这和第 7 课“先掉落，再回收敌人”属于同一规则：事件结算应发生在对象休眠之前。

## 静态事件的边界

`DropItem.OnCollected` 是静态事件，订阅者不需要拿到某一个掉落物实例就能收听全场拾取。

```csharp
private void OnEnable()
{
    DropItem.OnCollected += HandleCollected;
}

private void OnDisable()
{
    DropItem.OnCollected -= HandleCollected;
}
```

静态事件的代价是生命周期很长。订阅者忘记退订时，事件会继续持有订阅者方法引用，轻则重复响应，重则阻止对象被释放。当前 `PickupLogger` 是临时听众，第 9 课背包接管后，也必须保持 `OnEnable +=` / `OnDisable -=` 成对出现。

## 池化重置

第 8 课新增了两个必须随复用重置的运行期状态：

```csharp
public void StateReset()
{
    magnetState = MagnetState.Idle;
    currentSpeed = 0f;
}
```

如果只把状态改回 Idle，却忘记清零 `currentSpeed`，掉落物下次出场可能继承上一次的吸附速度。池化对象需要重置的不只是“看得见的状态”，还包括内部计时器、速度、状态机、目标引用和临时表现。

## Unity 假 null

原始资料记录了一个典型排查点：Unity 对象被销毁后，托管引用未必是真正的 C# `null`。`obj?.name` 这样的空条件访问不会触发 Unity 重载的 `== null`，对象已销毁时仍可能抛出 `MissingReferenceException`。

本项目里可以先按两类处理：

- 纯 C# 对象、`LootEntry` 等普通引用：可以使用 `?.` 简化判空。
- `GameObject`、`Component`、`Transform`、`ScriptableObject` 等 `UnityEngine.Object`：若可能被销毁，优先使用 `obj == null` 判断，再访问成员。

第 8 课 `PickupLogger` 里的 `entry.dropPrefab?.name` 对“配置字段就是 null”有帮助；如果 `dropPrefab` 引用指向被销毁的 Unity 对象，还需要更谨慎的 Unity 判空路径。

## 常见错误

| 问题 | 根因 | 处理方式 |
|---|---|---|
| `PickupLogger` 空引用 | 掉落表条目的 `dropPrefab` 没有配置 | 代码堆栈定位后检查数据资产，不能只盯脚本 |
| 吸过一次后下次高速飞走 | `currentSpeed` 未在回池后清零 | `OnGetFromPool()` 调用 `StateReset()`，同时重置状态与速度 |
| 掉落物超时也进入背包 | 把发货逻辑放在 `Recycle()` | 只有 `Collect()` 广播 `OnCollected`，超时只回池 |
| 静态事件重复响应 | 订阅者启用多次但未退订 | `OnEnable` / `OnDisable` 成对订阅和取消 |
| `UnityEditor.*` 混入运行时代码 | IDE 自动补全错误命名空间 | 运行时代码不引用 `UnityEditor`，否则打包阶段会失败 |
| 文件名 `Magent` 拼写错误 | 在文件系统中手动改名容易影响 `.meta` | Unity 脚本重命名优先在编辑器内完成，保留 GUID 引用 |
| 每帧磁吸距离判断开销扩大 | 使用 `Vector3.Distance` / `magnitude` 做大量距离比较 | 半径也平方，用 `sqrMagnitude` 比较 |

## 如何验证

### 功能验证

- 掉落物生成后处于 Idle，自转和超时计时正常。
- 玩家进入磁吸半径后只切一次 Attracted。
- 吸附速度从 0 增加到 `maxSpeed`，不会继承上一次速度。
- 玩家进入拾取半径后只触发一次 `Collect()`。
- `PickupLogger` 或后续背包只收到被玩家拾取的物品，不收到超时回收物品。
- `lootEntry`、`dropPrefab` 和 `rarity` 在拾取事件中与掉落表配置一致。

### 生命周期与性能验证

- 掉落物回池后再次取出，`survivalTimer`、`currentSpeed`、`magnetState`、颜色和 `lootEntry` 都是本轮数据。
- `PickupLogger` 禁用后不再响应拾取事件，重新启用后只响应一次。
- 大量掉落物同帧吸附和收取时，背包/UI/音效等订阅者能够批量处理副作用，不因每个事件都刷新 UI 而卡顿。
- 用 Profiler 观察同屏掉落物的 `Update`、距离判断、事件广播、回池和 GC Alloc；没有数据前不写“性能已优化”结论。

## 当前证据分层

| 结论 | 证据等级 | 说明 |
|---|---|---|
| 第 8 课实现了磁吸状态机、拾取事件和临时日志订阅者 | B | 来自用户放入 Inbox 的课程记录 |
| `Collect()` 与 `Recycle()` 应分离，避免超时回收误发货 | C | 根据代码职责与事件语义静态审阅 |
| 静态事件必须成对订阅/退订，否则有生命周期风险 | C | 根据 C# 事件和 Unity 生命周期推断 |
| 第 8 课已在当前环境 Unity 场景运行通过 | D | 未提供完整工程、Prefab、`.meta`、场景或运行日志，本次未声明通过 |
| `sqrMagnitude` 已带来可量化性能收益 | D | 缺少 Profiler 对照数据，只记录设计动机 |

## 相关内容

- [掉落系统与保底机制](loot-drop-and-pity.md)
- [背包纯数据网格](inventory-data-grid.md)
- [刷怪器与对象池](spawner-and-object-pooling.md)
- [Unity 生命周期](../../unity/lifecycle.md)
- [委托与事件](../../csharp/oop/delegates-and-events.md)
- [优化小 Tips](../../performance/perf-tips.md)

> 📎 标签：`Unity` `拾取系统` `磁吸` `状态机` `静态事件` `对象池` `项目实践`
