# 经验成长与三选一

> 项目：[Backpack Survivor](index.md)
>
> 状态：用户课程记录描述已实现 `LevelProgress`、三选一奖励、升级暂停、`PlayerRunStats` 和倍率消费；本环境完成静态审阅、项目文件只读复核与文档验证，未运行 Unity Editor / Play Mode
>
> 日期：2026-07-30
>
> 阶段：V0.2 掉落与背包构筑 · 第 17 课

## 学习目标

- 把第 16 课的“XP 显示字段”推进成可复用的等级成长规则。
- 用 `LevelProgress` 独立维护等级、当前经验、总经验和下一级阈值。
- 用 `LevelUpOptionId`、`LevelUpOption` 和 `LevelUpOptionGenerator` 把奖励数据从 UI 中拆出来。
- 用 `GameState.LevelUpSelecting` 区分升级选择和普通暂停，避免两条状态链互相抢 `Time.timeScale`。
- 让 `LevelUpChoiceView` 只展示选项并回传选择，不直接修改战斗数值。
- 用 `PlayerRunStats` 作为本局升级效果的统一落点，让玩家移动、武器伤害和射速只消费当前倍率。

## 交付范围

| 模块 | 当前职责 |
|---|---|
| `LevelProgress` | 普通 C# 等级状态：记录等级、当前 XP、总 XP、下一级阈值，并返回本次连升次数 |
| `LevelUpOptionId` | 用枚举表达奖励语义，避免用裸 `int` 表达“伤害 / 射速 / 移速” |
| `LevelUpOption` | 奖励数据本体：`Id / Title / Description / Value` |
| `LevelUpOptionGenerator` | 从奖励池中随机抽取 3 个不重复选项 |
| `GameState.LevelUpSelecting` | 本局状态机中的升级选择态，和 `Paused` 分开 |
| `LevelUpChoiceView` | 显示三项按钮文案，玩家点击后把对应 `LevelUpOption` 交回 `GameSession` |
| `PlayerRunStats` | 本局运行时倍率：`DamageMultiplier`、`FireRateMultiplier`、`MoveSpeedMultiplier` |
| `PlayerController` / `WeaponBase` / `AutoWeapon` / `ActiveWeapon` | 只读取倍率并参与最终数值计算，不认识升级 UI |

第 17 课补上了幸存者类游戏最核心的一段循环：

```text
打怪掉经验
  -> 吃经验
  -> 达到阈值升级
  -> 暂停战斗并弹出三选一
  -> 选择奖励
  -> 本局倍率改变
  -> 回到战斗继续验证效果
```

## LevelProgress

`LevelProgress` 是普通 C# 类，不继承 `MonoBehaviour`。它只维护经验事实，不负责 UI、暂停或奖励应用：

```csharp
public int AddXp(int amount)
{
    if (amount <= 0) return 0;

    int levelUpCount = 0;
    currentXp += amount;
    totalXp += amount;

    while (currentXp >= XpToNextLevel)
    {
        currentXp -= XpToNextLevel;
        levelUpCount++;
        level++;
    }

    return levelUpCount;
}
```

这里返回 `levelUpCount` 很重要：一次拾取可能跨过多个阈值。经验系统先准确回答“升了几级”，后续流程再决定要弹几次奖励选择。

当前阈值公式是：

```text
XpToNextLevel = baseXpToNextLevel + (level - 1) * xpGrowthPerLevel
```

它适合 Demo 阶段，因为数值可读、可预测，后续如果要做曲线、配置表或难度缩放，可以只替换 `LevelProgress` 的阈值来源，不让 UI 和战斗消费侧感知。

## 奖励数据

`LevelUpOptionId` 用枚举表达奖励类型：

```csharp
public enum LevelUpOptionId
{
    DamageUp,
    FireRateUp,
    MoveSpeedUp,
}
```

`LevelUpOption` 则承载展示与生效都需要的最小信息：

```csharp
public class LevelUpOption
{
    public LevelUpOptionId Id => id;
    public string Title => title;
    public string Description => description;
    public float Value => value;
}
```

