# Build 与演示包

> 学习状态：项目中使用，待复测
>
> 验证状态：用户记录称已完成正式 Windows 演示包独立运行验收；本次只读复核外部 Unity 工程 Build Profile、Player Settings、场景顺序、输入资产引用、Build 输出和 `.meta` 状态，未运行 exe。
>
> 前置知识：[Profiler 快扫与低风险优化](profiler-sweep-and-low-risk-optimization.md)、[主菜单与场景流](main-menu-and-scene-flow.md)、[胜负结算与重开闭环](run-result-and-restart-loop.md)
>
> 对应项目：[Backpack Survivor](index.md)
>
> 下一步：V0.3 已推进到内容池、音频和设置系统；作品材料整理继续作为求职展示支线推进
>
> 日期：2026-08-08
>
> 阶段：V0.2 掉落与背包构筑 · 第 36 课

## 学习目标

- 把项目从 Unity Editor 内可玩推进到正式 Windows 包可独立运行。
- 用 Build Profile、Player Settings 和场景顺序固定演示包交付条件。
- 区分 UI Input Module 的默认 UI actions 与玩家战斗输入 `GameInput`。
- 记录 Build 输出、版本号、窗口配置和已知非阻断风险。
- 明确 Build 产物不进入 Git，正式知识只记录配置、验证和交付路径。

## 当前理解

第 36 课的关键不是“点一次 Build 按钮”，而是建立交付边界：正式包关闭开发开关，目标分辨率和窗口模式可演示，场景从主菜单开始，输入资产引用有效，Build 输出能离开 Editor 独立运行。

当前交付链路是：

```text
Build Profile / Player Settings / EditorBuildSettings
  -> Windows Build 输出目录
  -> 独立 exe 启动
  -> MainMenu
  -> Run
  -> Result
  -> Restart / MainMenu
  -> 进入作品材料整理 / V0.3 内容、反馈和设置扩展
```

## 交付范围

| 模块 | 当前职责 |
|---|---|
| `Assets/Settings/Build Profiles/Windows.asset` | 正式 Windows Build Profile，关闭开发调试选项 |
| `ProjectSettings.asset` | 设置演示分辨率、窗口模式、版本号和输入后端 |
| `EditorBuildSettings.asset` | 固定 `MainMenu -> 01-Run` 场景顺序 |
| `InputSystemUIInputModule` | 使用 `InputSystem_Actions` 处理 UI 导航 / 点击 |
| `PlayerInput` | 使用 `GameInput.inputactions / PlayerNormal` 处理玩家战斗输入 |
| `Builds/BackpackSurvivor_v0.2_Windows/` | 外部项目的本地 Build 输出目录，不进入知识库 Git |

## 最小示例

### 正式包关闭开发选项

```yaml
m_Development: 0
m_ConnectProfiler: 0
m_BuildWithDeepProfilingSupport: 0
m_AllowDebugging: 0
m_WaitForManagedDebugger: 0
```

这些选项决定当前包是演示包，而不是 Profiler/调试用开发包。

### 演示窗口配置

```yaml
defaultScreenWidth: 1600
defaultScreenHeight: 900
resizableWindow: 1
fullscreenMode: 3
bundleVersion: 0.2.0
activeInputHandler: 1
```

`1600 x 900 + Windowed + Resizable` 适合录屏、面试演示和普通玩家试玩。

### 场景顺序

```text
0: Assets/BackpackSurvivor/Scenes/MainMenu/MainMenu.unity
1: Assets/BackpackSurvivor/Scenes/Run/01-Run.unity
```

Build 的首场景应该是主菜单，而不是开发期 Run 测试场景。

### 输入资产职责拆分

```text
MainMenu / EventSystem / InputSystemUIInputModule -> InputSystem_Actions
01-Run / EventSystem / InputSystemUIInputModule -> InputSystem_Actions
01-Run / PlayerInput -> GameInput.inputactions / PlayerNormal
```

UI 模块使用模板 UI actions，不代表玩家战斗输入被替换。移动、射击、交互、旋转、暂停和 Tab 背包仍由 `GameInput` 管理。

## 项目中的应用

### 第一个可交付演示包

用户记录中的 Windows 输出为：

```text
E:\YouXiKaiFa\Backpack Survivor\Builds\BackpackSurvivor_v0.2_Windows\
E:\YouXiKaiFa\Backpack Survivor\Builds\BackpackSurvivor_v0.2_Windows_20260808-203936.zip
```

本次静态检查可见外部 Build 目录和约 `64.9 MB` 的 zip 文件存在；当前环境没有运行 exe，因此只记录为静态存在证据。

### 非阻断风险降级

