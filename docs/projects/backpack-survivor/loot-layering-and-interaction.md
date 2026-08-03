# 掉落分层与交互拾取

> 项目：[Backpack Survivor](index.md)
>
> 状态：用户课程记录描述已实现两级掉落表、经验球自动吸取、装备 E 键交互拾取和提示 UI；本环境完成静态审阅与文档验证，未重新运行 Unity
>
> 日期：2026-07-26
>
> 阶段：V0.2 掉落与背包构筑 · 第 11 课

## 学习目标

- 把第 7 课的单层掉落表演进为“品类概率门 + 子表权重抽取”的两级结构。
- 修正保底机制边界：只有装备品类进入保底计数，经验球不稀释装备保底。
- 分离自动拾取和手动交互拾取：货币类磁吸，装备类落地后按 E 拾取。
- 用 `ICollectable` 与 `IInteractable` 表达不同能力合同，避免组件互相认识具体实现。
- 用局部物理查询探测可交互物，并用事件驱动提示 UI 显隐。
- 再次强化池化对象复用时运行期状态必须归零的流程。

## 交付范围

| 模块 | 当前职责 |
|---|---|
| `LootTableData.DropChannel` | 品类频道：`probability` 决定是否通过，`subTable` 决定通过后抽什么 |
| `LootRoller.RollBundle` | 遍历频道，一次死亡可并行产出经验、装备等多个条目 |
| `DropCategory` | 区分 `Xp`、`Gold`、`Equipment`，让生成和保底按品类分流 |
| `XpOrb` | 经验球，`IPoolable + ICollectable`，走磁吸自动拾取 |
| `DropItem` | 装备掉落物，`IPoolable + ICollectable + IInteractable`，走 E 键交互拾取 |
| `InteractDetector` | 玩家周围局部探测，节流调用 `OverlapSphereNonAlloc` 并选最近目标 |
| `InputReader.OnInteract` | E 键瞬时交互事件，与攻击的持续状态位区分 |
| `InteractPromptUI` | Presentation 层提示框，订阅目标变化事件，不用 `Update` 轮询显隐 |
| `InventorySystem` | 双频道收货口：装备入包，经验进入临时经验账本 |

第 11 课的主线是“搜打撤式掉落体验”：经验球自动吸附，装备留在地上等待玩家主动交互，后续宝箱、隐藏宝箱和撤离终端也可以复用同一套 `IInteractable`。

## 掉落表分层

第 7 课的单表权重随机只能回答“这次掉什么”。第 11 课需要回答更接近 GDD 的问题：

```text
经验球：必掉，但面额走子表
装备：独立概率掉落，掉了再按装备子表权重抽
金币：第 24 课补成 GoldOrb、局内金币统计和 HUD 显示
```

因此新增频道结构：

```csharp
[Serializable]
public class DropChannel
{
    [Range(0, 1)] public float probability = 1f;
    public LootTableData subTable;
}

public DropChannel[] channels;

[Serializable]
public class LootEntry
{
    public DropCategory category = DropCategory.Equipment;
    public string id;
    public GameObject dropPrefab;
    public Rarity rarity;
    public int weight;
    public int amount = 1;
    public int width = 1;
    public int height = 1;
}

public LootEntry[] entries;

public enum DropCategory
{
    Xp,
    Gold,
    Equipment,
}
```

一张表现在有两种形态：

- 束表：`channels` 非空，负责“哪些品类过门”。
- 叶表：`entries` 非空，负责“过门后具体抽哪一条”。

当前课程实现中，频道的 `subTable` 主要指向叶表。原始思考题已经指出，如果未来 Boss 表套精英表再套基础表，需要让 `RollBundle` 能识别子表也是束表，再递归展开。

## RollBundle 与保底边界

束表遍历每个频道，先掷概率门：

