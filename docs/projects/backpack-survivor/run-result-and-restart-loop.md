# 胜负结算与重开闭环

> 项目：[Backpack Survivor](index.md)
>
> 状态：用户课程记录描述已实现 `RunResult`、`GameSession.EndRun()`、`ResultView`、重开/退出按钮、环形经验 HUD 和血条 Slider 显示化修复；本环境完成静态审阅、项目文件只读复核与文档验证，未运行 Unity Editor / Play Mode
>
> 日期：2026-07-31
>
> 阶段：V0.2 掉落与背包构筑 · 第 20 课

## 学习目标

- 把胜利和失败统一收束到同一个终局入口，避免结算流程分叉。
- 用 `RunResult` 保存本局结束瞬间的数据快照，让结算 UI 只读结果，不反查运行时系统。
- 让 `GameSession.OnRunEnded` 成为结算事件源，`ResultView` 只负责显示面板、填充文案和处理按钮。
- 通过 `EnemyAI.OnEnemyDied` 统计本局击杀数，并在终局时写入结果快照。
- 用场景重载完成 Demo 阶段的“再来一局”闭环，同时明确 Build Settings 仍需复核。
- 把 XP HUD 从文本进度推进到环形 `Image.fillAmount`，并把血条 Slider 改成纯显示控件。

## 交付范围

| 模块 | 当前职责 |
|---|---|
| `RunResult` | 普通 C# 结果快照，记录 `FinalState / Elapsed / Level / TotalXp / KillCount`；第 25 课继续追加 `BackpackValue` |
| `GameSession.EndRun()` | 统一 Victory / Defeat 终局路径，切状态、暂停时间、生成结果并广播 |
| `GameSession.OnRunEnded` | 向表现层发布本局结算快照 |
| `EnemyAI.OnEnemyDied` | 敌人死亡的静态广播入口，供 `GameSession` 统计本局击杀数 |
| `ResultView` | 订阅 `OnRunEnded`，显示结算面板、标题颜色、统计文本和按钮行为 |
| `RestartButton` / `QuitButton` | 重开前恢复 `Time.timeScale = 1f` 并重载当前场景；退出按钮调用 `Application.Quit()` |
| `RunHudView.xpLoop` | 用 `Image.fillAmount` 显示当前等级内 XP 进度 |
| `HpSlider` | 关闭 `Interactable` 与 Navigation，让血条只作为 HUD 显示器 |

第 19 课补上了命中、受伤、升级和开箱反馈。第 20 课补的是“这一局怎么完整结束”：玩家死亡或时间胜利后，都要停表、出结算、显示本局结果，并能安全重开。

## RunResult

`RunResult` 不继承 `MonoBehaviour`，也不挂场景。它只是终局瞬间的一份数据快照：

```csharp
public class RunResult
{
    public GameState FinalState { get; }
    public float Elapsed { get; }
    public int Level { get; }
    public int TotalXp { get; }
    public int KillCount { get; }
}
```

这个边界很关键：结算面板显示的是“结束那一刻”的结果，而不是 UI 打开时再去追问 `GameSession`、经验系统、敌人系统或 HUD。第 25 课已经沿用这个规则补入 `BackpackValue`；后续如果要加本局金币、伤害统计、最高波次，也应先写入结果快照，再由表现层读取。

## GameSession.EndRun

胜利和失败都属于终局流程。第 20 课把它们统一到 `EndRun(finalState)`：

```csharp
private void EndRun(GameState finalState)
{
    if (state != GameState.Running) return;

    SetState(finalState);
    Time.timeScale = 0f;

    RunResult runResult = new RunResult(finalState, Elapsed, Level, TotalXp, killCount);
    OnRunEnded?.Invoke(runResult);
}
```

统一入口解决的是分叉一致性问题：胜利和失败都必须切状态、暂停时间、生成结果、广播结算。差异只剩 `GameState.Victory` 或 `GameState.Defeat`，不让“胜利有面板、失败漏面板”这类 bug 有空间。

`EndRun()` 的 `state != GameState.Running` 守卫也很重要。升级选择、普通暂停、已经结算后的重复死亡或计时回调，都不能再次生成结果。

## 击杀统计