课程记录提到 `DefaultVolumeProfile.asset` 中仍有 Missing/Test Volume 组件。用户记录称当前 Build 没受影响，因此第 36 课把它降级为已知非阻断风险，留到后续视觉/后处理整理，而不是在 Demo 冻结期引入新变量。

### 交付清洁度

用户记录称已清理 `InventorySystem` 经验日志和 `DropItem` 背包满日志。本次静态扫描仍可见 `ObjectPool` 的警告/错误日志以及 `PickupLogger` 临时日志；它们是否保留需要按后续发布策略继续确认。

## 常见错误

| 问题 | 根因 | 处理方式 |
|---|---|---|
| Build 启动直接进 Run | 场景顺序没有固定 MainMenu 为第 0 个场景 | 检查 `EditorBuildSettings.asset` |
| 正式包仍连 Profiler | Development / Connect Profiler 开关未关 | Build Profile 中关闭开发调试选项 |
| UI 可点击但玩家不能动，或反过来 | UI InputModule 和 PlayerInput 的 actions 资产混淆 | 分别检查 `InputSystem_Actions` 与 `GameInput / PlayerNormal` |
| Editor 能跑，exe 颜色异常 | 默认材质或 Shader 链路在 Build 中不稳定 | 显式材质资产 + Prefab 引用 + MPB |
| 把 Build 输出提交进仓库 | 没有区分源码和构建产物 | `[Bb]uilds/` 或项目构建目录保持忽略 |
| Missing 组件一律阻断交付 | 没区分阻断风险和后续清理项 | 若 Build 验收不受影响，可记录为已知非阻断风险 |

## 如何验证

### 当前已记录证据

| 结论 | 证据等级 | 说明 |
|---|---|---|
| 用户记录正式 Windows exe 独立运行验收通过 | B | 来自用户放入 Inbox 的第 36 课课程记录 |
| 用户记录 MainMenu、玩法说明、Run、背包、武器激活、颜色、结算、Restart 和返回 MainMenu 均在正式包中验收 | B | 来自用户放入 Inbox 的第 36 课课程记录 |
| 外部 Unity 工程 Windows Build Profile 静态可见开发调试选项均为 `0` | C | 本环境只读查看 `Windows.asset` |
| `ProjectSettings.asset` 静态可见 `1600 x 900`、可调整窗口、版本 `0.2.0` 和 `activeInputHandler: 1` | C | 本环境只读查看 Project Settings |
| `EditorBuildSettings.asset` 静态可见 MainMenu 在前、`01-Run` 在后 | C | 本环境只读查看场景顺序 |
| MainMenu 与 Run 的 `InputSystemUIInputModule` 静态可见引用 `InputSystem_Actions`，Run 的 `PlayerInput` 静态可见引用 `GameInput / PlayerNormal` | C | 本环境只读查看场景 YAML 和 inputactions `.meta` |
| 外部 Build 目录和 zip 文件静态存在 | C | 本环境只读查看 `E:\YouXiKaiFa\Backpack Survivor\Builds` |
| `Assets/BackpackSurvivor` 下本次静态抽查未发现缺失 `.meta` 的普通文件 | C | 本环境只读扫描外部 Unity 工程资产目录 |
| 当前环境亲自运行正式 exe 或 Unity Player | D | 当前环境未运行 exe，未验证真实窗口、输入、音画或退出行为 |

### 待补验证

- 准备演示视频、截图、README、操作说明和作品集讲解稿；V0.3 后续继续检查新增构筑物品投放节奏。
- 复核 `PickupLogger` 是否仍属于临时脚本，发布材料前决定保留、禁用或移除。
- 后续视觉整理时清理 Missing/Test Volume 组件，避免项目审阅时产生噪音。
- 如果要投递或分享 zip，补版本变更说明和已知问题列表。

## 复盘

- 原来的理解：Unity Editor 中完整跑通就可以算项目完成。
- 实践后的结论：可交付 Demo 必须能脱离 Editor 独立运行，且 Build 配置、输入资产、窗口、版本、忽略规则和已知风险都要能解释。
- 仍未理解：当前环境没有亲自运行 exe，不能把用户正式包验收记录升级为当前模型的运行验证。

## 相关内容

- 前置：[Profiler 快扫与低风险优化](profiler-sweep-and-low-risk-optimization.md)
- 前置：[主菜单与场景流](main-menu-and-scene-flow.md)
- 前置：[胜负结算与重开闭环](run-result-and-restart-loop.md)
- 记录：[Bug 记录簿](bug-log.md)
- 记录：[性能优化记录](performance-optimization-log.md)
- 检查清单：[Unity 项目能力](../../checklists/unity-project.md)

> 标签：`Unity` `Build` `Windows` `Player Settings` `Input System` `Demo 交付` `项目实践`
