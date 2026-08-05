# 数值调参台与首轮平衡

> 学习状态：已应用，待复测
>
> 前置知识：[合并升级收益兑现](merge-upgrade-reward-payoff.md)、[波次导演与 15 分钟节奏](wave-director-and-run-pacing.md)、[精英宝箱与终局压力强化](elite-chests-endgame-pressure.md)
>
> 对应项目：[Backpack Survivor](index.md)
>
> 下一步：[第 28 课旋转邻接方向修正](rotation-adjacency-direction-fix.md)
>
> 日期：2026-08-04
>
> 阶段：V0.2 掉落与背包构筑 · 第 27 课

## 学习目标

- 把 FireRateBoost 从“合并升级后容易超模”调回可控区。
- 让伤害数字和真实扣血使用同一份伤害语义，避免 UI overpromise。
- 让敌人血量随波次成长，不只靠刷怪数量制造后期压力。
- 用宝箱距离 HUD 给玩家目标感，但不替玩家做完整导航。
- 把首轮 15 分钟试玩记录沉淀成平衡证据，而不是只保留“感觉变好”。

## 当前理解

第 27 课的“数值调参台”不是先做一套复杂编辑器工具，而是先找 Demo 期最有杠杆的旋钮：

```text
玩家侧：弹夹基础值、等级倍率、攻速上限、伤害取整规则
敌人侧：普通怪血量、精英怪血量、刷怪间隔、场上上限、精英率
奖励侧：宝箱品质、宝箱距离可读性、玩家主动搜刮意愿
验证侧：完整试玩死亡时间、危险时间点、构筑强弱体感
```

当前最重要的平衡原则是：玩家成长、敌人成长和目标引导要一起看。只调玩家会变成无脑割草；只调敌人会变成数值压迫；只加提示又不能证明玩法闭环成立。

## 交付范围

| 模块 | 当前职责 |
|---|---|
| `Item.GetLevelEffectMultiplier()` | 把升级收益从线性 `Level` 改成等级倍率表 |
| `BackpackWeaponActivator.maxBackpackFireRateMultiplier` | 把背包攻速封顶收回到 `2.0x` |
| 掉落表弹夹 `effectValue` | 普通 / 优秀 / 稀有弹夹基准分别为 `10% / 15% / 20%` |
| `WeaponBase.Fire()` | 在伤害源头计算并取整 `finalDamage` |
| `DamageNumberView.Play()` | 显示同一伤害语义的整数文本 |
| `WaveDirector.WaveStage` | 新增普通 / 精英敌人直接最大血量配置 |
| `EnemySpawner.ApplyWaveSettings()` | 接收并保存当前波次血量参数 |
| `Health.SetMaxHpAndReset()` | 池化敌人出池后设置本波最大血量并回满 |
| `LootChest.unopenedChests` | 维护当前仍可打开的宝箱集合 |
| `LootChest.TryGetNearestUnopened()` | 给 HUD 查询最近未开启宝箱 |
| `ChestDistanceView` | 显示最近宝箱距离或“宝箱附近” |

## 最小示例

### FireRateBoost 等级倍率

```csharp
public float EffectValue => baseEffectValue * GetLevelEffectMultiplier();

private float GetLevelEffectMultiplier()
{
    if (Level == 1) return 1f;
    if (Level == 2) return 1.5f;
    if (Level == 3) return 2f;
    return 1f;
}
```

攻速是强体感收益，不适合让 Lv.2 = 2 倍、Lv.3 = 3 倍直接线性放大。当前写法保留合并收益，但避免“看到弹夹就无脑合并”。

### 伤害源头取整

```csharp
float rawDamage = damage * stats.DamageMultiplier;
float finalDamage = Mathf.RoundToInt(rawDamage);

bullet.Initialize(
    projectileSpeed,
    finalDamage,
    targetFaction,
    maxDistance,
    direction,
    0f,
    gameObject);
```

伤害数字是否好看是表现问题；真实伤害是多少是规则问题。取整放在 `WeaponBase` 后，池化子弹、无池兜底子弹、`Health` 和 `DamageNumberView` 都消费同一份规则事实。