敌人是池化对象，场上实例会不断启用、死亡和归还。如果 `GameSession` 对每个敌人实例逐个订阅，生命周期会很绕。第 20 课沿用项目里已有的静态死亡广播：

```text
EnemyAI.Die()
  -> EnemyAI.OnEnemyDied?.Invoke()
  -> GameSession.HandleEnemyDied()
  -> Running 状态下 killCount++
```

`killCount` 在 `StartRun()` 中归零，只有 `state == Running` 时递增，终局时写入 `RunResult.KillCount`。这样结算面板只展示快照，不需要自己数场景里还剩多少敌人。

静态事件的风险仍然存在：订阅和退订必须镜像，跨场景或重开时不能留下旧订阅者。本次静态检查只能确认 `GameSession` 中可见订阅/退订和状态守卫，不能替代 Play Mode 中对池化敌人、重复死亡和场景重载后的实测。

## ResultView

`ResultView` 是结算 UI 的投影层：

```text
OnRunEnded(RunResult)
  -> ResultPanel.SetActive(true)
  -> 根据 FinalState 设置胜利/失败标题和颜色
  -> 显示存活时间、等级、总经验、击杀数
```

它的职责不是判断玩家是否赢了，也不是重新统计数值。它只消费 `RunResult`，把已经确定的本局事实展示出来。

一个重要摆放规则是：`ResultView` 应挂在常驻的 UI 根节点上，`ResultPanel` 只是被它控制显隐的子面板。若把脚本挂在 `ResultPanel` 自己身上，隐藏面板会触发 `OnDisable()`，脚本退订 `OnRunEnded` 后就再也收不到结算事件。本次只读场景 YAML 可见 `ResultView` 挂在激活的 `Canvas` 上，`ResultPanel` 默认未激活，符合这个模式。

## 重开与退出

重开按钮当前走场景重载：

```csharp
private void HandleRestartClicked()
{
    Time.timeScale = 1f;

    int buildIndex = SceneManager.GetActiveScene().buildIndex;
    SceneManager.LoadScene(buildIndex);
}
```

先恢复 `Time.timeScale` 是必要动作。结算时 `EndRun()` 会把时间停在 `0f`，如果重开前不恢复，下一局可能继承暂停状态。

场景重载是 Demo 阶段很实用的清场方案：敌人池、投射物池、掉落物、背包、升级暂停、HUD、静态事件和临时运行态很多，手写 `ResetAll()` 很容易漏。等主菜单、关卡选择或无缝再开局需求稳定后，再决定是否拆成更细的重置流程。

本次只读复核发现一个必须保留的待验证点：Unity 项目中实际检查到的运行场景文件是 `Assets/BackpackSurvivor/Scenes/Run/01-Run.unity`，但 `EditorBuildSettings.asset` 指向 `Assets/BackpackSurvivor/Scenes/Run/Run1.unity`。因此当前只能说明按钮代码会按“当前场景 buildIndex”重载，不能声明 Build Settings 下的重开路径已经验证通过。

`QuitButton` 当前调用 `Application.Quit()`。它在 Editor 中通常不会真的退出，需要在目标 Build 中验证。

## 环形经验 HUD

第 20 课把经验显示从“文字进度”推进成环形经验：

```csharp
float ratio = 0f;

if (xpToNextLevel > 0)
    ratio = Mathf.Clamp01((float)currentXp / xpToNextLevel);

if (xpLoop != null)
    xpLoop.fillAmount = ratio;

levelText.text = level.ToString();
```

这里显示的是当前等级内进度，所以分子应是 `currentXp`，不是累计经验 `totalXp`。累计经验适合结算统计；圆环适合表达“距离下一等级还差多少”。

UGUI 的 `Image` 设置为 Filled / Radial 360 后，`fillAmount` 就是 0 到 1 的比例。圆环经验条不需要用 Slider 模拟，也不会天然成为 EventSystem 的可交互控件。

## HUD Slider 显示化

课程记录中还修复了一个常见 UI 输入坑：血条 `Slider` 被 EventSystem 选中后，A/D 或方向键会调整它的值。

处理方式是：

```text
HpSlider.Interactable = false
HpSlider.Navigation = None
```