这一层拆分避免 UI 自己拼奖励，也避免 `GameSession` 直接写一堆按钮文案。`Id` 用来结算，`Title / Description` 用来展示，`Value` 是当前阶段最小可用的数值参数。

## 三选一生成器

`LevelUpOptionGenerator` 当前内置 3 个基础奖励：

| 奖励 | 文案 | 当前值 |
|---|---|---|
| `DamageUp` | 火力强化 | 伤害 `+20%` |
| `MoveSpeedUp` | 轻装移动 | 移速 `+10%` |
| `FireRateUp` | 快速射击 | 射速 `+15%` |

生成逻辑先复制候选池，再随机抽取并移除，保证同一轮选择内不重复：

```csharp
while (result.Count < count && candidates.Count > 0)
{
    int index = UnityEngine.Random.Range(0, candidates.Count);
    LevelUpOption option = candidates[index];
    result.Add(option);
    candidates.Remove(option);
}
```

`Random.Range(0, candidates.Count)` 的整数重载是前闭后开。这里不能写成 `candidates.Count - 1`，否则最后一个候选永远抽不到。

## GameSession

第 16 课中，`GameSession` 只累计和广播 XP。第 17 课把 XP 交给 `LevelProgress`：

```csharp
private void HandleXpCollected(LootEntry entry)
{
    if (entry == null) return;
    if (state != GameState.Running) return;

    int upLevelCount = levelProgress.AddXp(entry.amount);
    BroadcastXpChanged();

    for (int i = 0; i < upLevelCount; i++)
    {
        int reachedLevel = levelProgress.Level - upLevelCount + i + 1;
        OnLevelUp?.Invoke(reachedLevel);
    }

    if (upLevelCount > 0)
    {
        RequestLevelUpChoice(levelProgress.Level);
    }
}
```

升级时进入独立状态：

```csharp
private void RequestLevelUpChoice(int level)
{
    if (state != GameState.Running) return;

    Time.timeScale = 0f;
    SetState(GameState.LevelUpSelecting);

    List<LevelUpOption> options = levelUpOptionGenerator.Generate(level, 3);
    OnLevelUpChoiceRequested?.Invoke(options);
}
```

`LevelUpSelecting` 和 `Paused` 分开后，普通暂停键只在 `Running <-> Paused` 间切换，不能把升级选择面板当成普通暂停恢复掉。升级选择完成后再回到 `Running`：

```csharp
public void ChooseLevelUpOption(LevelUpOption option)
{
    if (state != GameState.LevelUpSelecting) return;
    if (option == null) return;
    if (playerRunStats == null) return;

    playerRunStats.Apply(option);
    CompleteLevelUpChoice();
}
```

## LevelUpChoiceView

`LevelUpChoiceView` 是展示层，只订阅请求、刷新按钮、把玩家选择回传：

```csharp
private void HandleLevelUpChoiceRequested(List<LevelUpOption> options)
{
    currentOptions = options;
    choiceOneTitle.text = options[0].Title;
    choiceTwoTitle.text = options[1].Title;
    choiceThreeTitle.text = options[2].Title;
    choiceOneDescription.text = options[0].Description;
    choiceTwoDescription.text = options[1].Description;
    choiceThreeDescription.text = options[2].Description;
    Open();
}
```

按钮回调不直接改伤害、移速或射速：

```text
按钮点击
  -> SelectChoiceOne/Two/Three()
  -> Close()
  -> GameSession.ChooseLevelUpOption(option)
  -> PlayerRunStats.Apply(option)
```

这让 UI 保持“显示 + 回传”的职责，不成为隐藏的第二个规则主人。

## PlayerRunStats

`PlayerRunStats` 是本局升级效果的统一落点：

```csharp
public void Apply(LevelUpOption option)
{
    switch (option.Id)
    {
        case LevelUpOptionId.DamageUp:
            damageMultiplier += option.Value;
            break;

        case LevelUpOptionId.FireRateUp:
            fireRateMultiplier += option.Value;
            break;

        case LevelUpOptionId.MoveSpeedUp:
            moveSpeedMultiplier += option.Value;
            break;
    }
}
```

`GameSession.StartRun()` 会把倍率重置回默认值：

