# 掉落系统与保底机制

> 项目：[Backpack Survivor](index.md)
>
> 状态：用户课程记录描述已实现；本环境完成静态检查与文档验证，未重新运行 Unity
>
> 日期：2026-07-23
>
> 阶段：V0.2 掉落与背包构筑 · 第 7 课

## 学习目标

- 用 `ScriptableObject` 表达掉落表，把配置数据和运行时代码分开。
- 用权重随机实现“一次掷骰，必中且只中一个”的掉落选择。
- 用保底计数处理连续未掉出稀有物品的体验问题。
- 让敌人死亡、掉落生成、对象池取出、掉落物回收形成完整生命周期。

## 交付范围

| 模块 | 当前职责 |
|---|---|
| `LootTableData` | 用 `ScriptableObject` 保存掉落条目、稀有度和权重 |
| `LootRoller` | 普通 C# 类，负责权重随机和保底计数 |
| `LootManager` | 场景入口，读取掉落表，调用掷骰器，再从对象池生成掉落物 |
| `DropItem` | 掉落物表现，接入 `IPoolable`，按稀有度变色并超时回收 |
| `EnemyAI.Die` | 在敌人归还对象池前结算掉落 |

原始记录描述的链路是：

```text
敌人死亡
  ↓
LootManager.TrySpawnDrop(position)
  ↓
LootRoller.Roll(lootTable)
  ↓
dropPool.Get(position)
  ↓
DropItem.Initialize(rarity)
  ↓
DropItem 超时 Return 到对象池
```

本页将这条链路记录为用户项目实践。当前知识库环境没有完整 Unity 工程、Prefab、`.meta`、场景和 Profiler 数据，因此只声明完成了静态审阅和文档构建验证，不声称本次亲自在 Unity 中运行通过。

后续第 11 课已经把本页的单层掉落表演进为“两级掉落表 + 品类分流”，并修正了“经验球不进入装备保底计数”的边界，详见[掉落分层与交互拾取](loot-layering-and-interaction.md)。第 22 课继续把 `LootEntry` 扩展为背包物品源头数据，新增标签、接口方向、结算价值和效果强度，详见[内容面铺开](content-expansion-fire-rate-boost.md)。

## 分层设计

```text
EnemyAI
  └─ 触发死亡结果
LootManager
  └─ 组装掉落表、掷骰器和对象池
LootRoller
  └─ 纯算法：权重随机 + 保底
LootTableData
  └─ 纯配置：Prefab、稀有度、权重
DropItem
  └─ 表现与生命周期：颜色、自转、超时回收
```

这节课最重要的结构不是“掉一个球”，而是把数据、算法、场景入口和表现拆开：

- `LootTableData` 是策划可调配置，不负责执行随机。
- `LootRoller` 不继承 `MonoBehaviour`，不依赖场景对象，理论上可以脱离 Unity 场景做概率和保底测试。
- `LootManager` 是组装层，负责把“抽到了什么”转换为“在场景中生成什么”。
- `DropItem` 只关心自己被取出后的表现和回收，不主动查找敌人或掉落表。

## 掉落表配置

`LootTableData` 用 `ScriptableObject` 保存一组条目：

```csharp
[CreateAssetMenu(fileName = "NewLootTable", menuName = "BackpackSurvivor/LootTable")]
public class LootTableData : ScriptableObject
{
    [Serializable]
    public class LootEntry
    {
        public GameObject dropPrefab;
        public Rarity rarity;
        public int weight;
    }

    public LootEntry[] entries;

    public int TotalWeight
    {
        get
        {
            int total = 0;
            if (entries == null)
            {
                return 0;
            }

            foreach (LootEntry entry in entries)
            {
                if (entry != null && entry.weight > 0)
                {
                    total += entry.weight;
                }
            }

            return total;
        }
    }
}
```

注意当前原始实现里 `dropPrefab` 已经进入配置，但 `LootManager` 仍然只从一个 `dropPool` 取对象，并只把 `rarity` 传给 `DropItem`。这说明项目还处在灰盒阶段：如果未来不同掉落物真的对应不同 Prefab，需要演进为“按条目选择对应池”或“统一掉落 Prefab + 运行时配置内容”。

