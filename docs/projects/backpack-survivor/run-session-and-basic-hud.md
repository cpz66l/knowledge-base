# 单局框架与基础 HUD

> 项目：[Backpack Survivor](index.md)
>
> 状态：用户课程记录描述已实现 `GameState`、`RunTimer`、`GameSession`、基础 HUD、暂停/恢复和胜负入口；本环境完成静态审阅、项目文件只读复核与文档验证，未运行 Unity Editor / Play Mode
>
> 日期：2026-07-29
>
> 阶段：V0.2 掉落与背包构筑 · 第 16 课

## 学习目标

- 建立“单局”的状态主人，让时间、胜负、暂停、经验显示不再散落在各个系统里。
- 用 `GameState` 显式表达 `NotStarted / Running / Paused / Victory / Defeat`，避免多个 bool 互相打架。
- 把计时事实放进纯 C# `RunTimer`，把胜负裁决留给 `GameSession`。
- 让基础 HUD 只消费 `GameSession` 的只读快照和事件，不直接改本局数据。
- 用“订阅事件 + 主动拉快照”解决 HUD 初始化时序问题。
- 把暂停输入作为意图传给 `GameSession`，由状态机裁决能否暂停或恢复。

## 交付范围

| 模块 | 当前职责 |
|---|---|
| `GameState` | 单局主状态：`NotStarted`、`Running`、`Paused`、`Victory`、`Defeat` |
| `RunTimer` | 普通 C# 计时器，只维护时长、已过时间、剩余时间、归一化进度和是否到时 |
| `GameSession` | 本局规则主人：推进计时、处理死亡、累计经验、暂停恢复、广播 HUD 快照 |
| `RunHudView` | 显示倒计时、经验、等级和状态文本，只消费 `GameSession` |
| `InputReader.OnPause` | 把 Escape / Pause Action 翻译成暂停意图 |
| `GameInput.inputactions` | 新增 `Pause` 动作，课程记录中绑定 `<Keyboard>/escape` |

本课把前面分散的功能零件收束成“一局游戏”：什么时候开始，什么时候胜利，什么时候失败，暂停算什么状态，HUD 看谁的数据，都由 `GameSession` 统一裁决。

## 状态枚举

`GameState` 用枚举表达本局状态：

```csharp
namespace BS.GamePlay.Run
{
    public enum GameState
    {
        NotStarted,
        Running,
        Paused,
        Victory,
        Defeat
    }
}
```

`NotStarted` 用来区分“场景已加载”和“本局已开始”。`Paused` 不是终局，只是 `Running` 的临时冻结态。用枚举而不是多个 bool，可以避免 `isRunning == true` 同时 `isPaused == true` 这类非法组合。

## RunTimer

`RunTimer` 是普通 C# 类，不继承 `MonoBehaviour`：

```csharp
public class RunTimer
{
    private float duration;
    private float elapsed;

    public float Duration => duration;
    public float Elapsed => elapsed;

    public float Remaining
    {
        get
        {
            float remaining = duration - elapsed;
            return remaining < 0f ? 0f : remaining;
        }
    }

    public float Normalized
    {
        get
        {
            if (duration <= 0f) return 1f;

            float normalized = elapsed / duration;
            return normalized < 0f ? 0f : (normalized > 1f ? 1f : normalized);
        }
    }

    public bool IsFinished => elapsed >= duration;

    public void Tick(float deltaTime)
    {
        if (deltaTime < 0f) return;
        elapsed += deltaTime;
    }

    public void Reset()
    {
        elapsed = 0f;
    }
}
```

计时器只回答时间事实：过了多久、还剩多久、是否到时。它不判断胜利，因为“时间到了”是事实，“时间到了是否胜利”是玩法规则。后续如果出现 Boss 战、撤离点、加时或缩圈机制，不应该污染计时器本身。

## GameSession

`GameSession` 是本局规则主人：

```csharp
public event Action<GameState> OnStateChanged;
public event Action<float, float> OnTimeChanged;
public event Action<int, int> OnXpChanged;

public GameState State => state;
public float Elapsed => timer.Elapsed;
public float Remaining => timer.Remaining;
public float TimeNormalized => timer.Normalized;
public int TotalXp => totalXp;
public int Level => level;
```

对外暴露只读属性和事件，而不是让 HUD、经验球或输入系统直接改本局状态。

`StartRun()` 初始化本局并广播初始快照：

```csharp
public void StartRun()
{
    timer.Reset();
    totalXp = 0;
    level = 1;

    SetState(GameState.Running);
    OnXpChanged?.Invoke(totalXp, level);
    OnTimeChanged?.Invoke(timer.Elapsed, timer.Remaining);
}
```

初始广播很重要。事件驱动 UI 不能只等“变化”，因为 UI 一出现就需要当前时间、经验、等级和状态。