```csharp
public List<LootEntry> RollBundle(LootTableData bundle)
{
    List<LootEntry> entries = new List<LootEntry>();

    if (bundle == null || bundle.channels == null || bundle.channels.Length == 0)
    {
        return entries;
    }

    foreach (var channel in bundle.channels)
    {
        if (UnityEngine.Random.value < channel.probability)
        {
            LootEntry entry = Roll(channel.subTable);
            if (entry != null)
            {
                entries.Add(entry);
            }
        }
    }

    return entries;
}
```

保底只属于装备抽取，不属于“任意掉落”。修正后的计数边界是：

```text
抽到 Rare 及以上装备 -> pityCount = 0
抽到 Common / Uncommon 装备 -> pityCount++
抽到经验 / 金币 / 空结果 -> 不碰 pityCount
```

这样经验球必掉不会稀释装备保底，也不会把保底计数错误清零。

## 按品类选池

`LootManager` 从“拿一个 `dropPool` 生成所有掉落物”演进为按品类分流：

```csharp
public void TrySpawnDrop(Vector3 position, LootTableData bundle)
{
    List<LootEntry> list = lootRoller.RollBundle(bundle);

    foreach (LootEntry entry in list)
    {
        if (entry == null) continue;

        if (entry.category == DropCategory.Equipment)
        {
            DropItem dropItem = dropPool.Get(position).GetComponent<DropItem>();
            dropItem.Initialize(entry);
        }
        else if (entry.category == DropCategory.Xp)
        {
            Vector2 randomOffset = Random.insideUnitCircle * offset;
            Vector3 pos = position + new Vector3(randomOffset.x, 0, randomOffset.y);
            XpOrb xpOrb = currencyPool.Get(pos).GetComponent<XpOrb>();
            xpOrb.Initialize(entry);
        }
        else if (entry.category == DropCategory.Gold)
        {
            // 第 24 课已补为 GoldOrb 对象池生成、散落飞行和局内金币记账
        }
    }
}
```

这里把“装备池”和“货币池”分开。经验球可以带随机偏移并挂 `PickUpMagnet`，装备则落地旋转并等待交互拾取。

## 两份能力合同

本课新增两个接口：

```csharp
namespace BS.GamePlay.Loot
{
    public interface ICollectable
    {
        void Collect();
    }
}

namespace BS.GamePlay.Interaction
{
    public interface IInteractable
    {
        string GetPrompt();
        void Interact();
    }
}
```

`ICollectable` 表示“能被收货口收走”，`IInteractable` 表示“能被玩家主动交互”。同一个对象可以签多份合同：

```text
XpOrb    = IPoolable + ICollectable
DropItem = IPoolable + ICollectable + IInteractable
```

`PickUpMagnet` 不需要认识 `XpOrb`，只需要调用 `ICollectable.Collect()`。`InteractDetector` 不需要认识 `DropItem`，只需要调用 `IInteractable.Interact()`。

## 自动拾取与手动拾取

经验球走自动磁吸：

```text
XpOrb 落地
  -> PickUpMagnet Idle
  -> 玩家进入吸附范围
  -> Attracted
  -> 进入收取范围
  -> XpOrb.Collect()
  -> XpOrb.OnCollected(entry)
  -> InventorySystem.HandleCurrency
  -> Recycle()
```

装备走手动交互：

```csharp
public class DropItem : MonoBehaviour, IPoolable, ICollectable, IInteractable
{
    public string GetPrompt() => $"按 E 拾取 {lootEntry.id}";

    public void Interact()
    {
        Collect();
    }

    public void Collect()
    {
        OnCollected?.Invoke(lootEntry);
        Recycle();
    }
}
```

关键点是 `Interact()` 不自己广播和回池，而是复用 `Collect()`。这样磁吸、按钮、脚本触发等不同入口都汇合到同一个收货口，后续如果收货口改成“请求-确认”协议，只需要改一个出口。

## 局部交互探测

玩家身边的可交互物用局部物理查询，而不是全局注册表：