## 权重随机

权重随机的核心是把所有有效权重铺成一条数轴：

```text
Common:   weight 70  → [0, 70)
Uncommon: weight 20  → [70, 90)
Rare:     weight 10  → [90, 100)
```

在 `[0, total)` 中掷一个随机点，再用累加区间命中条目。这样一次掷骰只会返回一个结果，并且概率自然归一。它比“每个条目各掷一次概率”更稳定，因为后者可能全不中，也可能同时中多个。

```csharp
private LootEntry PickByWeight(LootEntry[] entries)
{
    int total = 0;
    foreach (LootEntry entry in entries)
    {
        if (entry != null && entry.weight > 0)
        {
            total += entry.weight;
        }
    }

    if (total <= 0)
    {
        return null;
    }

    int roll = UnityEngine.Random.Range(0, total);
    int accum = 0;

    foreach (LootEntry entry in entries)
    {
        if (entry == null || entry.weight <= 0)
        {
            continue;
        }

        accum += entry.weight;
        if (roll < accum)
        {
            return entry;
        }
    }

    return null;
}
```

当前条目数量很少，线性扫描足够清晰。若后续掉落表非常大，可以预计算前缀和，再用二分查找把单次抽取从 O(n) 降到 O(log n)，但那会引入配置变更后的缓存刷新问题。

## 保底机制

`pityCount` 记录连续未抽中 `Rare` 及以上的次数。达到阈值后，下一次只在稀有池里按权重抽；自然抽中稀有或保底抽中稀有后都要清零。

原始思路是正确的，但静态检查发现一个边界：`PickByWeight` 可能返回 `null`，如果随后直接访问 `result.rarity`，当掉落表全是空条目或零权重时会触发空引用。更稳妥的结构应先判空：

```csharp
public LootEntry Roll(LootTableData table)
{
    if (table == null || table.entries == null || table.entries.Length == 0)
    {
        return null;
    }

    if (pityCount >= pityThreshold)
    {
        LootEntry[] rareEntries = Array.FindAll(
            table.entries,
            entry => entry != null
                && entry.weight > 0
                && entry.rarity >= Rarity.Rare);

        LootEntry pityResult = PickByWeight(rareEntries);
        if (pityResult != null)
        {
            pityCount = 0;
            return pityResult;
        }
    }

    LootEntry result = PickByWeight(table.entries);
    if (result == null)
    {
        return null;
    }

    if (result.rarity >= Rarity.Rare)
    {
        pityCount = 0;
    }
    else
    {
        pityCount++;
    }

    return result;
}
```

还需要明确 `pityThreshold <= 0` 的语义：是禁止保底、立即保底，还是视为配置错误。正式项目里建议在 `LootManager` 初始化时对阈值做限制或日志提示。

## 掉落入口

`LootManager` 的职责是把配置、算法和对象池串起来：

```csharp
public void TrySpawnDrop(Vector3 position)
{
    LootEntry entry = lootRoller.Roll(lootTable);
    if (entry == null)
    {
        return;
    }

    GameObject obj = dropPool.Get(position);
    DropItem dropItem = obj.GetComponent<DropItem>();
    if (dropItem == null)
    {
        dropPool.Return(obj);
        return;
    }

    dropItem.Initialize(entry.rarity);
}
```

这类入口要把失败路径集中处理：掉落表为空、总权重为 0、池未配置、池对象缺少 `DropItem`、`LootRoller` 尚未初始化都应安全失败。当前原始记录只展示了核心路径，正式工程需要把这些配置错误转成可观察日志。

`EnemyAI.Die()` 中生成掉落必须发生在 `pool.Return(gameObject)` 之前。归还后敌人会被停用，死亡位置、事件上下文和后续副作用都容易变得含糊。更广的规则是：死亡事件的结果应在死亡对象仍处于可读状态时结算完。

## DropItem 生命周期

掉落物复用了第 5 课的 `ObjectPool` / `IPoolable` 协议：

```text
Get(position)
  ↓
SetPool + OnGetFromPool
  ↓
Initialize(rarity)
  ↓
Update 自转与计时
  ↓
survivalTimer >= survivalTime
  ↓
pool.Return(gameObject)
```