## 时间与胜负

`Update()` 只在 `Running` 状态推进计时：

```csharp
private void Update()
{
    if (state != GameState.Running) return;

    timer.Tick(Time.deltaTime);
    OnTimeChanged?.Invoke(timer.Elapsed, timer.Remaining);

    if (timer.IsFinished)
    {
        SetState(GameState.Victory);
    }
}
```

暂停、胜利、失败都不再推进本局时间。这里不是让 HUD 停止显示，而是从规则层停止本局逻辑推进。

玩家死亡与经验拾取分别通过事件进入 `GameSession`：

```csharp
private void HandlePlayerDeath()
{
    if (state != GameState.Running) return;
    SetState(GameState.Defeat);
}

private void HandleXpCollected(LootEntry entry)
{
    if (entry == null) return;
    if (state != GameState.Running) return;

    totalXp += entry.amount;
    OnXpChanged?.Invoke(totalXp, level);
}
```

经验本课只累计和显示，不做升级。经验阈值、升级暂停、三选一 UI 和奖励应用已在后续[经验成长与三选一](level-progression-and-choice.md)中单独记录。

## 暂停与恢复

`InputReader` 只翻译输入意图：

```csharp
public event Action OnPause;

public void Pause(InputAction.CallbackContext ctx)
{
    if (ctx.performed)
    {
        OnPause?.Invoke();
    }
}
```

真正的状态裁决在 `GameSession`：

```csharp
private void TogglePause()
{
    if (state == GameState.Running)
    {
        PauseRun();
    }
    else if (state == GameState.Paused)
    {
        ResumeRun();
    }
}

private void PauseRun()
{
    if (state != GameState.Running) return;
    Time.timeScale = 0f;
    SetState(GameState.Paused);
}

private void ResumeRun()
{
    if (state != GameState.Paused) return;
    Time.timeScale = 1f;
    SetState(GameState.Running);
}
```

`else if` 是关键。若用两个连续 `if`，一次按键可能先从 `Running` 进 `Paused`，再立刻命中第二个分支恢复成 `Running`，表现为暂停键没有效果。

胜利或失败后再按暂停键不会回到 `Running`。输入层不应该绕过状态机改结算结果。

## 基础 HUD

`RunHudView` 订阅 `GameSession` 事件：

```csharp
private void OnEnable()
{
    if (gameSession == null) return;

    gameSession.OnTimeChanged += HandleTimeChanged;
    gameSession.OnXpChanged += HandleXpChanged;
    gameSession.OnStateChanged += HandleStateChanged;
}

private void OnDisable()
{
    if (gameSession == null) return;

    gameSession.OnTimeChanged -= HandleTimeChanged;
    gameSession.OnXpChanged -= HandleXpChanged;
    gameSession.OnStateChanged -= HandleStateChanged;
}
```

同时在 `Start()` 主动拉取一次当前快照：

```csharp
private void Start()
{
    if (gameSession == null) return;

    HandleTimeChanged(gameSession.Elapsed, gameSession.Remaining);
    HandleXpChanged(gameSession.TotalXp, gameSession.Level);
    HandleStateChanged(gameSession.State);
}
```

只订阅事件会遇到初始化时序问题：如果 `GameSession.StartRun()` 先广播，HUD 后订阅，就会漏掉初始值。只拉快照也不够，因为后续变化还要持续更新。因此这里采用“事件负责变化，快照负责初始值”。

## 单局链路

### 开局

```text
Scene Load
  -> GameSession.Awake()
  -> new RunTimer(runDurationSeconds)
  -> GameSession.Start()
  -> StartRun()
  -> State = Running
  -> 广播初始 XP / 时间 / 状态
  -> RunHudView 显示 15:00、XP、Lv
```

### 时间胜利

```text
Update()
  -> state == Running
  -> RunTimer.Tick(Time.deltaTime)
  -> OnTimeChanged(elapsed, remaining)
  -> HUD 倒计时刷新
  -> timer.IsFinished
  -> SetState(Victory)
  -> HUD 显示 VICTORY
```

### 玩家死亡

```text
Health.OnDeath
  -> GameSession.HandlePlayerDeath()
  -> SetState(Defeat)
  -> HUD 显示 DEFEAT
```

### 经验显示

```text
XpOrb.Collect()
  -> XpOrb.OnCollected(lootEntry)
  -> GameSession.HandleXpCollected()
  -> totalXp += entry.amount
  -> OnXpChanged(totalXp, level)
  -> RunHudView 刷新 XP / Lv
```

## 常见错误