```csharp
int count = Physics.OverlapSphereNonAlloc(
    playerH.Position,
    detectionRadius,
    buffer,
    interactableLayerMask);

IInteractable nearest = null;
float minSqDist = Mathf.Infinity;

for (int i = 0; i < count; i++)
{
    Collider col = buffer[i];
    if (col == null) continue;

    IInteractable interactable = col.GetComponent<IInteractable>();
    if (interactable == null) continue;

    float sqrDist = (col.transform.position - playerH.Position).sqrMagnitude;
    if (sqrDist < minSqDist)
    {
        minSqDist = sqrDist;
        nearest = interactable;
    }
}
```

只遍历 `[0, count)` 很重要。`NonAlloc` 查询的缓冲区后半段可能保留上一次结果，遍历整个数组会读到过期目标。

目标变化才广播：

```csharp
if (nearest != previousTarget)
{
    previousTarget = nearest;
    CurrentTarget = nearest;
    OnTargetChanged?.Invoke(nearest);
}
```

这让提示 UI 不需要每帧轮询。`InteractPromptUI` 收到新目标时，先写文本再显示面板，避免闪旧内容。

## 注册表 vs 物理查询

项目里已经有两个“找最近”的场景，但问题形状不同：

| 场景 | 问题形状 | 当前方案 |
|---|---|---|
| 自动武器索敌 | 全图活着的目标，频繁被 AI 查询 | `TargetRegistry` |
| 玩家交互拾取 | 玩家周围 2 米有什么 | `OverlapSphereNonAlloc` |

全图成员管理适合注册表；局部空间询问适合物理查询。反过来会带来错配：玩家交互用注册表需要遍历全图所有物体，敌人索敌用物理查询又会让每个敌人频繁扫空间。

## 池化状态归零

第 11 课再次暴露对象池状态未重置问题：

| 问题 | 表现 | 根因 | 修复 |
|---|---|---|---|
| 敌人死了不消失 | 尸体继续追人且不吃伤害 | `DropItem.OnGetFromPool()` 里残留 `pum.StateReset()`，但装备已摘掉 `PickUpMagnet`，空引用中断死亡流程 | 清掉装备掉落物上的 `pum` 依赖 |
| 经验球范围外秒吸 | 部分经验球一出生就飞向玩家 | `XpOrb.OnGetFromPool()` 未重置磁吸状态机和速度 | 调用 `pum.StateReset()` |
| 经验球出生即死 | 超时球复用后首帧回池 | `survivalTimer` 未清零 | `survivalTimer = 0f` |

升级后的机械流程：

```text
池化类新增运行期字段
  -> 同一分钟检查 OnGetFromPool
  -> 明确旧值复活是否会出事
  -> 写入归零逻辑或解释为什么不用归零
```

这条规则已经从“经验教训”升级为项目 review 清单。

## 已知挂账：拾取失败吞物品

> 后续演进：第 13 课已把 `IInteractable.Interact()` 改为返回 `bool`，通过请求-确认和兜底吐回修复吞物品风险，详见[背包交互补丁](inventory-interaction-patches.md)。本节保留第 11 课当时暴露的设计债。

原始记录明确暴露了一个重要设计债：

```text
玩家按 E
  -> DropItem.Interact()
  -> Collect()
  -> DropItem.OnCollected(entry)
  -> Recycle()
  -> InventorySystem.HandleCollected()
  -> 背包放不下，只 Log
  -> 物品已经被回收，等于被吞
```

这说明当前收货口是“无条件收”。正式规则应该升级为“请求-确认”：

```text
玩家请求拾取
  -> 先问背包能否容纳
  -> 能放：Collect + 回池 + 入包
  -> 不能放：留在地上 + 给反馈
```

R 键旋转可以缓解大件装备放不下的问题，但不能替代收货口协议修正。

## 常见错误

