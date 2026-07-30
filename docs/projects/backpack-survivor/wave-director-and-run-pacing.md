# 波次导演与 15 分钟节奏

> 项目：[Backpack Survivor](index.md)
>
> 状态：用户课程记录描述已实现 `WaveDirector`、波次阶段表、`EnemySpawner.ApplyWaveSettings()`、波次 HUD 和高频日志清理；本环境完成静态审阅、项目文件只读复核与文档验证，未运行 Unity Editor / Play Mode
>
> 日期：2026-07-30
>
> 阶段：V0.2 掉落与背包构筑 · 第 18 课

## 学习目标

- 把固定刷怪参数推进成按本局时间变化的压力曲线。
- 让 `GameSession.Elapsed` 成为波次系统的唯一时间事实源，避免第二套计时器。
- 用 `WaveDirector` 调度阶段，把“第几分钟该多难”从 `EnemySpawner` 中拆出去。
- 只在阶段变化时写入刷怪参数和广播 HUD，避免每帧重复触发。
- 让暂停、升级选择、胜利和失败等非 `Running` 状态不推进波次阶段。
- 用阶段名和颜色给玩家反馈 15 分钟 Demo 的压力变化。
- 清理高频目标注册日志，避免刷怪密度提高后 Console 噪音放大。

## 交付范围

| 模块 | 当前职责 |
|---|---|
| `EnemySpawner` | 执行刷怪：计时、环带取点、检查场上数量、从敌人池取出敌人 |
| `EnemySpawner.ApplyWaveSettings` | 接收导演给出的 `spawnInterval` 和 `maxAlive`，不判断当前阶段 |
| `WaveDirector` | 读取 `GameSession.Elapsed`，按阶段表切换压力参数 |
| `WaveStage` | 阶段配置：开始时间、刷怪间隔、最大存活数、阶段名和显示颜色 |
| `currentStageIndex` | 阶段门闸：只有 index 变化时才应用参数和广播事件 |
| `OnWaveStageChanged` | 把阶段序号、名称和颜色传给 HUD |
| `RunHudView.waveText` | 显示 `WAVE n · 阶段名`，并使用阶段配置颜色 |
| `TargetRegistry` | 保持目标注册表职责，清掉注册 / 注销临时日志 |

第 17 课已经形成“打怪 -> 吃经验 -> 升级 -> 变强”的成长循环。第 18 课补上它的对手戏：敌人压力随本局时间上升，玩家强化不再只是数字变大，而是用来对抗更密、更高压的波次。

## EnemySpawner

第 5 课的 `EnemySpawner` 已经能在玩家周围环带刷敌人。第 18 课保留它的执行器职责，只新增一个外部调参入口：

```csharp
public void ApplyWaveSettings(float spawnInterval, int maxAlive)
{
    if (spawnInterval < 0.1 || maxAlive <= 0) return;

    this.spawnInterval = spawnInterval;
    this.maxAlive = maxAlive;
}
```

`EnemySpawner` 不关心第几分钟，也不保存阶段名或颜色。它只知道当前应该多久刷一次、最多允许多少个目标存活。这样它可以继续复用原来的环带取点、对象池和 `TargetRegistry.Count` 上限逻辑。

当前静态代码中 `maxAlive` 字段是 `float`，`ApplyWaveSettings` 参数是 `int`。作为“数量上限”，长期看更适合统一为整数；当前不影响文档入库，但应在后续整理工程细节时归一。

## WaveStage

`WaveStage` 是一段压力配置：

```csharp
[Serializable]
public class WaveStage
{
    public float startTimeSeconds;
    public float spawnInterval;
    public int maxAlive;
    public string stageName;
    public Color displayColor;
}
```

字段分成两类：

| 字段 | 用途 |
|---|---|
| `startTimeSeconds` | 阶段开始锚点，单位是本局已运行秒数 |
| `spawnInterval` | 当前阶段刷怪间隔，越小压力越高 |
| `maxAlive` | 当前阶段场上敌人上限 |
| `stageName` | HUD 显示的可读阶段名 |
| `displayColor` | HUD 显示颜色，课程记录中特别要求 alpha 为 `1` |

把阶段名称和颜色放在配置中，可以避免 HUD 自己写“第几波变什么颜色”的判断。表现信息是阶段配置的一部分，HUD 只投影导演给出的结果。

## WaveDirector

`WaveDirector` 是 15 分钟压力曲线的规则主人：

