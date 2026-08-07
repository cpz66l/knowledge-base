# 金币掉落与局内经济 HUD

> 项目：[Backpack Survivor](index.md)
>
> 状态：项目中使用
>
> 验证状态：待验证。用户课程记录描述已实现金币掉落、`GoldOrb`、金币散落飞出、局内金币统计和 HUD 显示；本环境完成静态审阅、项目文件只读复核与文档验证，未运行 Unity Editor / Play Mode。
>
> 日期：2026-08-02
>
> 阶段：V0.2 掉落与背包构筑 · 第 24 课

## 学习目标

- 把第 11 课挂账的 `DropCategory.Gold` 从占位分支推进成真实掉落资源。
- 让金币复用已有掉落管线、对象池、散落飞出和磁吸手感，而不是另写一套平行生成系统。
- 用 `GoldOrb.OnCollected` 把收集事实交给 `GameSession`，避免金币球或 HUD 自己记账。
- 让 `RunHudView` 用“订阅变化 + 主动拉快照”的方式显示局内金币。
- 识别 Unity `[SerializeField]` 字段改名后的引用丢失风险，并把 Inspector / YAML 复核纳入验证清单。
- 明确本课只完成局内金币闭环，结算页金币和最终评分留给后续经济模型统一设计。

## 交付范围

| 模块 | 当前职责 |
|---|---|
| `LootTableData.DropCategory.Gold` | 金币品类，继续和经验、装备共用掉落表分流 |
| `LootManager.goldOrbPool` | 金币对象池，`SpawnEntry()` 在 Gold 分支取出 `GoldOrb` |
| `GoldOrb` | 金币掉落物，`IPoolable + ICollectable`，负责旋转、散落飞行、磁吸、收集事件和自然回收 |
| `PickUpMagnet` | 继续提供自动吸附手感，飞行期间临时关闭，落地后恢复 |
| `GameSession.totalGold` | 本局金币事实源，收集金币时累计并广播 |
| `GameSession.OnGoldChanged` | 通知 HUD 和后续表现层刷新金币数 |
| `RunHudView.goldText` | 显示当前本局金币，不保存经济状态 |
| `GoldDrop.asset` | 金币面额表，当前静态可见 5 / 12 / 25 三档金币 |

第 23 课把高价值装备入口交给精英和宝箱。第 24 课补的是另一种经济反馈：金币不再只是 `DropCategory` 中的枚举，而是能从怪物和宝箱掉出来、飞到地上、被磁吸、进入本局统计，并显示在 HUD 上。

```text
掉落系统：决定这次是否出金币、出多少钱
GoldOrb：负责金币在世界里的表现和拾取事件
GameSession：统计本局金币
RunHudView：只显示当前金币
```

## Gold 分支接入掉落管线

`LootManager.SpawnEntry()` 继续是所有掉落的统一入口。第 24 课只是把原来的 Gold 挂账补成对象池生成：

```csharp
else if (entry.category == DropCategory.Gold)
{
    Vector2 randomOffset = Random.insideUnitCircle * offset;
    Vector3 target = position + new Vector3(randomOffset.x, 0, randomOffset.y);

    GoldOrb goldOrb = goldOrbPool.Get(position).GetComponent<GoldOrb>();
    goldOrb.Initialize(entry);
    goldOrb.PlayScatterFlight(position, target);

    return goldOrb.gameObject;
}
```

这比另写 `GoldSpawner` 更稳。敌人死亡、宝箱开箱、丢弃生成、未来商店或 GM 工具都可以继续走 `LootManager.SpawnEntry()`，只在品类分支上选择不同池。

当前静态资产可见 `GoldDrop.asset` 是叶表，三档金币均为 `category: Gold`，权重和面额分别为：

| 金币条目 | 权重 | 面额 |
|---|---:|---:|
| 小堆金币 | 60 | 5 |
| 一袋金币 | 30 | 12 |
| 大袋金币 | 10 | 25 |

普通敌人、精英敌人和宝箱束表已静态可见引用金币子表，但真实掉落频率仍需 Play Mode 采样确认。

## GoldOrb

`GoldOrb` 独立于 `XpOrb`，但复用同一类能力：

```csharp
public class GoldOrb : MonoBehaviour, IPoolable, ICollectable
{
    public static event Action<LootEntry> OnCollected;

    private PickUpMagnet pum;
    private LootEntry lootEntry;
    private float survivalTimer;
    private bool isCollected;
    private Coroutine flightRoutine;
}
```

金币和经验都能磁吸，但语义不同：

```text
XpOrb.OnCollected   -> 经验成长、升级选择
GoldOrb.OnCollected -> 本局经济、HUD 金币
```

拆成两类掉落物，可以复用手感，不混淆资源含义。后续金币倍率、商店、结算评分都不会污染经验升级逻辑。