| 问题 | 根因 | 处理方式 |
|---|---|---|
| 经验球影响装备保底 | 必掉经验也进入 pity 计数 | 只有 `Equipment` 参与保底累计和清零 |
| 物品生成后路线错误 | 用条目名字或 Prefab 判断类型 | 用 `DropCategory` 明确按品类分流 |
| 装备仍被磁吸 | 组件和 Layer 没有按拾取方式分化 | 货币挂磁吸，装备挂交互 Trigger 和 Interactable Layer |
| 对空气按 E 报错 | `CurrentTarget` 为空仍调用 `Interact()` | 交互入口第一行判空 |
| `NonAlloc` 读到旧目标 | 遍历了整个 buffer | 只遍历 `[0, count)` |
| 提示框闪旧文本 | 先显示面板再改文字 | 先设置 `promptText.text`，再 `SetActive(true)` |
| Input Actions 改动丢失 | 编辑器内修改未 Save Asset | 怀疑资产异常先看 `git diff`，确认是否写盘 |

## 如何验证

### 掉落与概率验证

- 束表中经验频道设为 `1.0` 时，每次死亡都能生成经验球。
- 装备频道按独立概率生成，不与经验球互斥。
- 装备子表权重为 0 或空表时安全失败，不空引用。
- 保底阈值调低后，只由装备未中稀有累计；经验球不改变 pity。
- 普通怪和精英怪挂不同束表，掉落结果符合配置差异。

### 拾取与交互验证

- 经验球只走磁吸自动拾取，装备只走 E 键交互拾取。
- `InteractDetector` 只在玩家附近可交互物变化时更新提示。
- 多个可交互物同时在范围内时，提示最近目标。
- 目标回池、走出范围或被拾取后，提示框隐藏。
- 对空气按 E 不报错。
- 背包满或形状放不下时，当前版本会吞物品；后续请求-确认修复前必须作为已知问题保留。

### 池化与性能验证

- 经验球回池再取出，磁吸状态、速度和生存计时都归零。
- 装备回池再取出，生存计时、颜色、`lootEntry` 和交互提示都使用本轮数据。
- `OverlapSphereNonAlloc` 的 `buffer` 满载时有日志或降级策略。
- Profiler 观察探测间隔、物理查询、提示 UI 显隐、经验球批量吸附和 GC Alloc；没有数据前不写性能收益结论。

## 当前证据分层

| 结论 | 证据等级 | 说明 |
|---|---|---|
| 第 11 课实现了两级掉落表、品类分流、经验球自动拾取和装备交互拾取 | B | 来自用户放入 Inbox 的课程记录 |
| 经验球不应进入装备保底计数 | B | 原始记录明确描述了修正原因和实现 |
| `ICollectable` / `IInteractable` 分离能让磁吸、交互和收货口各自依赖接口 | C | 当前模型基于代码结构和职责边界静态审阅 |
| `OverlapSphereNonAlloc` 只遍历 `[0, count)` 是必要边界 | C | 根据 Unity NonAlloc 查询语义和缓冲区复用推断 |
| 第 11 课已由当前环境在 Unity Editor / Play Mode 中运行通过 | D | 本次未收到完整 Unity 工程、场景、Prefab、Input Actions 或 `.meta`，未运行 Unity |
| 探测方案或池化方案已带来可量化性能收益 | D | 缺少 Profiler 对照数据，暂不写成性能结论 |

## 相关内容

- 前置：[掉落系统与保底机制](loot-drop-and-pity.md)
- 前置：[拾取与磁吸](pickup-and-magnet.md)
- 前置：[背包 UI 与拖拽](inventory-ui-and-drag.md)
- 后续：[容器搜刮与宝箱系统](container-looting-and-chests.md)
- 后续：[背包交互补丁](inventory-interaction-patches.md)
- 后续：[金币掉落与局内经济 HUD](gold-drops-and-economy-hud.md)
- Unity：[Unity 生命周期](../../unity/lifecycle.md)
- 性能：[对象池](../../performance/memory/object-pool.md)
- C#：[委托与事件](../../csharp/oop/delegates-and-events.md)

> 📎 标签：`Unity` `掉落系统` `交互系统` `IInteractable` `对象池` `物理查询` `保底机制` `项目实践`
