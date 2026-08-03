# 精英宝箱与终局压力强化

> 项目：[Backpack Survivor](index.md)
>
> 状态：用户课程记录描述已实现普通/精英敌人分池、宝箱品质曲线、终局高压精英潮、GLB 闪白修复和波次下发奖励参数；本环境完成静态审阅、项目文件只读复核与文档验证，未运行 Unity Editor / Play Mode
>
> 日期：2026-08-02
>
> 阶段：V0.2 掉落与背包构筑 · 第 23 课

## 学习目标

- 把普通敌人、精英敌人和宝箱的奖励职责拆开，避免普通怪长期承担高价值装备入口。
- 让 `WaveDirector` 同时调度敌人压力、精英概率、宝箱频率和宝箱品质权重。
- 用 `normalEnemyPool / eliteEnemyPool` 让精英怪成为刷怪器的一种池选择结果，而不是另写一套生成系统。
- 识别 Unity `Random.Range(int, int)` 上限排他的坑，概率判断改用 `Random.value`。
- 用单一 `GetWeightForTier()` 规则源处理宝箱权重，避免“算总权重”和“找命中”两轮逻辑分叉。
- 针对 GLB 模型受击反馈，区分事件链路和材质表现问题，并用临时材质替换 + `OnDisable()` 恢复解决池化残留。

## 交付范围

| 模块 | 当前职责 |
|---|---|
| `EnemySpawner` | 执行刷怪；按 `eliteSpawnChance` 在普通/精英对象池之间选择 |
| `normalEnemyPool / eliteEnemyPool` | 分别生成普通敌人与精英敌人，保留同一套刷怪入口 |
| `WaveDirector.WaveStage` | 在时间阶段上集中配置刷怪间隔、场上上限、精英率、宝箱击杀间隔、宝箱上限和宝箱品质权重 |
| `ChestSpawner.ApplyWaveSettings()` | 接收当前波次的宝箱节奏和品质权重覆盖 |
| `ChestTierWeight` | 用 `chestName + weight` 表达当前阶段对某种宝箱品质的权重覆盖 |
| `GetWeightForTier()` | 宝箱权重单一规则源；阶段权重优先，缺失时回退默认权重 |
| `DamageFlashView` | 用临时 `flashMaterial` 替换 GLB 渲染器材质，闪白结束或回池时恢复原 `sharedMaterials` |

第 22 课把物品源头、长期掉落池和第一条可堆叠邻接收益铺开。第 23 课解决的是 15 分钟 Demo 的节奏层：玩家不只是看到怪变多，还能感受到前期发育、中期上压、后期精英潮和高品质宝箱期待。

```text
普通怪：经验为主，保留低概率小掉落
精英怪：优秀 / 稀有装备入口
宝箱：更高品质和惊喜入口
终局：高压力 + 高品质期待
```

## 普通与精英分池

`EnemySpawner` 从单一敌人池演进为普通/精英两个池：

```csharp
[SerializeField] private ObjectPool normalEnemyPool;
[SerializeField] private ObjectPool eliteEnemyPool;
[SerializeField, Range(0f, 1f)] private float eliteSpawnChance;

private ObjectPool PickEnemyPool()
{
    if (eliteEnemyPool == null) return normalEnemyPool;

    float randomValue = Random.value;
    if (randomValue < eliteSpawnChance)
        return eliteEnemyPool;

    return normalEnemyPool;
}
```

精英不是写死在 `WaveDirector` 里的特殊生成命令，而是刷怪器当前参数的一部分。这样 `EnemySpawner` 仍然只负责“到时间、找点、取池对象”，不会长成第二个波次导演。

这里也修掉一个容易误判的概率坑：

```text
Random.Range(0, 1)      // int 重载，只会返回 0
Random.value            // float，范围 0.0~1.0
```

离散索引可以用整数 `Random.Range`，概率掷骰更适合 `Random.value`。

## 敌人和奖励职责

第 23 课新增 `NormalEnemy.prefab` 与 `EliteEnemy.prefab`，并让它们挂不同掉落表。第 24 课在这个奖励分层之后补上金币子表、`GoldOrb` 掉落表现和局内经济 HUD，让经验、装备和金币三条反馈更清晰。静态资产抽样显示：

| Prefab | 静态可见差异 |
|---|---|
| `NormalEnemy.prefab` | 使用普通敌人掉落表，缩放为 `1` |
| `EliteEnemy.prefab` | 使用精英敌人掉落表，缩放为 `1.5` |

掉落职责也被拆开：

| 来源 | 当前职责 |
|---|---|
| 普通敌人 | 经验为主，低概率装备掉落 |
| 精英敌人 | 更高概率装备入口，承担优秀 / 稀有装备期待 |
| 宝箱 | 高品质奖励入口，随阶段提高品质权重 |