## 池化与散落飞行

第 24 课延续对象池纪律：新增运行期状态后，同步检查 `OnGetFromPool()`。

```csharp
public void OnGetFromPool()
{
    if (flightRoutine != null)
    {
        StopCoroutine(flightRoutine);
        flightRoutine = null;
    }

    pum.enabled = true;
    pum.StateReset();

    survivalTimer = 0f;
    isCollected = false;
}
```

金币飞出期间会临时关闭磁吸：

```csharp
private IEnumerator FlyRoutine(Vector3 from, Vector3 to)
{
    pum.enabled = false;

    // 抛物线飞到落点

    pum.enabled = true;
    pum.StateReset();
    flightRoutine = null;
}
```

目的不是技术炫技，而是体验分层：

```text
先让玩家看见金币掉出来
再让金币进入自动吸附规则
```

如果飞行刚开始就允许磁吸，玩家看到的可能只是“怪死了，钱消失了，HUD 数字变了”，掉落反馈会弱很多。

## 本局金币事实源

金币属于“一局 Run 的经济状态”，所以由 `GameSession` 统计：

```csharp
private int totalGold;
public int TotalGold => totalGold;

public event Action<int> OnGoldChanged;

private void HandleGoldCollected(LootEntry entry)
{
    if (entry == null) return;
    if (State != GameState.Running) return;

    totalGold += entry.amount;
    OnGoldChanged?.Invoke(totalGold);
}
```

`GoldOrb` 只广播“我被收集了，金额是多少”。它不改 HUD，也不写存档；`RunHudView` 只显示当前值，不拥有金币状态。这样后续结算页、调试面板、商店和局外奖励都可以读同一个事实源。

`StartRun()` 也要清零并广播初始值：

```text
StartRun()
  -> totalGold = 0
  -> OnGoldChanged(0)
```

这保证重开后不会继承上一局金币。

## HUD 初始化

`RunHudView` 订阅 `OnGoldChanged`，同时在 `Start()` 主动拉快照：

```csharp
private void OnEnable()
{
    gameSession.OnGoldChanged += HandleGoldChanged;
}

private void Start()
{
    HandleGoldChanged(gameSession.TotalGold);
}
```

这是事件驱动 UI 的稳定结构：

```text
Start 主动拉当前快照
事件负责后续变化
```

只等事件会受 Unity 生命周期顺序影响。如果 `GameSession.StartRun()` 先广播 0，HUD 后订阅，就会漏掉初始金币显示。

## Unity 字段改名风险

课程记录中暴露了一个典型 Unity 坑：`[SerializeField] private` 字段虽然是 private，但序列化数据按字段名写进 Scene / Prefab。字段从拼错的 `glodOrbPool` 改为 `goldOrbPool` 后，Inspector 引用可能不会自动迁移。

本环境静态检查到：

- `LootManager.cs` 当前字段为 `goldOrbPool`。
- `01-Run.unity` 中 `goldOrbPool` 已有对象引用。
- 静态脚本扫描未发现旧字段名 `glodOrbPool`。

这只能说明当前 YAML 可见引用已经接上，不能替代 Unity Editor 中的 Inspector 与 Play Mode 复核。后续改序列化字段名时，优先考虑：

```csharp
[FormerlySerializedAs("glodOrbPool")]
[SerializeField] private ObjectPool goldOrbPool;
```

确认场景 / Prefab 保存后，再决定是否保留迁移属性。

## 周期链路

### 敌人掉金币

```text
EnemyAI.Die()
  -> lootManager.TrySpawnDrop(health.Position, lootTable)
  -> LootRoller.RollBundle(bundle)
  -> LootManager.SpawnEntry(entry, position)
  -> entry.category == Gold
  -> goldOrbPool.Get(position)
  -> GoldOrb.Initialize(entry)
  -> GoldOrb.PlayScatterFlight(position, target)
```

### 金币进入 HUD

```text
GoldOrb.Collect()
  -> GoldOrb.OnCollected(lootEntry)
  -> GameSession.HandleGoldCollected(entry)
  -> totalGold += entry.amount
  -> OnGoldChanged(totalGold)
  -> RunHudView.HandleGoldChanged(totalGold)
  -> goldText.text = totalGold
```

### 池化复位

```text
OnGetFromPool()
  -> 停止旧 flightRoutine
  -> 启用 PickUpMagnet
  -> StateReset()
  -> survivalTimer = 0
  -> isCollected = false
```

## 常见错误