血条属于 HUD 显示器，不是玩家可操作控件。只要它参与 Selectable 导航，就可能抢走玩家移动输入。本次静态场景检查可见 `HpSlider` 对应组件的 `m_Interactable: 0`，并且 `RunHudView.Awake()` 也有禁用交互和 Navigation 的兜底逻辑；真实输入行为仍需 Play Mode 复核。

## 周期链路

### 失败结算

```text
Player Health 归零
  -> Health.OnDeath
  -> GameSession.HandlePlayerDeath()
  -> EndRun(GameState.Defeat)
  -> SetState(Defeat) + Time.timeScale = 0
  -> new RunResult(...)
  -> OnRunEnded(result)
  -> ResultView 显示失败结算
```

### 胜利结算

```text
RunTimer.Tick(Time.deltaTime)
  -> timer.IsFinished
  -> EndRun(GameState.Victory)
  -> SetState(Victory) + Time.timeScale = 0
  -> new RunResult(...)
  -> OnRunEnded(result)
  -> ResultView 显示胜利结算
```

### 重开

```text
点击 RestartButton
  -> ResultView.HandleRestartClicked()
  -> Time.timeScale = 1
  -> SceneManager.LoadScene(currentBuildIndex)
  -> 场景重新加载
```

### XP 圆环

```text
拾取经验球
  -> GameSession.HandleXpCollected()
  -> LevelProgress.AddXp()
  -> OnXpChanged(totalXp, level, currentXp, xpToNextLevel)
  -> RunHudView 更新 xpLoop.fillAmount 和等级数字
```

## 常见错误

| 问题 | 根因 | 处理方式 |
|---|---|---|
| 结算时面板不出现 | `ResultView` 挂在默认隐藏的 `ResultPanel` 上，隐藏后退订事件 | 把 `ResultView` 挂在常驻 Canvas / HUDRoot，面板只作为被控制对象 |
| 标题文字赋值但不可见 | 胜利/失败标题颜色 alpha 为 0 | 先查对象激活、引用，再查颜色 alpha |
| 下一局一开始就是暂停 | 终局或暂停后重开前没有恢复 `Time.timeScale` | `LoadScene()` 前先设 `Time.timeScale = 1f` |
| 圆环进度异常飙满 | 使用累计 `totalXp` 除以下一级阈值 | 使用当前等级内 `currentXp / xpToNextLevel` |
| 血条被键盘左右键控制 | Slider 仍可交互并参与 Navigation | HUD Slider 关闭 `Interactable`，Navigation 设为 None |
| 统计击杀重复或跨局污染 | 静态事件订阅未退订，或池化敌人重复触发死亡 | `OnEnable` / `OnDisable` 镜像订阅，死亡入口加幂等守卫，Play Mode 复核 |
| 重开按钮在 Build 中加载失败 | Build Settings 场景路径或 buildIndex 配置不一致 | 复核 `EditorBuildSettings.asset`，确保当前 Run 场景进入 Build Settings |
| Quit 在 Editor 中没反应 | `Application.Quit()` 在 Editor 下通常不退出 | 在目标 Build 中验证退出行为 |

## 如何验证

### 结算路径

- 玩家死亡后进入失败结算，倒计时停止，ResultPanel 出现。
- 计时结束后进入胜利结算，倒计时停止，ResultPanel 出现。
- 终局后不会继续刷怪、拾取经验、弹升级选择或重复触发结算。
- 普通暂停和升级选择状态不会误触发 `EndRun()`。

### 结果数据

- `RunResult.FinalState` 与触发路径一致：死亡为 `Defeat`，时间到为 `Victory`。
- 存活时间格式正确，失败时显示真实已存活时间，胜利时接近本局目标时长。
- 等级、总经验和击杀数与本局 HUD / 战斗过程一致。
- 池化敌人死亡只统计一次，重开后 `killCount` 从 0 开始。

### UI 与按钮

- `ResultView` 挂在常驻 Canvas / HUDRoot，不挂在默认隐藏的 ResultPanel 上。
- `ResultPanel` 默认隐藏，结算时由 `ResultView` 显示。
- `RestartButton` 点击后先恢复 `Time.timeScale`，再加载正确的 Run 场景。
- `QuitButton` 在目标 Build 中可以退出游戏。
- 胜利/失败标题颜色 alpha 为 1。