| 问题 | 根因 | 处理方式 |
|---|---|---|
| HUD 初始值为空 | HUD 订阅晚于 `StartRun()` 初始广播 | `Start()` 主动拉当前快照 |
| Pause Action 没响应 | Input Actions 新增动作但 PlayerInput UnityEvent 未接线 | 检查 `GameInput.inputactions`、PlayerInput 事件和 `InputReader.Pause` 绑定 |
| 一按暂停又立刻恢复 | `Running` 和 `Paused` 用两个连续 `if` | 使用 `if / else if`，一次输入只走一次状态迁移 |
| 胜利/失败后还能恢复游戏 | 输入层直接改 `Time.timeScale` 或状态 | 由 `GameSession` 根据 `GameState` 裁决 |
| 退出后 `timeScale` 留在 0 | 暂停系统改了全局状态但没有恢复口 | 恢复、禁用或退出时兜回 `Time.timeScale = 1f` |
| HUD 成为第二个状态主人 | HUD 自己算时间、经验或胜负 | HUD 只显示 `GameSession` 输出 |

## 如何验证

### 单局状态

- 场景加载后 `StartRun()` 进入 `Running`，HUD 显示初始时间、XP 和等级。
- 倒计时只在 `Running` 状态减少。
- 时间到达 0 后进入 `Victory`，HUD 显示胜利状态。
- 玩家死亡时进入 `Defeat`，HUD 显示失败状态。
- `Victory` / `Defeat` 后暂停键不会把状态拉回 `Running`。

### 经验与 HUD

- 收集经验球后，`totalXp` 增加并刷新 HUD。
- 非 `Running` 状态下收集经验不会继续累计本局 XP。
- HUD 后于 `GameSession` 初始化时，仍能通过快照显示当前值。
- 状态文本在 `Running` 时为空，在 `Paused` / `Victory` / `Defeat` 时显示对应文本。

### 暂停

- Escape 触发 `InputReader.OnPause`。
- `Running -> Paused` 时 `Time.timeScale = 0f`，倒计时停止。
- `Paused -> Running` 时 `Time.timeScale = 1f`，倒计时继续。
- 禁用 `GameSession` 或退出本局时，全局 `Time.timeScale` 被恢复。

### 工程边界

- `RunTimer` 不依赖 UnityEngine，可作为纯 C# 逻辑单独测试。
- `GameSession` 订阅 `Health.OnDeath`、`XpOrb.OnCollected`、`InputReader.OnPause` 时有镜像退订。
- `GameInput.inputactions` 保存了 `Pause` 动作，`01-Run.unity` 保存了 `GameSession`、HUD 和 PlayerInput 接线。
- 本环境只做项目文件只读复核，没有运行 Unity Editor / Play Mode；仍需在 Unity 中复核场景、Prefab、Input Actions、`.meta` / GUID 和实际暂停/胜负表现。

## 当前证据分层

| 结论 | 证据等级 | 说明 |
|---|---|---|
| 第 16 课实现了 `GameState`、`RunTimer`、`GameSession`、`RunHudView`、基础 HUD、暂停恢复和胜负入口 | B | 来自用户放入 Inbox 的课程记录 |
| 项目工作区存在 `GameState.cs`、`RunTimer.cs`、`GameSession.cs`、`RunHudView.cs` 及对应 `.meta` | C | 本环境对 `E:\YouXiKaiFa\Backpack Survivor` 做只读文件扫描 |
| `GameSession` 代码中可见 `Health.OnDeath`、`XpOrb.OnCollected`、`InputReader.OnPause` 订阅与镜像退订 | C | 本环境只读查看脚本，未编译或运行 Unity |
| `RunHudView` 采用事件订阅和 `Start()` 主动拉快照 | C | 本环境只读查看脚本，未运行场景 |
| 第 16 课已由当前环境在 Unity Editor / Play Mode 中运行通过 | D | 未启动 Unity，未运行 Play Mode，未验证场景接线 |
| 第 16 课当时已经完成经验成长与三选一 | D | 原始记录明确留到后续课程，本页只记录经验累计和显示；后续第 17 课已另页记录 |

## 相关内容

- 前置：[背包武器激活](backpack-weapon-activation.md)
- 前置：[背包 UI 与拖拽](inventory-ui-and-drag.md)
- 前置：[拾取与磁吸](pickup-and-magnet.md)
- 后续：[经验成长与三选一](level-progression-and-choice.md)
- 后续：[波次导演与 15 分钟节奏](wave-director-and-run-pacing.md)
- 后续：[战斗反馈快包](combat-feedback-pack.md)
- 后续：[胜负结算与重开闭环](run-result-and-restart-loop.md)
- Unity：[Unity 生命周期](../../unity/lifecycle.md)
- UGUI：[UGUI 总览](../../unity/ugui/index.md)
- C#：[委托与事件](../../csharp/oop/delegates-and-events.md)

> 📎 标签：`Unity` `单局框架` `GameSession` `HUD` `暂停` `GameState` `事件驱动 UI` `项目实践`
