# 场景氛围与演示包装

> 学习状态：项目中使用，待复测
>
> 验证状态：用户记录称已完成实测与代码验收；本次只读复核外部 Unity 工程脚本、输入配置、场景 YAML、材质和 `.meta`，未运行 Unity Editor / Play Mode / Profiler / Player Build。
>
> 前置知识：[主菜单与场景流](main-menu-and-scene-flow.md)、[物品图标与背包可读性](item-icons-and-backpack-readability.md)、[容器搜刮与宝箱系统](container-looting-and-chests.md)、[合并升级收益兑现](merge-upgrade-reward-payoff.md)
>
> 对应项目：[Backpack Survivor](index.md)
>
> 下一步：第 34 课完整 15 分钟通关验收
>
> 日期：2026-08-08
>
> 阶段：V0.2 掉落与背包构筑 · 第 33 课

## 学习目标

- 在不新增大系统的前提下，提升 Demo 第一眼的画面秩序和试玩可读性。
- 让装备掉落复用经验 / 金币已有的散落飞行反馈。
- 用 Tab 背包开关减少战斗视野遮挡，并保护拖拽中的临时态。
- 修复物品丢弃再拾取后等级重置的问题，保持 `Item -> LootEntry -> Item` 往返保真。
- 在新一局开始时主动清理静态运行时状态，降低重开残留风险。
- 用 URP Lit 地面材质和阴影链路让角色、地面和场景光照更统一。

## 当前理解

第 33 课不是继续开大机制，而是做 Demo 冲刺期的包装补强：场景地面、边界提醒、宝箱辨识、掉落反馈、背包占屏、重开稳定性和光照阴影。它们不一定是最炫的功能，但会直接影响外部试玩者是否觉得项目“像一版完成的 Demo”。

当前观感链路是：

```text
主菜单进入 Run
  -> 地面与边界更像正式场景
  -> 敌人死亡后装备 / 经验 / 金币都有散落反馈
  -> 背包默认关闭，Tab 调出整理
  -> 丢弃回捡保留等级
  -> 重开时清理静态状态
  -> 地面参与光照并接收阴影
```

危险区视觉暂缓是合理取舍：它会改变路线压力和数值节奏，需要更多平衡验证；背包开关、掉落散落、材质和重置入口属于低风险高感知收益，更适合 V0.2 收口。

## 交付范围

| 模块 | 当前职责 |
|---|---|
| `LootManager.SpawnEntry()` | 装备、经验、金币生成后统一调用散落飞行表现 |
| `DropItem.PlayScatterFlight()` | 装备掉落短距离抛物线飞散，飞行期间关闭碰撞，落地后恢复 |
| `DropItem.OnGetFromPool()` | 停止旧飞行协程、归零计时和收集态、恢复碰撞器 |
| `InputReader.OnOpenBag` | 输入层把 Tab 翻译成打开 / 关闭背包意图 |
| `InventoryUIController.HandleOpenBag()` | 用 `CanvasGroup` 同步控制背包可见、可交互和射线阻挡 |
| `LootEntry.level` | 世界掉落实例临时携带运行时物品等级 |
| `Item` 构造函数 | 接收并钳制等级到 `1 ~ MaxLevel` |
| `GameSession.StartRun()` | 新一局开始时清理 `TargetRegistry` 和 `LootChest` 静态运行时状态 |
| `M_Ground_Quarantine_Lit.mat` | 地面使用 URP Lit 材质，参与光照并接收阴影 |

## 最小示例

### 装备掉落复用散落飞行

```csharp
if (entry.category == DropCategory.Equipment)
{
    Vector2 randomOffset = Random.insideUnitCircle * offset;
    Vector3 target = position + new Vector3(randomOffset.x, 0, randomOffset.y);
    DropItem dropItem = dropPool.Get(position).GetComponent<DropItem>();
    dropItem.Initialize(entry);
    dropItem.PlayScatterFlight(position, target);
    return dropItem.gameObject;
}
```

装备不需要另写一套动画。经验、金币、装备都从死亡点散开，玩家能用同一种视觉语言理解“这是战利品”。

### 池化对象清理飞行状态

```csharp
public void OnGetFromPool()
{
    if (flightRoutine != null)
    {
        StopCoroutine(flightRoutine);
        flightRoutine = null;
    }

    survivalTimer = 0f;
    itemCollider.enabled = true;
    isCollected = false;
}
```

池化类新增运行时字段后，必须同一分钟补出池归零。否则“飞行中被回收”的对象可能带着旧协程或关闭的碰撞器再次出场。

### Tab 背包开关

