# 设置菜单与基础选项

> 项目：《背包幸存者》Backpack Survivor  
> 模块周期：V0.3.6  
> 学习状态：项目复盘已整理  
> 证据归属：用户 `inbox/V0.3.6设置菜单与基础选项复盘.md` 复盘记录；用户记录 `dotnet build BackpackSurvivor/BackpackSurvivor.sln --no-restore` 通过且实机验收设置生效，本环境未重复运行 Unity / dotnet build  
> 关键词：GameSettings、SettingsService、SettingsPanelView、PlayerPrefs、SFX 音量、BGM 音量、分辨率设置

## 学习目标

- 把 Demo 的基础设置能力从 UI 控件扩展为“数据、持久化、应用、消费侧响应”的完整链路。
- 区分设置面板表现层、设置服务层和音频 / 屏幕消费侧。
- 记录 `PlayerPrefs`、音量倍率、分辨率和窗口模式的第一版边界。

## 当前实现

V0.3.6 在主菜单新增设置入口，让玩家能调整声音和屏幕表现，并让设置跨场景、跨重启保持。

本次实现覆盖：

- `GameSettings` 设置快照。
- `SettingsService` 统一 `Load / Save / Apply / ResetToDefault`。
- `PlayerPrefs` 持久化。
- `SettingsPanelView` 映射 Slider / Dropdown。
- Master / SFX / Music 音量。
- 分辨率和窗口模式。
- SFX、BGM 和跨场景按钮音消费设置。

## 架构链路

### 设置数据

```text
GameSettings
  masterVolume
  sfxVolume
  musicVolume
  resolutionWidth
  resolutionHeight
  fullscreenMode
```

`GameSettings` 是普通数据类，不继承 `MonoBehaviour`，只表达当前设置快照。默认值由 `GameSettings.CreateDefault()` 集中提供。

### 设置服务

```text
SettingsService.Load()
SettingsService.Save(settings)
SettingsService.Apply(settings)
SettingsService.ResetToDefault()
SettingsService.GetEffectiveSfxVolume(settings)
SettingsService.GetEffectiveMusicVolume(settings)
```

`PlayerPrefs` 的 key 集中在 `SettingsService` 内，避免其它脚本散落硬编码字符串。

音量计算为：

```text
有效 SFX 音量 = Master x SFX
有效 Music 音量 = Master x Music
```

### 设置通知

```text
SettingsService.Apply(settings)
        ↓
SettingsService.Applied(settings)
        ↓
SfxPlayer / MusicVolumeApplier 自己响应
```

`SettingsPanelView` 不直接修改 `AudioSource.volume`，而是提交设置；真正使用设置的是音频系统和屏幕系统。

### 设置面板

```text
Open：Load 设置，刷新 UI，显示面板
Apply：Save + Apply 当前设置
Reset：恢复默认，保存并应用，再刷新 UI
Close：关闭面板，丢弃未 Apply 的修改
```

Dropdown 保存的是索引，因此 `SettingsPanelView` 维护分辨率选项列表，再在索引和 `width / height` 之间转换。

## 关键取舍

### 为什么第一版使用 PlayerPrefs

设置数据体量小、结构稳定、暂时没有复杂版本迁移需求。`PlayerPrefs` 成本低，适合 Demo 的音量和分辨率设置。后续如果做完整存档，再考虑统一 `SaveService` 或 JSON。

### 为什么不上 AudioMixer

`AudioMixer` 更适合完整音频工程，但 V0.3.6 的目标是让音量设置真实可用。现阶段使用倍率乘法更轻，也不会打断已有 `SfxPlayer` cue 表结构。

### 为什么 UI 不直接控制音频系统

设置面板属于表现层，只应该收集玩家选择并提交设置。`SfxPlayer` 和 `MusicVolumeApplier` 自己订阅和应用设置，后续暂停菜单、结算页设置入口或更多设置项才能复用同一链路。

### 为什么不新增 SettingsBootstrap

当前已有 `SfxPlayer.Awake()` 自读设置、`MusicVolumeApplier.Awake()` 自读设置和 `MainMenuController.Awake()` 应用屏幕设置。已有链路能覆盖 MainMenu 到 Run 的实际流程时，不为了“架构看起来完整”额外加层。

## 踩坑与修正

- `GameSettings` 初版误继承 `MonoBehaviour`，已改为普通数据类。
- 默认分辨率曾写反为 `1080 x 1920`，已修正为 `1920 x 1080`。
- `Load()` 初版曾把 `MusicVolumeKey` 读入 `masterVolume`，已修正为 `musicVolume`。
- `Save()` 初版曾重复 clamp `masterVolume`，漏掉 `musicVolume`，已修正。
- 曾同时存在 `SettingService.cs` 和 `SettingsService.cs`，已清理为唯一 `SettingsService.cs`。
- `MainMenuController` 曾混入 `using static Unity.VisualScripting.Member;`，已删除。
- 跨场景开始按钮音初版绕过设置音量，已接入 `GetEffectiveSfxVolume()`。

## 验收记录

用户复盘记录的验收项：

- 主菜单能打开 Settings 面板。
- Slider 能显示并修改 Master / SFX / Music 音量。
- Dropdown 能显示分辨率和窗口模式。
- 分辨率候选池支持常见分辨率和当前显示器原生分辨率，并去重。
- Apply 后设置保存并立即应用。
- Reset 后设置恢复默认，UI 同步刷新。
- Master 拉到 0 时，SFX 和 BGM 都静音。
- SFX 拉到 0 时，按钮、射击、拾取等短音效静音，BGM 保留。
- Music 拉到 0 时，BGM 静音，短音效保留。
- MainMenu 与 Run 场景 BGM 都吃设置倍率。
- 开始游戏跨场景按钮音也吃 SFX 设置倍率。
- 用户记录 `dotnet build BackpackSurvivor/BackpackSurvivor.sln --no-restore` 通过，0 error。
- 危险 `using` 扫描通过。

本环境只整理复盘和知识页，没有重复运行 Unity 或 `dotnet build`。

## 面试表达

可以这样讲：

```text
我没有把设置逻辑直接写在主菜单 UI 里，而是拆成 GameSettings 数据快照、SettingsService 持久化服务、SettingsPanelView 表现层，以及 SfxPlayer / MusicVolumeApplier 消费侧。设置面板只提交配置，音频和屏幕系统自己响应配置变化。这个结构后续可以复用到暂停菜单、Result 设置入口和更多选项。
```

这段的重点不是“做了几个 Slider”，而是 UI、持久化、应用和消费侧响应的边界清楚。

## 风险与下一步

- 当前设置面板只在主菜单存在，Run 中还没有暂停菜单设置入口。
- 当前没有 `AudioMixer`，未来增加混响、ducking、分组压缩、淡入淡出时再升级。
- 分辨率系统暂不处理刷新率、多显示器和独占全屏。
- `SettingsPanelView` 通过 `MainMenuController` 播按钮音，有轻微 UI 耦合；复用到 Run 时应改为直接调用 `SfxPlayer` 或统一 UI 音效入口。
- 用户复盘提示外部项目存在 `Assets/_Recovery/`，提交前需要清理或忽略，避免误提交。
- 下一模块建议进入 V0.3.7 敌人寻路与群体移动优化。

> 标签：`Backpack Survivor` `设置菜单` `PlayerPrefs` `Unity Audio` `项目复盘`