### 波次直接血量

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
    public float normalEnemyMaxHp = 1f;
    public float eliteEnemyMaxHp = 1f;
}
```

Demo 平衡阶段直接写血量比写倍率更直观。策划视角更关心“第 4 波普通怪 130 血”，而不是“基础血量乘某个倍率后刚好是多少”。

### 池化敌人出池重置血量

```csharp
public void SetMaxHpAndReset(float newMaxHp)
{
    if (newMaxHp <= 1f) return;
    maxHp = newMaxHp;
    currentHp = maxHp;
    OnHealthChanged?.Invoke(currentHp, maxHp);
}
```

敌人使用对象池后，血量不能只在 Prefab 或 `Awake()` 中初始化。新一轮出池必须按当前波次重置最大血量和当前血量，否则上一轮残血或旧波次血量会污染下一次出生。

### 最近宝箱查询

```csharp
public static bool TryGetNearestUnopened(Vector3 from, out LootChest nearest)
{
    nearest = null;
    float sqrNearestDistance = float.MaxValue;

    foreach (var chest in unopenedChests)
    {
        if (chest == null) continue;
        if (chest.gameObject.activeInHierarchy == false) continue;

        float sqrDistance = (chest.transform.position - from).sqrMagnitude;
        if (sqrDistance < sqrNearestDistance)
        {
            sqrNearestDistance = sqrDistance;
            nearest = chest;
        }
    }

    return nearest != null;
}
```

宝箱数量不大，但距离比较仍使用 `sqrMagnitude`。这里沉淀的是习惯：每帧查询中的排序 / 最近距离问题，先避免无意义开方。

## 项目中的应用

### FireRateBoost 首轮回调

第 26 课让合并升级收益真正进入 `EffectValue`，但线性等级收益会让弹夹快速超模。第 27 课把弹夹基础值和升级倍率同时收回来：

| 弹夹 | 基础 `effectValue` | 等级倍率 |
|---|---:|---|
| 普通弹夹 | `0.10` | Lv.1 = `1.0x` |
| 优秀弹夹 | `0.15` | Lv.2 = `1.5x` |
| 稀有弹夹 | `0.20` | Lv.3 = `2.0x` |

`BackpackWeaponActivator.maxBackpackFireRateMultiplier` 同步降到 `2.0x`。这样弹夹仍然能明显提高射速，但不会让少数高等级弹夹把 15 分钟 Demo 的压力曲线打穿。

### 伤害显示与规则语义统一

第 26 课先发现“显示 25，但 50 血敌人需要 3 枪”的认知问题；第 27 课把修复从显示层推进到规则层：

```text
WeaponBase.damage × PlayerRunStats.DamageMultiplier
  -> WeaponBase 源头 RoundToInt
  -> Projectile.Initialize(finalDamage)
  -> Health.TakeDamage(info.damage)
  -> DamageNumberView.RoundToInt(damage)