```csharp
private void Update()
{
    if (gameSession == null || enemySpawner == null) return;
    if (gameSession.State != GameState.Running) return;
    if (waveStages == null || waveStages.Count == 0) return;

    for (int i = waveStages.Count - 1; i >= 0; i--)
    {
        if (gameSession.Elapsed >= waveStages[i].startTimeSeconds)
        {
            int stageIndex = currentStageIndex;
            currentStageIndex = i;

            if (stageIndex != currentStageIndex)
            {
                enemySpawner.ApplyWaveSettings(
                    waveStages[i].spawnInterval,
                    waveStages[i].maxAlive);

                OnWaveStageChanged?.Invoke(
                    currentStageIndex,
                    waveStages[i].stageName,
                    waveStages[i].displayColor);
            }

            break;
        }
    }
}
```

三个边界最重要：

- **时间事实源**：只读 `GameSession.Elapsed`，不自己累计第二套时间。
- **状态门闸**：只有 `GameState.Running` 时才判断阶段，暂停和升级选择不会偷跑难度。
- **阶段门闸**：只有 `currentStageIndex` 变化时才应用参数和广播事件。

阶段查找采用倒序，是因为后面的阶段天然也满足前面阶段的开始条件。比如第 9 分钟同时满足 0、2、5、8 分钟阶段，如果正序遍历就会停在开局阶段；倒序遍历会优先命中最新阶段。

## 开局阶段

`currentStageIndex` 初始为 `-1`。只要第 0 阶段的 `startTimeSeconds` 已满足，第一帧 `Running` 就会被视为一次正式阶段切换：

```text
currentStageIndex = -1
  -> 命中 waveStages[0]
  -> ApplyWaveSettings()
  -> OnWaveStageChanged(0, name, color)
  -> RunHudView 显示 WAVE 1
```

这解决了事件驱动 UI 的初始值问题：不能只等“下一次变化”，开局阶段本身也应该广播一次。

## RunHudView

`RunHudView` 订阅 `WaveDirector.OnWaveStageChanged`：

```csharp
private void HandleWaveStageChanged(int stageIndex, string stageName, Color displayColor)
{
    if (waveText == null) return;

    waveText.text = $"WAVE {stageIndex + 1} · {stageName}";
    waveText.color = displayColor;
}
```

HUD 不写阶段规则。它不判断第几分钟、不计算刷怪压力，也不决定颜色含义。它只显示导演给出的阶段序号、阶段名和颜色。

这条边界延续了第 16、17 课的 UI 原则：

```text
规则层：GameSession / WaveDirector
展示层：RunHudView
```

## 周期链路

### 开局进入第 1 波

```text
Scene Start
  -> GameSession.StartRun()
  -> State = Running
  -> WaveDirector.Update()
  -> Elapsed >= waveStages[0].startTimeSeconds
  -> currentStageIndex: -1 -> 0
  -> EnemySpawner.ApplyWaveSettings()
  -> OnWaveStageChanged(0, name, color)
  -> RunHudView 显示 WAVE 1
```

### 阶段切换

```text
RunTimer.Tick(Time.deltaTime)
  -> GameSession.Elapsed 增长
  -> WaveDirector 倒序匹配当前阶段
  -> 阶段 index 发生变化
  -> ApplyWaveSettings(spawnInterval, maxAlive)
  -> OnWaveStageChanged(stageIndex, name, color)
  -> 刷怪压力提高，HUD 文案和颜色更新
```

### 暂停与升级选择

```text
Esc 暂停 / 升级三选一
  -> GameSession.State != Running
  -> WaveDirector.Update() return
  -> 不切阶段，不改刷怪参数
```

普通暂停和升级选择都会把 `Time.timeScale` 置为 `0`，`EnemySpawner` 的 `Time.deltaTime` 也会停住。但胜利 / 失败状态是否还需要显式停用刷怪器，不能只靠 `WaveDirector` 推断，仍需 Play Mode 复核。

## 15 分钟节奏

课程记录中的目标是给 Demo 一条清晰压力曲线：

```text
开局适应
  -> 中期上压
  -> 后期困难
  -> 末段冲刺
```

这个阶段系统比直接上 Boss 更适合当前项目阶段：它低成本、可配置、能验证成长系统，也能为后续精英潮、Boss 前压迫、宝箱节奏和结算面板提供时间轴入口。

## 高频日志清理

第 18 课还清理了 `TargetRegistry` 注册 / 注销时的临时 `Debug.Log`。这不是小事：刷怪密度提高后，目标注册和注销会变成高频路径。无意义日志会：

- 污染 Console，让真正错误更难看见；
- 影响运行时性能观察；
- 在批量敌人生成 / 死亡时制造大量字符串和编辑器开销。

调试信息如果后续还需要，应做成可开关的调试模式，而不是长期留在热路径中。

## 常见错误