这比“普通怪也高概率掉好东西”更像游戏经济。普通怪如果长期掉稀有装备，玩家就不会期待精英和宝箱，奖励节奏也会变得扁平。

## WaveStage 同时调敌人和宝箱

第 18 课的 `WaveStage` 只调刷怪压力。第 23 课把它扩展成“压力 + 奖励”的阶段配置：

```csharp
[Serializable]
public class WaveStage
{
    public float startTimeSeconds;
    public float spawnInterval;
    public int maxAlive;
    public string stageName;
    public Color displayColor;

    [Range(0f, 1f)] public float eliteSpawnChance;

    public int chestKillsToSpawn;
    public int chestMaxFieldCount;
    public ChestSpawner.ChestTierWeight[] chestTierWeights;
}
```

`WaveDirector` 在阶段切换时分别把参数下发给敌人生成器和宝箱生成器：

```csharp
enemySpawner.ApplyWaveSettings(
    stage.spawnInterval,
    stage.maxAlive,
    stage.eliteSpawnChance);

chestSpawner.ApplyWaveSettings(
    stage.chestKillsToSpawn,
    stage.chestMaxFieldCount,
    stage.chestTierWeights);
```

这保持了清楚的职责边界：

```text
WaveDirector：什么时候、什么压力、什么奖励倾向
EnemySpawner：按当前参数刷敌人
ChestSpawner：按当前参数计数、选点、抽品质、生成宝箱
```

## 15 分钟压力曲线

课程记录中的当前曲线是“前期发育，后期考试”：

| 时间 | 阶段名 | 刷怪间隔 | 场上上限 | 精英率 | 宝箱击杀间隔 | 宝箱上限 |
|---:|---|---:|---:|---:|---:|---:|
| 0s | 洒洒水 | 2.0 | 8 | 0% | 10 | 2 |
| 180s | 简单 | 1.5 | 15 | 5% | 15 | 2 |
| 360s | 普通 | 0.6 | 20 | 10% | 25 | 3 |
| 600s | 上压力 | 0.3 | 25 | 20% | 30 | 4 |
| 780s | 终局 | 0.1 | 35 | 30% | 35 | 5 |

前期宝箱频率更友好，帮助玩家构筑成型；中后期奖励间隔变长，敌人密度和精英比例上升，用压力检验背包构筑是否站得住。

当前选择“终局精英潮”而不是立刻做 Boss，是 Demo 冲刺期的成本判断。Boss 需要技能、读招、演出、奖励和失败反馈；精英潮复用已有敌人池、波次、掉落和 HUD，更容易在短时间内形成可见体验闭环。

## 宝箱品质曲线

宝箱奖励不只看“多久出一个”，还要看“出什么品质”。第 23 课把品质权重交给 `WaveStage.chestTierWeights`：

| 阶段 | 普通 | 不普通 | 稀有 | 史诗 |
|---|---:|---:|---:|---:|
| 洒洒水 | 80 | 20 | 0 | 0 |
| 简单 | 65 | 30 | 5 | 0 |
| 普通 | 45 | 40 | 15 | 0 |
| 上压力 | 25 | 45 | 25 | 5 |
| 终局 | 10 | 35 | 40 | 15 |

这样终局不只是更危险，也更有奖励期待。风险和收益一起上升，玩家才会愿意撑到最后几分钟。

## 权重随机单一规则源

`ChestTier.weight` 是默认权重，`currentTierWeights` 是当前阶段覆盖权重。权重获取被收束到一个函数：

```csharp
private int GetWeightForTier(ChestTier tier)
{
    if (tier == null) return 0;

    if (currentTierWeights != null)
    {
        foreach (var tierWeight in currentTierWeights)
        {
            if (tierWeight == null) continue;
            if (tierWeight.chestName == tier.chestName)
                return Mathf.Max(0, tierWeight.weight);
        }
    }

    return Mathf.Max(0, tier.weight);
}
```

`PickByWeight()` 的两轮循环都调用同一个函数：

```csharp
int total = 0;
foreach (var t in tiers)
{
    int weight = GetWeightForTier(t);
    if (weight <= 0) continue;
    total += weight;
}

int roll = UnityEngine.Random.Range(0, total);
int accum = 0;
foreach (var t in tiers)
{
    int weight = GetWeightForTier(t);
    if (weight <= 0) continue;

    accum += weight;
    if (roll < accum)
        return t;
}
```

这能避免一个隐性 bug：第一轮把默认回退权重算进总数，第二轮却只查阶段权重，导致 `roll` 落到回退区间时找不到命中项。权重随机表最怕“双规则”，总权重和命中返回必须共用同一个取权重函数。