```csharp
public void OpenBag(InputAction.CallbackContext ctx)
{
    if (ctx.performed) OnOpenBag?.Invoke();
}

public void HandleOpenBag()
{
    if (bagPanelcanvasGroup == null || isDragging) return;

    isBagOpen = !isBagOpen;

    bagPanelcanvasGroup.alpha = isBagOpen ? 1 : 0;
    bagPanelcanvasGroup.interactable = isBagOpen;
    bagPanelcanvasGroup.blocksRaycasts = isBagOpen;

    if (!isBagOpen)
        HideTooltip();

    Redraw();
}
```

背包关闭不是只改透明度。`alpha / interactable / blocksRaycasts` 必须同步，否则透明面板仍可能吃点击或 Tooltip 不跟着消失。拖拽中禁止关包，是为了保护 `dragItem`、`ghost`、旧锚点和预览格子这些临时态。

### 丢弃再拾取保留等级

```csharp
LootEntry entry = new LootEntry
{
    id = item.Id,
    rarity = item.Rarity,
    width = item.BaseWidth,
    height = item.BaseHeight,
    itemTag = item.Tag,
    connectableSides = item.LocalConnectableSides,
    scoreValue = item.BaseScoreValue,
    effectValue = item.BaseEffectValue,
    level = item.Level
};
```

这里写的是 `BaseScoreValue / BaseEffectValue`，不是当前等级放大后的值；否则 Lv.2 物品会把已放大的数值错误当成 Lv.1 基础值。`level` 承担“这一次世界掉落实例”的运行时等级，不回写 ScriptableObject。

### 新一局清静态状态

```csharp
public void StartRun()
{
    playerRunStats.ResetToDefault();
    TargetRegistry.Clear();
    LootChest.ResetRuntimeState();
    timer.Reset();
    levelProgress.Reset();
    killCount = 0;
    totalGold = 0;

    SetState(GameState.Running);
    BroadcastXpChanged();
}
```

场景重载不等于 static 自动归零。目标注册表、未开启宝箱列表和场上宝箱计数都属于本局运行时状态，必须有明确 Reset 入口。

### 地面 Lit 材质

```text
Material: M_Ground_Quarantine_Lit
Shader: Universal Render Pipeline/Lit
BaseMap: 场景地面贴图
Receive Shadows: 1
```

地面贴图解决“长什么样”，Lit 材质解决“怎么被光照”。想让玩家、宝箱和地面处在同一个空间里，主地面至少要参与光照并接收阴影。

## 项目中的应用

### 体验优先级收口

第 33 课选择包装和稳定性，而不是继续加机制。这说明 Demo 冲刺期的优先级不是“所有想法都做”，而是优先处理玩家马上能看到、能误解、能被卡住的点。

### UI 从常驻 HUD 改成主动管理界面

背包是核心系统，但不应该一直抢占战斗视野。Tab 开关让它变成“需要整理时主动打开”的管理界面，同时仍保留背包幸存者的构筑节奏。

### 运行时状态往返保真

等级已经影响武器伤害、芯片效果、物品价值和背包决策，因此它不能在丢弃到世界再拾取时丢失。正确边界是：静态配置仍在 ScriptableObject，单次世界掉落实例用 `LootEntry.level` 暂存运行时状态。

### 重开稳定性从显式 Reset 开始

第 20 课依赖场景重载清场，第 33 课开始补显式静态状态清理。两者并不冲突：场景重载负责大部分场景对象，`StartRun()` 负责那些不会随场景对象自然销毁的 static 容器。

## 常见错误

| 问题 | 根因 | 处理方式 |
|---|---|---|
| 丢弃再拾取后等级回到 1 | `Item -> LootEntry -> Item` 往返链没有携带 Level | `LootEntry.level = item.Level`，拾取时传入 `Item` 构造函数 |
| Lv.2 当前值污染 Lv.1 基础值 | 丢弃时写入 `ScoreValue / EffectValue` 当前收益 | 丢弃时写 `BaseScoreValue / BaseEffectValue` |
| 透明背包挡住点击 | 只改 `alpha`，没有关 `blocksRaycasts` | 用 CanvasGroup 三件套同步开关 |
| 拖拽中关包导致 ghost 残留 | 背包开关破坏拖拽临时态 | `isDragging` 时拒绝切换背包 |
| 重开后敌人或宝箱状态残留 | static 容器不随场景对象生命周期自动清空 | `TargetRegistry.Clear()` 与 `LootChest.ResetRuntimeState()` 放入新局入口 |
| 装备飞行对象再次出池异常 | 旧协程、碰撞器或 collected 状态残留 | `OnGetFromPool()` 停协程并归零运行态 |
| 地面不受光照 | 材质使用 Unlit 或 Renderer / URP 阴影链路不完整 | 检查 Lit Shader、Cast Shadows、Receive Shadows、URP Asset 阴影支持 |

