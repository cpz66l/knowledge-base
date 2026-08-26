# 本地存档与最高纪录

> 项目：《背包幸存者》Backpack Survivor  
> 模块周期：V0.3.10  
> 学习状态：项目复盘已整理  
> 证据归属：用户 `inbox/V0.3.10本地存档与最高纪录复盘.md` 复盘记录；用户记录重启保留、坏档兜底和 `dotnet build BackpackSurvivor/BackpackSurvivor.sln --no-restore` 通过，本环境未重复运行 Unity / dotnet build  
> 关键词：SaveData、SaveService、RunResult、MainMenuRecordView、JSON、本地存档、局外留存

## 学习目标

- 给 Demo 增加第一版局外留存，不再一局结束就完全清空成果。
- 区分战绩型存档和断点续玩，不把运行时状态保存范围做失控。
- 建立 `RunResult -> SaveService -> MainMenuRecordView` 的数据边界。

## 当前实现

V0.3.10 只记录“打过多少局、赢过多少局、胜利时带出了什么价值”，不保存局内断点状态。

当前字段：

```text
totalRuns
totalWins
bestBackpackValue
totalGold
legendaryFoundCount
legendaryCollectedValue
lastPlayedVersion
```

字段口径：

- `totalRuns`：开局次数，开始一局即记录。
- `totalWins`：胜利次数。
- `bestBackpackValue`：历史最高胜利背包价值。
- `totalGold`：胜利后带出的局外金币。
- `legendaryFoundCount`：胜利带出的传说成品数量。
- `legendaryCollectedValue`：胜利带出的传说成品累计价值。
- `lastPlayedVersion`：最后写入存档的版本号。

## 架构链路

```text
GameSession.StartRun()
        ↓
SaveService.RecordRunStarted()
        ↓
保存 totalRuns
```

```text
GameSession.EndRun()
        ↓
RunResult
  TotalGold / BackpackValue / LegendaryFoundCount / LegendaryCollectedValue
        ↓
SaveService.ApplyVictoryResult(result)
        ↓
JSON 保存到 Application.persistentDataPath
        ↓
MainMenuRecordView 读取展示
```

存档路径：

```text
Path.Combine(Application.persistentDataPath, "save_data.json")
```

读取失败或 JSON 损坏时，回退默认存档并覆盖坏档，避免坏档阻断游戏。

## 关键取舍

### 为什么做战绩存档，不做断点续玩

断点续玩需要保存玩家位置、敌人状态、掉落物、背包布局、波次进度、随机状态和大量运行时对象。当前 Demo 的目标是展示系统深度和工程完整度，因此战绩型存档成本低、收益高、容易验证。

### 为什么失败只记录开局数

当前口径是：失败证明玩家开过这一局；胜利才证明收益被带出。因此失败不累计金币、传说价值或最高背包价值，能让胜利在局外层面更有意义。

### 为什么传说物品按带出成品计数

字段语义是“胜利带出的传说成品数”，不是“历史摸到传说次数”。合成后数量减少是合理结果，价值通过 `legendaryCollectedValue` 体现。后续如果做图鉴，再新增 `legendaryPickedCount` 或 `legendaryDiscoveredIds`。

### 为什么 SaveService 不做纯静态类

`SaveService` 使用 `MonoBehaviour + static Instance + DontDestroyOnLoad`，保留 Unity 生命周期，便于跨场景保活、启动加载和后续调试。但跨场景服务必须挂在独立根物体上，不能挂在 Canvas 或业务大对象上。

## 踩坑与修正

- `LoadOrCreate()` 初版没有给 `CurrentData` 赋默认值，修正为无文件或读取失败时创建默认存档。
- `SaveService` 初版挂在 MainMenu 的 Canvas 上，`DontDestroyOnLoad(gameObject)` 把主菜单 UI 带进 Run 场景；修正为独立根物体承载。
- 直接运行 Run 场景没有存档服务时可能空引用，修正为空安全调用。
- `MainMenuRecordView` 按钮音和 TMP 文本引用缺失时可能空引用，补空判断。
- 设置 / 纪录弹窗打开后后方按钮仍可点，修正为添加全屏遮罩阻挡点击穿透。

## 验收记录

用户复盘记录覆盖：

- 主菜单显示总开局、胜利次数、最高背包价值、局外金币、传说带出数和传说累计价值。
- 开始一局后 `totalRuns` 增加并写入 JSON。
- 失败不增加胜利和带出收益字段。
- 胜利后累计胜场、金币、最高背包价值和传说统计。
- 停止播放或关闭后重新进入，主菜单仍可读取存档。
- JSON 损坏或读取失败时不会阻断游戏，会回退默认存档。
- `SaveService` 移出 UI 根物体后，MainMenu 面板不会跟进 Run 场景。
- 设置 / 纪录弹窗遮罩阻止后方点击穿透。
- 用户记录 `dotnet build BackpackSurvivor/BackpackSurvivor.sln --no-restore` 通过，0 error。
- 危险 `using` 扫描干净。

本环境只整理复盘和知识页，没有重复运行 Unity 或 dotnet build。

## 面试表达

```text
我为项目补了一套本地战绩存档系统，没有选择高成本的断点续玩，而是先做局外留存记录。SaveData 承载数据，SaveService 作为跨场景服务负责 JSON 读写，路径使用 Application.persistentDataPath。GameSession 在开局时记录总局数，在胜利结算时把金币、最高背包价值和传说物品带出数据写入存档。主菜单通过 MainMenuRecordView 只读展示。这个模块还处理了坏档兜底、跨场景单例挂载边界和弹窗点击穿透问题。
```

## 风险与下一步

- 当前存档没有正式迁移系统；字段结构变化时需要 `saveVersion` 和迁移逻辑。
- `JsonUtility` 适合简单数据，复杂字典 / 列表 / 图鉴可能需要 DTO 或换 JSON 库。
- Demo 阶段不做加密和防篡改，玩家可以手改 JSON。
- 如果忘挂 `SaveService`，空安全能防崩但不会记录数据，发布前仍要检查服务入口。
- 局外金币目前只累计展示，还没有消费出口。
- 下一步进入[V0.3 Release 文案与发布验收](v0.3-release-notes.md)。

> 标签：`Backpack Survivor` `本地存档` `JSON` `SaveService` `局外留存`