## GLB 受击闪白

新 GLB 模型导入后，旧的 `renderer.material.color` 闪白方式不再可靠。课程记录的排查顺序是正确的：先确认 `Health.OnDamaged -> DamageFlashView.HandleDamaged` 事件链路能触发，再判断问题在材质表现层。

当前改为临时替换材质：

```csharp
private void ApplyFlashMaterial()
{
    if (flashMaterial == null) return;

    for (int i = 0; i < renderers.Length; i++)
    {
        Renderer renderer = renderers[i];
        if (renderer == null) continue;

        Material[] flashMaterials = new Material[renderer.sharedMaterials.Length];
        for (int j = 0; j < flashMaterials.Length; j++)
            flashMaterials[j] = flashMaterial;

        renderer.sharedMaterials = flashMaterials;
    }
}
```

并在闪白结束或对象禁用时恢复：

```csharp
private void OnDisable()
{
    if (flashRoutine != null)
    {
        StopCoroutine(flashRoutine);
        flashRoutine = null;
    }

    RestoreMaterials();
}
```

这个方案比改颜色粗暴，但对 Demo 更稳：它不依赖原 Shader 是否支持 `_Color` 或 `_BaseColor`。代价是必须缓存并恢复每个 Renderer 的 `sharedMaterials`，否则池化敌人可能带着闪白材质回池。

## 周期链路

### 精英生成

```text
GameSession.Running
  -> WaveDirector 读取 Elapsed
  -> 进入新的 WaveStage
  -> EnemySpawner.ApplyWaveSettings(spawnInterval, maxAlive, eliteSpawnChance)
  -> EnemySpawner 到时间尝试生成
  -> PickEnemyPool()
  -> normalEnemyPool / eliteEnemyPool
  -> 敌人出场并进入追击 / 攻击 / 死亡流程
```

### 宝箱节奏

```text
WaveDirector 阶段切换
  -> ChestSpawner.ApplyWaveSettings(killsToSpawn, maxFieldCount, chestTierWeights)
  -> EnemyAI.OnEnemyDied
  -> ChestSpawner.AddKillsCount()
  -> killsCount 达标
  -> TryFindSpawnPoint()
  -> PickByWeight()
  -> LootChest.Initialize(chestName, color, bundle)
```

### GLB 闪白

```text
Health.TakeDamage()
  -> OnDamaged
  -> DamageFlashView.HandleDamaged()
  -> 停止旧协程，启动新 FlashRoutine
  -> ApplyFlashMaterial()
  -> 等待 flashDuration
  -> RestoreMaterials()
  -> OnDisable 再兜底恢复，防池化残留
```

## 常见错误

| 问题 | 根因 | 处理方式 |
|---|---|---|
| 精英概率永远不生效 | 把 `Random.Range(0, 1)` 当成 0~1 概率 | 用 `Random.value` 做浮点概率掷骰 |
| `EnemySpawner` 变成导演 | 在生成器里写第几分钟刷什么 | 时间和阶段归 `WaveDirector`，生成器只消费当前参数 |
| 普通怪高概率掉好装备 | 测试掉落没有回调 | 普通怪经验为主，精英和宝箱承担高价值入口 |
| 只调宝箱频率不调品质 | 后期仍按固定低品质权重抽 | `WaveStage` 同时配置击杀间隔、场上上限和品质权重 |
| 权重随机出现 null | 总权重和命中返回使用两套取权重规则 | `GetWeightForTier()` 成为单一规则源 |
| GLB 受击事件正常但不闪 | 旧方案依赖材质颜色属性 | 改为临时替换 `flashMaterial` |
| 池化敌人带着闪白回池 | 受击协程中断时没有恢复材质 | `OnDisable()` 停协程并 `RestoreMaterials()` |
| 用 0 偷偷禁用宝箱 | `ApplyWaveSettings()` 把击杀间隔和上限钳到至少 1 | 后续若要禁用宝箱，应显式加 `chestEnabled` |

## 如何验证

### 敌人生成

- 普通池和精英池都在 `01-Run.unity` 中接入 `EnemySpawner`。
- `eliteSpawnChance = 0` 时只出普通敌人。
- 提高 `eliteSpawnChance` 后，精英出现比例随阶段上升。
- `normalEnemyPool` 或 `eliteEnemyPool` 缺失时不应空引用崩溃；缺精英池时回退普通池。
- `TargetRegistry.Count < maxAlive` 的上限仍限制普通和精英总场上数量。

### 掉落经济

- 普通敌人掉落以经验为主，装备概率低于测试期。
- 精英敌人使用独立掉落表，并能稳定承担优秀 / 稀有装备入口。
- 宝箱在早期更频繁，后期出现间隔变长但品质权重提高。
- 终局阶段能看到更高稀有度宝箱概率提高，但仍需 Play Mode 统计样本验证真实分布。