| 问题 | 根因 | 处理方式 |
|---|---|---|
| 开局波次 HUD 为空 | 只等后续阶段变化，没有广播第 0 阶段 | `currentStageIndex = -1`，开局命中第 0 阶段也广播 |
| 第 9 分钟仍命中第 0 阶段 | 正序查找阶段，先命中早期条件 | 倒序遍历阶段表，优先匹配最新阶段 |
| 升级选择时难度偷跑 | 波次系统自己计时或不看 `GameSession.State` | `WaveDirector` 只在 `Running` 工作，并读取 `GameSession.Elapsed` |
| HUD 文字存在但看不见 | 阶段颜色 alpha 为 `0` | Inspector 中把 `displayColor.a` 调为 `1` |
| 每帧重复触发波次表现 | 没有阶段 index 门闸 | 只有 `currentStageIndex` 变化时才 Apply 和广播 |
| 胜负后仍可能刷怪 | `WaveDirector` 停止切阶段，但 `EnemySpawner` 未显式读取终局状态 | Play Mode 复核胜负后刷怪行为，必要时让刷怪器订阅状态或由 GameSession 停用刷怪 |
| 高压刷怪时 Console 爆量 | 高频注册 / 注销路径留 `Debug.Log` | 删除临时日志或做成显式调试开关 |

## 如何验证

### 波次阶段

- 开局进入 `Running` 后立即显示第 1 波，HUD 不为空。
- 到达每个 `WaveStage.startTimeSeconds` 后只切换一次阶段。
- 阶段切换后 `EnemySpawner.spawnInterval` 和 `maxAlive` 符合配置。
- 倒序匹配能在后期时间命中最新阶段，而不是早期阶段。
- 阶段颜色 alpha 为 `1`，HUD 文案可见。

### 状态与暂停

- 普通暂停时波次阶段不切换，刷怪计时不推进。
- 升级三选一时波次阶段不切换，恢复后按本局时间继续判断。
- 胜利 / 失败后是否还会生成新敌人需要单独确认；当前静态代码只能证明 `WaveDirector` 不再切阶段，不能证明 `EnemySpawner` 被停用。

### 工程边界

- `WaveDirector` 不维护第二套计时器，只读 `GameSession.Elapsed`。
- `WaveDirector` 和 `RunHudView` 的事件订阅 / 退订成对。
- `EnemySpawner.ApplyWaveSettings()` 对非法间隔和非正上限有保护。
- `TargetRegistry` 高频注册 / 注销路径不保留临时日志。
- 本环境只做项目文件只读复核，没有运行 Unity Editor / Play Mode；仍需在 Unity 中复核 `WaveDirector` 阶段表、HUD 文本引用、颜色 alpha、对象池峰值、刷怪压力和 Profiler / GC Alloc。

## 当前证据分层

| 结论 | 证据等级 | 说明 |
|---|---|---|
| 第 18 课实现了 `WaveDirector`、阶段表、波次 HUD 和刷怪参数调度 | B | 来自用户放入 Inbox 的课程记录 |
| 项目工作区存在 `WaveDirector.cs`、`EnemySpawner.cs`、`RunHudView.cs`、`TargetRegistry.cs` 及相关 `.meta` | C | 本环境对 `E:\YouXiKaiFa\Backpack Survivor` 做只读文件扫描 |
| `WaveDirector` 代码中可见读取 `GameSession.Elapsed`、`GameState.Running` 门闸、倒序阶段匹配和 `OnWaveStageChanged` 广播 | C | 本环境只读查看脚本，未编译或运行 Unity |
| `RunHudView` 代码中可见波次事件订阅和 `waveText` 文案 / 颜色刷新 | C | 本环境只读查看脚本，未运行场景 |
| `01-Run.unity` 中可见 `WaveDirector`、`EnemySpawner`、`RunHudView.waveText` 和阶段颜色 alpha 为 `1` 的 YAML 片段 | C | 本环境只读检查场景 YAML 和 `.meta` GUID，未打开 Unity Editor |
| 第 18 课已由当前环境在 Unity Editor / Play Mode 中运行通过 | D | 未启动 Unity，未运行 Play Mode，未验证真实刷怪节奏、HUD 颜色或对象池压力 |
| 胜利 / 失败后刷怪器一定停止 | D | 当前静态代码只能看到 `WaveDirector` 停止切阶段，`EnemySpawner` 是否继续刷怪需 Play Mode 复核 |

## 相关内容

- 前置：[经验成长与三选一](level-progression-and-choice.md)
- 前置：[单局框架与基础 HUD](run-session-and-basic-hud.md)
- 前置：[刷怪器与对象池](spawner-and-object-pooling.md)
- 后续：[战斗反馈快包](combat-feedback-pack.md)
- Unity：[Unity 生命周期](../../unity/lifecycle.md)
- UGUI：[UGUI 总览](../../unity/ugui/index.md)
- 性能：[优化小 Tips](../../performance/perf-tips.md)

> 📎 标签：`Unity` `波次系统` `刷怪器` `GameSession` `时间轴` `HUD` `对象池` `项目实践`