```

这条链路的判断标准很简单：如果 UI 显示 25，玩家就应该能相信真实伤害也是 25。表现层可以决定字体、颜色、位置和动画，但不应该单独解释战斗规则。

### 波次血量成长

当前课程记录中的首轮波次血量基准：

| Wave | 普通怪最大血量 | 精英怪最大血量 |
|---:|---:|---:|
| 1 | 40 | 150 |
| 2 | 65 | 150 |
| 3 | 90 | 200 |
| 4 | 130 | 300 |
| 5 | 160 | 400 |

这让敌人成长从“数量 / 密度”扩展到“质量”。如果玩家已经有武器、升级、合并和邻接四条成长来源，而敌人只提高数量，后期很容易变成清屏速度测试；加入血量后，TTK 会随波次拉长，终局压力更容易成立。

### 宝箱距离 HUD

`LootChest` 维护未开启宝箱列表，宝箱出池时加入，开箱或回池时移出。`ChestDistanceView` 每帧查询最近未开启宝箱：

```text
没有宝箱：显示空文本
距离 < hideDistance：显示“宝箱附近”
距离 >= hideDistance：显示“宝箱:{distance:F1}m”
```

当前取舍是显示距离，不显示箭头。距离提示会告诉玩家“附近有目标、值不值得绕过去”，但方向、路线、是否冒险仍由玩家判断。这样比箭头导航更能保留搜刮和幸存者压力之间的取舍。

静态场景 YAML 可见 `ChestDistanceText` 是 `TextMeshProUGUI`，`m_RaycastTarget: 0`，并由 `ChestDistanceView` 引用；但真实拖拽、背包输入和 HUD 层级仍需 Play Mode 复核。

### 首轮 15 分钟试玩

用户记录中有一局完整试玩：在运气不好、没有拿到高强度 AK 的情况下，剩约 3 分钟失败。这个结果对 Demo 很有价值：

```text
能进入终局 -> 前中期没有早崩
剩 3 分钟失败 -> 终局压力不是摆设
构筑强弱可感知 -> 随机掉落和背包整理已经影响局势
玩家愿意继续玩 -> 第一轮玩法闭环开始成立
```

这类证据不是“当前环境亲自运行通过”，而是用户课程记录和试玩记录。知识库记录时必须写清证据归属。

## 常见错误

| 问题 | 根因 | 处理方式 |
|---|---|---|
| 弹夹升级收益过猛 | 攻速收益按 `Level` 线性放大，且封顶过高 | 基础值回调，等级倍率改为 `1.0 / 1.5 / 2.0`，上限收回到 `2.0x` |
| 伤害数字和扣血不一致 | UI 层单独取整，规则层仍用浮点 | 在 `WeaponBase` 源头统一取整，显示层只复述 |
| 后期只靠怪物数量上压 | 玩家有多条成长线，敌人只有密度成长 | `WaveStage` 同时配置普通 / 精英直接血量 |
| 池化敌人带旧血量出生 | 出池时没有按当前波次重置 `maxHp/currentHp` | `Health.SetMaxHpAndReset()` 在取池后立即调用 |
| 宝箱提示过度导航 | 直接箭头替玩家找路 | 先显示距离，让路线选择留给玩家 |
| 纯 HUD 文本挡输入 | TMP Text 保留 `Raycast Target` | 纯展示文本关闭射线，并在 Play Mode 复核拖拽 |
| 一次调太多参数无法归因 | 同时改玩家、敌人、掉落、经验和提示 | 先记录死亡时间、危险点和超模来源，再控制变量调整 |
| 把一次试玩当终局结论 | 样本量不足 | 当前只记录首轮平衡信号，后续继续补 TTK 和重复样本 |

## 如何验证

### 当前已记录证据

| 结论 | 证据等级 | 说明 |
|---|---|---|
| 第 27 课完成 FireRateBoost 回调、伤害语义统一、波次血量、宝箱距离 HUD 和首轮试玩 | B | 来自用户放入 Inbox 的课程记录与用户试玩记录 |
| `Item.EffectValue` 已改为基础值乘等级倍率表 | C | 本环境只读查看外部 Unity 工程 `Item.cs` |
| `BackpackWeaponActivator.maxBackpackFireRateMultiplier` 场景值为 `2.0` | C | 本环境只读查看 `01-Run.unity` YAML |
| 普通 / 优秀 / 稀有弹夹基础值分别为 `0.10 / 0.15 / 0.20` | C | 本环境只读抽样查看掉落表资产 |
| `WeaponBase.Fire()` 中池化和无池路径使用同一 `finalDamage` | C | 本环境只读查看 `WeaponBase.cs` |
| `WaveStage` 与 `EnemySpawner.ApplyWaveSettings()` 已包含普通 / 精英血量参数 | C | 本环境只读查看 `WaveDirector.cs` 与 `EnemySpawner.cs` |
| `LootChest.TryGetNearestUnopened()`、`ChestDistanceView` 和 `ChestDistanceText.m_RaycastTarget: 0` 静态可见 | C | 本环境只读查看脚本、`.meta` 与 `01-Run.unity` YAML |
| 当前环境未运行 Unity Editor / Play Mode、Profiler 或 Player Build | D | 未启动 Unity，未亲自复测真实画面、手感、性能或 Build |

### 待补验证

- 用 Play Mode 复核显示伤害、真实扣血和敌人死亡枪数是否一致。
- 记录不同波次普通怪 / 精英怪的 TTK 样本，确认血量曲线是否过硬或过软。
- 复核 FireRateBoost 多弹夹叠加、Lv.2 / Lv.3 升级收益和 `2.0x` 封顶体感。
- 复核宝箱距离文本在背包拖拽、升级面板、暂停和结算面板中的层级与射线行为。
- 连续多局记录死亡 / 通关时间、宝箱获取数、强构筑来源和第一次危险时间点。
- 使用 Profiler 查看终局波次、伤害数字、宝箱距离查询、邻接刷新和对象池扩容。
- 执行 Player Build，确认字体、HUD、场景重载和退出按钮行为。
- 针对 `LootChest.unopenedChests` 设计场景切换 / 重开清理验证，避免静态列表残留旧场景对象。

## 复盘

- 原来的理解：平衡主要是调几个伤害、攻速和刷怪数字。
- 实践后的结论：真正要调的是完整循环。玩家是否愿意找宝箱、整理背包、承担终局压力，和单个数字同样重要。
- 仍未理解：缺少重复试玩、Profiler 数据、真实 TTK 样本和 Player Build 结果，因此不能把这次参数写成最终平衡。

## 相关内容

- 前置：[合并升级收益兑现](merge-upgrade-reward-payoff.md)
- 前置：[内容面铺开](content-expansion-fire-rate-boost.md)
- 前置：[波次导演与 15 分钟节奏](wave-director-and-run-pacing.md)
- 前置：[精英宝箱与终局压力强化](elite-chests-endgame-pressure.md)
- 前置：[战斗反馈快包](combat-feedback-pack.md)
- 前置：[容器搜刮与宝箱系统](container-looting-and-chests.md)
- 后续：[旋转邻接方向修正](rotation-adjacency-direction-fix.md)
- 后续：[武器稀有度与等级差异](weapon-rarity-and-level-scaling.md)
- C#：[C# 工程实践路线](../../csharp/engineering/index.md)
- 检查清单：[Unity 项目能力](../../checklists/unity-project.md)

> 标签：`Unity` `数值平衡` `FireRateBoost` `波次系统` `伤害数字` `宝箱系统` `试玩验证` `项目实践`