最关键的复用状态是 `survivalTimer`，它必须在每次取出时清零，否则旧掉落物再次出现后可能立刻回收。

原始 `DropItem.Awake()` 里用 `GameObject.CreatePrimitive(PrimitiveType.Sphere)` 创建灰盒模型，并用 `Renderer.material.color` 改颜色。这适合快速验证，但后续有两个演进方向：

- 美术资源稳定后，把模型、碰撞、材质和子物体放进 Prefab，而不是运行时创建。
- 同屏掉落物很多时，优先评估 `MaterialPropertyBlock`，避免为每个掉落物隐式实例化材质。

## 常见错误

| 问题 | 根因 | 处理方式 |
|---|---|---|
| `lootManager` 找不到或跨方法失效 | 在方法内写了 `LootManager lootManager = ...`，创建的是局部变量 | 跨方法使用的引用应是成员字段，赋值时不要再写类型名 |
| 一只怪掉两个物品 | `Die()` 和 `OnReturnPool()` 都触发掉落 | 掉落只属于死亡事件，不属于回池事件 |
| 零权重表触发空引用 | `PickByWeight` 返回 `null` 后继续访问 `result.rarity` | 抽取结果先判空，再读稀有度 |
| 掉落物刚出现就消失 | 池化复用时没有清零 `survivalTimer` | 在 `OnGetFromPool()` 重置计时器 |
| 掉落表里的 Prefab 没生效 | 配置里有 `dropPrefab`，但入口只使用单一 `dropPool` | 明确是统一掉落表现，还是为不同条目建立不同池 |
| 每次取出敌人都全局查找管理器 | `FindAnyObjectByType<LootManager>()` 放在复用路径上 | 可先接受灰盒方案；后续改成序列化引用、生成器注入或缓存服务 |

## 如何验证

### 算法验证

- 空表、`entries = null`、全零权重、负权重条目都安全返回 `null`。
- 固定随机种子或替换随机源后，权重区间命中符合预期。
- 连续未中稀有时，`pityCount` 按次数累加。
- 达到保底阈值后只从 `Rare` 及以上条目抽取。
- 自然抽中稀有和保底抽中稀有都会清零。

### Unity 场景验证

- 敌人死亡时只掉落一次，且掉落位置使用敌人死亡位置。
- 掉落生成发生在敌人归还对象池之前。
- 掉落物颜色与 `Rarity` 对应关系一致。
- 掉落物超时后回到池，再次取出时计时器、颜色和表现状态正确重置。
- 池预热不足时是否扩容、扩容次数和 GC Alloc 需要用 Profiler 记录。
- 不同掉落 Prefab、Collider、Layer、拾取半径和地形合法性仍需第 8 课继续验证。

## 当前证据分层

| 结论 | 证据等级 | 说明 |
|---|---|---|
| 第 7 课设计了掉落表、权重随机、保底和掉落物池化生命周期 | B | 来自用户放入 Inbox 的课程记录 |
| `LootRoller` 可以作为纯算法类与 Unity 场景入口分离 | C | 根据代码结构静态审阅 |
| 原始 `Roll()` 在零权重/无有效条目下存在 `result.rarity` 空引用风险 | C | 根据 `PickByWeight` 可能返回 `null` 的控制流推断 |
| 掉落系统已在当前环境 Unity 场景运行通过 | D | 未提供完整工程、Prefab、`.meta`、场景或运行日志，本次未声明通过 |
| 池化掉落物显著降低 GC 或帧时间 | D | 缺少 Profiler 对照数据，暂不写成性能结论 |

## 相关内容

- [刷怪器与对象池](spawner-and-object-pooling.md)
- [掉落分层与交互拾取](loot-layering-and-interaction.md)
- [内容面铺开](content-expansion-fire-rate-boost.md)
- [敌人追击、近战与死亡流程](enemy-ai-and-melee.md)
- [Unity 生命周期](../../unity/lifecycle.md)
- [对象池专题](../../performance/memory/object-pool.md)
- [委托与事件](../../csharp/oop/delegates-and-events.md)

> 📎 标签：`Unity` `掉落系统` `ScriptableObject` `权重随机` `保底机制` `对象池` `项目实践`