### HUD

- 经验圆环随 `currentXp / xpToNextLevel` 增长，升级后回到溢出进度。
- 圆环中间等级文本随等级变化刷新。
- `HpSlider` 不可交互，Navigation 为 None，键盘移动不会改变血条值。
- HUD 控件没有因为 RaycastTarget 或 Selectable 抢走玩家输入。

### 工程边界

- `RunResult` 是普通 C# 类，不依赖 Unity 生命周期。
- `GameSession` 对玩家死亡、经验拾取、暂停输入和敌人死亡事件的订阅退订保持镜像。
- `ResultView` 对 `OnRunEnded` 与按钮 `onClick` 的订阅退订保持镜像。
- `EditorBuildSettings.asset` 中的 Run 场景路径与实际场景文件一致。
- 本环境只做项目文件只读复核，没有运行 Unity Editor / Play Mode；仍需在 Unity 中复核真实结算画面、按钮、Build Settings、场景重载和退出行为。

## 当前证据分层

| 结论 | 证据等级 | 说明 |
|---|---|---|
| 第 20 课实现了 `RunResult`、统一 `EndRun()`、`OnRunEnded`、`ResultView`、重开/退出按钮、环形 XP HUD 和 HUD Slider 显示化修复 | B | 来自用户放入 Inbox 的课程记录 |
| 项目工作区存在 `RunResult.cs`、`ResultView.cs`、`GameSession.cs`、`RunHudView.cs`、`EnemyAI.cs` 及对应 `.meta` / 场景引用 | C | 本环境对 `E:\YouXiKaiFa\Backpack Survivor` 做只读文件扫描和 `rg` 检查 |
| `GameSession` 代码中可见 `EnemyAI.OnEnemyDied` 订阅、`killCount` 归零/递增、`EndRun(finalState)`、`RunResult` 生成和 `OnRunEnded` 广播 | C | 本环境只读查看脚本，未编译或运行 Unity |
| `ResultView` 代码中可见订阅 `OnRunEnded`、显示面板、填充标题/统计、重开前恢复 `Time.timeScale` 并调用 `SceneManager.LoadScene(buildIndex)` | C | 本环境只读查看脚本，未点击按钮 |
| `01-Run.unity` 中可见 `ResultView` 挂在激活的 `Canvas` 上、引用默认隐藏的 `ResultPanel`，并引用 Restart / Quit 按钮 | C | 本环境只读检查场景 YAML 和脚本 GUID |
| `RunHudView` 代码中可见 `xpLoop.fillAmount`，场景中可见 `HpSlider` 为不可交互 | C | 本环境只读查看脚本和场景 YAML |
| 重开按钮在目标 Build 中一定加载正确场景 | D | 当前 `EditorBuildSettings.asset` 指向 `Run1.unity`，而实际检查到的场景文件是 `01-Run.unity`，需要 Unity 中复核 |
| 当前环境已在 Unity Editor / Play Mode 中验证结算、重开、退出和 HUD 行为 | D | 未启动 Unity，未运行 Play Mode，未验证真实按钮、场景重载或 Build 行为 |

## 相关内容

- 前置：[战斗反馈快包](combat-feedback-pack.md)
- 前置：[波次导演与 15 分钟节奏](wave-director-and-run-pacing.md)
- 前置：[经验成长与三选一](level-progression-and-choice.md)
- 前置：[单局框架与基础 HUD](run-session-and-basic-hud.md)
- 系统：[容器搜刮与宝箱系统](container-looting-and-chests.md)
- 后续：[构筑最小兑现](build-payoff-dual-wield.md)
- 后续：[金币掉落与局内经济 HUD](gold-drops-and-economy-hud.md)
- 后续：[背包价值与物品价值显示](backpack-value-and-item-value-display.md)
- C#：[委托与事件](../../csharp/oop/delegates-and-events.md)
- C#：[C# 工程实践路线](../../csharp/engineering/index.md)
- UGUI：[UGUI 总览](../../unity/ugui/index.md)
- Unity：[Unity 生命周期](../../unity/lifecycle.md)

> 📎 标签：`Unity` `RunResult` `结算面板` `GameSession` `SceneManager` `UGUI` `TimeScale` `项目实践`