| 问题 | 根因 | 处理方式 |
|---|---|---|
| 击杀后 Gold 分支空引用 | 字段改名后 `goldOrbPool` 引用丢失 | 检查 Inspector / YAML，必要时用 `[FormerlySerializedAs]` |
| 金币球一出生就被吸走 | 飞行期间仍启用磁吸 | `PlayScatterFlight()` 期间关闭 `PickUpMagnet`，落地后恢复 |
| 金币复用后立刻回池 | `survivalTimer` 没有清零 | `OnGetFromPool()` 重置生存计时 |
| 金币重复加账 | 连续触发 `Collect()` | `isCollected` 做幂等守卫 |
| HUD 初始金币为空 | HUD 订阅晚于开局广播 | `RunHudView.Start()` 主动读取 `TotalGold` |
| GoldOrb 直接改 HUD | 掉落物承担了规则或表现状态 | GoldOrb 广播事件，GameSession 记账，HUD 显示 |
| 本课硬塞结算金币 | 局内经济和结算模型边界未定 | 先完成局内闭环，结算页和最终评分后续统一设计 |

## 如何验证

### 掉落与拾取

- 敌人或宝箱的束表包含金币频道时，能生成 `GoldOrb`。
- `GoldDrop.asset` 的三档面额能通过权重抽取出现。
- 金币先散落到地上，再进入磁吸拾取状态。
- 金币 15 秒未拾取时自然回池。
- 连续进入收集范围只加一次金币，不重复触发 `OnCollected`。

### HUD 与状态

- 开局 HUD 金币显示为 0。
- 收集 5 / 12 / 25 面额金币后，HUD 按累计值刷新。
- 暂停、升级选择、胜利和失败后，非 `Running` 状态不继续累计金币。
- 重开新局后 `totalGold` 清零，HUD 不保留上一局数字。

### 工程边界

- `GoldOrb` 不直接引用 `RunHudView`、`ResultView` 或存档系统。
- `GameSession` 对 `GoldOrb.OnCollected` 的订阅和退订成对。
- `RunHudView` 对 `OnGoldChanged` 的订阅和退订成对。
- `LootManager.goldOrbPool` 在场景中已接入对象池引用。
- 静态扫描未发现旧字段名 `glodOrbPool`、`UnityEditor`、`ShadowCascadeGUI`、`using static BS.GamePlay.Waves.WaveDirector` 或 `Random.Range(0, 1)`。
- 本环境未运行 Unity Editor / Play Mode / Profiler / Player Build；真实掉落频率、HUD 表现、磁吸手感和性能仍需项目内验证。

## 当前证据分层

| 结论 | 证据等级 | 说明 |
|---|---|---|
| 第 24 课实现了金币掉落、金币散落、局内金币统计和 HUD 显示 | B | 来自用户放入 Inbox 的课程记录 |
| `LootManager` 已包含 `goldOrbPool`，Gold 分支会取出 `GoldOrb`、初始化并播放散落飞行 | C | 本环境只读查看外部 Unity 工程脚本 |
| `GoldOrb` 已实现 `IPoolable + ICollectable`、`OnCollected`、幂等收集、15 秒自然回收、飞行协程和磁吸状态复位 | C | 本环境只读查看 `GoldOrb.cs` |
| `GameSession` 已订阅 `GoldOrb.OnCollected`，开局清零 `totalGold`，收集时广播 `OnGoldChanged` | C | 本环境只读查看 `GameSession.cs` |
| `RunHudView` 已订阅 `OnGoldChanged`，并在 `Start()` 主动拉取 `TotalGold` | C | 本环境只读查看 `RunHudView.cs` |
| `GoldDrop.asset` 存在三档金币面额；`GoldOrb.prefab` 挂有 `GoldOrb` 和 `PickUpMagnet` | C | 本环境只读检查资产、Prefab 与 `.meta` |
| `01-Run.unity` 中可见 `goldOrbPool` 和 `goldText` 序列化引用 | C | 本环境只读检查场景 YAML |
| 金币在 Unity Play Mode 中已经按预期掉落、飞散、磁吸、计入 HUD | D | 本环境未运行 Unity 或观察画面 |
| 金币系统已完成 Profiler / Player Build 验证 | D | 未运行 Profiler 或 Player Build |

## 相关内容

- 前置：[精英宝箱与终局压力强化](elite-chests-endgame-pressure.md)
- 前置：[掉落分层与交互拾取](loot-layering-and-interaction.md)
- 前置：[单局框架与基础 HUD](run-session-and-basic-hud.md)
- 后续：[背包价值与物品价值显示](backpack-value-and-item-value-display.md)
- 系统：[胜负结算与重开闭环](run-result-and-restart-loop.md)
- Unity：[Unity 生命周期](../../unity/lifecycle.md)
- 性能：[对象池](../../performance/memory/object-pool.md)
- 检查清单：[Unity 项目能力](../../checklists/unity-project.md)

> 📎 标签：`Unity` `金币掉落` `局内经济` `HUD` `对象池` `磁吸` `序列化字段` `项目实践`