```text
StartRun()
  -> playerRunStats.ResetToDefault()
  -> timer.Reset()
  -> levelProgress.Reset()
  -> State = Running
  -> 广播 XP / 时间初始快照
```

这样“上一局拿过的强化”不会残留到下一局。

## 倍率消费侧

玩家和武器都只读 `PlayerRunStats`：

```csharp
float finalMoveSpeed = moveSpeed * stats.MoveSpeedMultiplier;
float finalDamage = damage * stats.DamageMultiplier;
float finalAttackInterval = attackInterval / stats.FireRateMultiplier;
```

这个边界很干净：

```text
升级系统：决定本局倍率怎么变
消费侧：用当前倍率算最终表现
```

`PlayerController` 不需要知道三选一 UI，`WeaponBase` 不需要知道奖励池，`AutoWeapon` 和 `ActiveWeapon` 也不需要认识 `LevelUpOptionId`。后续加暴击、拾取范围、子弹速度或最大生命时，先决定它是否属于 `PlayerRunStats`，再让对应消费侧读取。

## 完整链路

### 经验进入升级选择

```text
XpOrb.Collect()
  -> XpOrb.OnCollected(entry)
  -> GameSession.HandleXpCollected(entry)
  -> LevelProgress.AddXp(entry.amount)
  -> BroadcastXpChanged()
  -> upLevelCount > 0
  -> RequestLevelUpChoice(levelProgress.Level)
  -> Time.timeScale = 0
  -> State = LevelUpSelecting
  -> LevelUpOptionGenerator.Generate(level, 3)
  -> OnLevelUpChoiceRequested(options)
  -> LevelUpChoiceView.Open()
```

### 选择变成真实战斗数值

```text
玩家点击某个 Button
  -> LevelUpChoiceView 取出对应 LevelUpOption
  -> GameSession.ChooseLevelUpOption(option)
  -> PlayerRunStats.Apply(option)
  -> CompleteLevelUpChoice()
  -> Time.timeScale = 1
  -> State = Running
  -> PlayerController / WeaponBase / AutoWeapon / ActiveWeapon 读取新倍率
```

## 常见错误

| 问题 | 根因 | 处理方式 |
|---|---|---|
| UI 和奖励规则绑死 | 按钮里直接随机或直接改数值 | 让 `LevelUpOptionGenerator` 出卡，`GameSession` 接选择，`PlayerRunStats` 落数值 |
| 升级面板被暂停键关闭 | 升级和普通暂停共用 `Paused` | 使用 `LevelUpSelecting` 表达“正在选奖励” |
| 选完后战斗永远停住 | 只打开面板，没有统一恢复 `Time.timeScale` | `CompleteLevelUpChoice()` 负责恢复到 `1f` 并切回 `Running` |
| 奖励池不足 3 个导致 UI 越界 | 生成器可能返回少于 3 项，但 View 固定访问 `options[0..2]` | 当前池子正好 3 项；后续扩展时要给 View 加数量守卫或动态按钮 |
| 一次连升多级只给一次选择 | `LevelProgress` 支持连升计数，但选择流程只请求一次三选一 | 后续加入待选择队列，每升一级消耗一次选择 |
| 重开后保留上一局强化 | 没有重置 `PlayerRunStats` | `StartRun()` 调用 `ResetToDefault()` |
| 缺少 `PlayerRunStats` 时报空引用 | `StartRun()` 直接调用 `playerRunStats.ResetToDefault()` | Inspector 配好引用或确保场景中存在组件；后续可补空引用防御与日志 |
| 射速倍率变成乘冷却 | 把 `attackInterval` 乘以倍率 | 当前语义是射速提高，所以冷却间隔除以 `FireRateMultiplier` |

## 如何验证

### 经验与等级

- 开局后等级为 `1`，当前经验为 `0`，总经验为 `0`，下一级阈值为基础值。
- 拾取正数经验后，总经验和当前经验同步刷新到 HUD。
- 当前经验达到阈值后等级上升，当前经验扣除阈值并保留溢出。
- 一次获得大量经验时，`LevelProgress.AddXp()` 能返回正确连升次数。
- 非 `Running` 状态下拾取经验不会推动升级流程。

### 三选一流程