### 宝箱权重

- 每个阶段的 `chestTierWeights` 名称能匹配 `ChestTier.chestName`。
- 漏填某个宝箱品质时能回退 `ChestTier.weight` 默认值。
- 负数权重被归零，不参与总权重和命中。
- 总权重循环和命中循环都调用 `GetWeightForTier()`。
- 如果后续要阶段性禁用宝箱，不用 `0` 偷偷表达，而是新增显式开关。

### 闪白与池化

- 受击时 `Health.OnDamaged` 能触发 `DamageFlashView.HandleDamaged()`。
- 普通敌人和精英敌人受击时都能看到闪白。
- 连续受击会停止旧协程并重新闪白。
- 敌人闪白期间死亡或回池后，再取出不会保留白色材质。
- 多材质槽模型能在闪白结束后恢复原始 `sharedMaterials`。

### 工程边界

- `WaveDirector` 不直接生成敌人或宝箱，只下发参数。
- `EnemySpawner` 不判断时间阶段，只读取当前刷怪参数和精英概率。
- `ChestSpawner` 不判断第几分钟，只按当前击杀间隔、上限和权重抽宝箱。
- 本环境静态扫描项目脚本未发现 `UnityEditor`、`ShadowCascadeGUI`、`using static BS.GamePlay.Waves.WaveDirector` 或 `Random.Range(0, 1)`。
- 本环境未运行 Unity Editor / Play Mode / Profiler / Player Build；真实生成比例、宝箱概率、终局压力和材质表现仍需项目内验证。

## 当前证据分层

| 结论 | 证据等级 | 说明 |
|---|---|---|
| 第 23 课实现了普通/精英分池、宝箱品质曲线、终局压力强化和 GLB 闪白修复 | B | 来自用户放入 Inbox 的课程记录 |
| `EnemySpawner` 已包含 `normalEnemyPool`、`eliteEnemyPool`、`eliteSpawnChance` 和 `PickEnemyPool()`，并使用 `Random.value` | C | 本环境只读查看外部 Unity 工程脚本 |
| `WaveDirector.WaveStage` 已包含精英概率、宝箱击杀间隔、宝箱上限和 `chestTierWeights`，阶段切换时下发给 `EnemySpawner` 与 `ChestSpawner` | C | 本环境只读查看 `WaveDirector.cs` |
| `ChestSpawner` 已包含 `ChestTierWeight`、`currentTierWeights`、`ApplyWaveSettings()` 和 `GetWeightForTier()`，且两轮权重循环都调用同一函数 | C | 本环境只读查看 `ChestSpawner.cs` |
| `DamageFlashView` 已使用 `flashMaterial` 替换 `sharedMaterials`，并在 `OnDisable()` 停协程和恢复材质 | C | 本环境只读查看 `DamageFlashView.cs` |
| `01-Run.unity` 中可见普通/精英池引用、5 个阶段的精英率、宝箱击杀间隔、宝箱上限和宝箱品质权重 | C | 本环境只读检查场景 YAML |
| `NormalEnemy.prefab` 与 `EliteEnemy.prefab` 存在；静态抽样可见精英缩放更大，并挂不同敌人掉落表 | C | 本环境只读检查 Prefab 与 `.meta` |
| 普通敌人与精英敌人在 Unity Play Mode 中按目标比例生成，宝箱品质概率符合曲线 | D | 未运行 Unity，未采样统计 |
| GLB 模型闪白在 Editor 和 Player Build 中已经视觉确认 | D | 未运行 Unity 或 Player Build |
| `EditorBuildSettings.asset` 的场景路径已经修正为当前检查的 `01-Run.unity` | D | 静态检查仍看到 Build Settings 指向 `Assets/BackpackSurvivor/Scenes/Run/Run1.unity` |

## 相关内容

- 前置：[内容面铺开](content-expansion-fire-rate-boost.md)
- 前置：[波次导演与 15 分钟节奏](wave-director-and-run-pacing.md)
- 前置：[容器搜刮与宝箱系统](container-looting-and-chests.md)
- 前置：[战斗反馈快包](combat-feedback-pack.md)
- 前置：[掉落分层与交互拾取](loot-layering-and-interaction.md)
- 后续：[金币掉落与局内经济 HUD](gold-drops-and-economy-hud.md)
- Unity：[Unity 生命周期](../../unity/lifecycle.md)
- 性能：[对象池](../../performance/memory/object-pool.md)
- 检查清单：[Unity 项目能力](../../checklists/unity-project.md)

> 📎 标签：`Unity` `波次系统` `精英怪` `宝箱系统` `权重随机` `对象池` `材质` `项目实践`