## 如何验证

### 当前已记录证据

| 结论 | 证据等级 | 说明 |
|---|---|---|
| 用户记录已通过装备散落、Tab 背包、拖拽中不关包、关包隐藏 Tooltip、丢弃回捡等级保真、重开刷新状态和地面阴影链路验收 | B | 来自用户放入 Inbox 的第 33 课课程记录 |
| 用户记录称 `dotnet build` 通过，危险 using 扫描干净 | B | 来自课程记录；本次未重复运行外部工程构建 |
| `LootManager.cs` 静态可见 Equipment / Xp / Gold 分支均调用 `PlayScatterFlight()` | C | 本环境只读查看外部 Unity 工程脚本 |
| `DropItem.cs` 静态可见 `flightRoutine`、飞行期间关闭碰撞、落地恢复碰撞、出池时停旧协程并归零 | C | 本环境只读查看外部 Unity 工程脚本 |
| `GameInput.inputactions` 静态可见 `OpenBag` 绑定 `<Keyboard>/tab`，`InputReader.cs` 静态可见 `OnOpenBag` 事件 | C | 本环境只读查看输入配置和脚本 |
| `InventoryUIController.cs` 静态可见 `CanvasGroup` 背包开关、拖拽中拒绝关包、关包隐藏 Tooltip、`01-Run.unity` 中可见该引用接到 BagPanel CanvasGroup | C | 本环境只读查看脚本和场景 YAML |
| `LootEntry.level`、`Item` 构造函数等级钳制、`InventorySystem.DiscardToWorld()` 写回 `item.Level` 均静态可见 | C | 本环境只读查看外部 Unity 工程脚本 |
| `TargetRegistry.Clear()`、`LootChest.ResetRuntimeState()` 和 `GameSession.StartRun()` 中的调用静态可见 | C | 本环境只读查看外部 Unity 工程脚本 |
| `M_Ground_Quarantine_Lit.mat` 与 `.meta` 存在，材质使用 URP Lit Shader；`01-Run.unity` 中 Ground Renderer 引用该材质且 Cast / Receive Shadows 为 1 | C | 本环境只读查看材质、`.meta` 和场景 YAML |
| Unity Editor / Play Mode、Profiler 或 Player Build 的视觉、交互、性能和构建验证 | D | 当前环境未启动 Unity，未实测画面、输入、重开、阴影或 Build |

### 待补验证

- Play Mode 跑一局，确认装备、经验和金币散落都在落地后才能被拾取。
- 拖拽物品时连续按 Tab，确认背包不会关闭且 ghost / 预览格子不残留。
- 丢弃 Lv.2 / Lv.3 武器、芯片和收集品后重新拾取，确认等级、价值、Tooltip 和战斗倍率保持一致。
- 重开多局，确认 `TargetRegistry.Count`、宝箱场上计数、未开启宝箱列表和金币 / 经验 / 击杀数都从新局初始值开始。
- 在目标 Player Build 中确认 Tab 输入、中文 UI、Lit 材质、阴影和主菜单 / Run 风格一致。
- 使用 Profiler 观察散落协程、背包 Redraw、CanvasGroup 开关和阴影设置是否引入明显 GC Alloc 或帧率波动。

## 复盘

- 原来的理解：系统能玩之后，下一步自然是继续堆新机制。
- 实践后的结论：Demo 已经具备核心循环时，包装、稳定性和第一眼可读性更能提高交付质量。低风险高感知收益的改动，往往比新机制更适合冲刺期。
- 仍未理解：缺少当前环境亲自运行的 Play Mode、Player Build 和 Profiler 数据，不能把静态链路升级成真实性能或画面验收。

## 相关内容

- 前置：[主菜单与场景流](main-menu-and-scene-flow.md)
- 前置：[容器搜刮与宝箱系统](container-looting-and-chests.md)
- 前置：[合并升级收益兑现](merge-upgrade-reward-payoff.md)
- 前置：[物品图标与背包可读性](item-icons-and-backpack-readability.md)
- UGUI：[Canvas](../../unity/ugui/canvas.md)
- UGUI：[UGUI 总览](../../unity/ugui/index.md)
- C#：[C# 工程实践路线](../../csharp/engineering/index.md)
- 检查清单：[Unity 项目能力](../../checklists/unity-project.md)

> 标签：`Unity` `Demo 包装` `CanvasGroup` `Input System` `对象池` `static Reset` `URP Lit` `阴影` `项目实践`