- 升级时进入 `LevelUpSelecting`，`Time.timeScale = 0f`，战斗暂停。
- 升级面板显示 3 个不重复选项，并且标题、描述和值语义一致。
- 点击任意选项后面板关闭，`PlayerRunStats` 对应倍率改变。
- 选完后 `Time.timeScale = 1f`，状态回到 `Running`。
- `Paused` 状态和 `LevelUpSelecting` 状态互不误切。

### 倍率消费

- `DamageUp` 后新发射投射物伤害提高。
- `FireRateUp` 后 `AutoWeapon` 和 `ActiveWeapon` 的最终开火间隔缩短。
- `MoveSpeedUp` 后玩家移动速度提高，且仍受 `MapBounds` 限制。
- 重开本局后 `DamageMultiplier`、`FireRateMultiplier`、`MoveSpeedMultiplier` 回到 `1f`。

### 工程边界

- `LevelProgress` 不依赖 UnityEngine，可脱离场景写最小测试。
- `GameSession` 对 `Health.OnDeath`、`XpOrb.OnCollected`、`InputReader.OnPause` 的订阅和退订仍保持镜像。
- `LevelUpChoiceView` 对 `OnLevelUpChoiceRequested` 和三个按钮 `onClick` 的订阅、退订成对。
- `01-Run.unity` 中存在 `LevelUpChoiceView` 与 `PlayerRunStats` 组件引用；`GameSession.playerRunStats` 当前序列化引用为空，但脚本中有 `FindAnyObjectByType<PlayerRunStats>()` 兜底，仍需 Play Mode 复核是否稳定命中。
- 本环境只做项目文件只读复核，没有运行 Unity Editor / Play Mode；仍需在 Unity 中复核 Canvas、Button、TMP、Input Actions、Prefab、`.meta` / GUID、真实暂停和倍率表现。

## 当前证据分层

| 结论 | 证据等级 | 说明 |
|---|---|---|
| 第 17 课实现了经验成长、三选一、升级暂停和运行时倍率入口 | B | 来自用户放入 Inbox 的课程记录 |
| 项目工作区存在 `LevelProgress.cs`、`LevelUpOption*.cs`、`LevelUpOptionGenerator.cs`、`LevelUpChoiceView.cs`、`PlayerRunStats.cs` 及对应 `.meta` | C | 本环境对 `E:\YouXiKaiFa\Backpack Survivor` 做只读文件扫描 |
| `GameSession` 代码中可见 `LevelProgress.AddXp()`、`GameState.LevelUpSelecting`、`OnLevelUpChoiceRequested` 和 `PlayerRunStats.Apply()` 链路 | C | 本环境只读查看脚本，未编译或运行 Unity |
| `01-Run.unity` 中可见 `LevelUpChoiceView` 和 `PlayerRunStats` 脚本 GUID 引用 | C | 本环境只读检查场景 YAML 和 `.meta` GUID，未打开 Unity Editor |
| `PlayerController`、`WeaponBase`、`AutoWeapon`、`ActiveWeapon` 消费 `PlayerRunStats` 倍率 | C | 本环境只读查看脚本，未运行场景 |
| 第 17 课已由当前环境在 Unity Editor / Play Mode 中运行通过 | D | 未启动 Unity，未运行 Play Mode，未验证场景接线或实际按钮点击 |
| 多级连升已经逐级弹出多次三选一 | D | 当前静态代码只看到一次 `RequestLevelUpChoice(levelProgress.Level)`，待加入选择队列后再确认 |

## 相关内容

- 前置：[单局框架与基础 HUD](run-session-and-basic-hud.md)
- 前置：[拾取与磁吸](pickup-and-magnet.md)
- 前置：[主动武器与 WeaponBase 提炼](active-weapons-and-weapon-base.md)
- 后续：[波次导演与 15 分钟节奏](wave-director-and-run-pacing.md)
- UGUI：[UGUI 总览](../../unity/ugui/index.md)
- C#：[委托与事件](../../csharp/oop/delegates-and-events.md)
- C#：[C# 工程实践路线](../../csharp/engineering/index.md)

> 📎 标签：`Unity` `经验成长` `三选一` `GameSession` `状态机` `UGUI` `运行时数值` `项目实践`
