# 基础音频系统与 BGM

> 项目：《背包幸存者》Backpack Survivor  
> 模块周期：V0.3.5  
> 学习状态：项目复盘已整理  
> 证据归属：用户 `inbox/V0.3.5基础音频系统与BGM复盘.md` 复盘记录；用户记录实机测试“效果非常不错”，本环境未运行 Unity Editor / Play Mode / Player Build  
> 关键词：SfxPlayer、AudioCue、WeaponSfxId、BGM、UI 音效、跨场景点击音

## 学习目标

- 从“零散播放声音”升级为可扩展的音频反馈系统。
- 区分高频武器射击音效、通用短音效和 BGM 的播放链路。
- 记录 UI 点击跨场景播放时“反馈完整”和“入口可靠性”的取舍。

## 当前实现

V0.3.5 建立了基础音频链路，让射击、拾取、背包操作、升级、胜负和场景氛围都有声音反馈。

本次接入内容：

- 手枪、步枪、霰弹枪三类武器射击音效。
- 武器音效冷却、音量、pitch 随机、多 clip 随机。
- `SfxId / WeaponSfxId + Cue 表` 结构。
- 拾取、升级、背包开关、拖放、合成、宝箱、传说物、胜负和 UI 点击音效。
- 主菜单 BGM 与 Run 场景 BGM。
- 开始游戏按钮跨场景点击音，避免为了听完音效拖慢场景切换。

## 架构链路

### 武器射击

```text
AutoWeapon / ActiveWeapon
        ↓
WeaponBase.Fire()
        ↓
SfxPlayer.PlayWeaponShoot(WeaponSfxId)
        ↓
WeaponAudioCue：clip / volume / pitch / cooldown
        ↓
AudioSource.PlayOneShot
```

射击是最高频音效，和普通短音效相比更需要冷却、随机 pitch、clip 随机和武器类型差异。

### 通用短音效

```text
GameSession / InventorySystem / InventoryUIController / ResultView / LootChest
        ↓
SfxPlayer.PlaySfx(SfxId)
        ↓
AudioCue：clip / volume / pitch / cooldown
        ↓
AudioSource.PlayOneShot
```

调用方只表达事件语义，例如金币拾取、合成成功、背包打开、游戏失败。Clip、音量、随机和冷却放在 cue 配置里。

### BGM

```text
Scene AudioSource
        ↓
Music clip
        ↓
Play On Awake + Loop
```

当前 BGM 使用场景内独立 `AudioSource`，不复用 SFX 的 source。原因是 `SfxPlayer` 播短音效时会临时改 pitch，若与 BGM 共用 source，音乐可能被 pitch 变化污染。

### 跨场景 UI 点击音

```text
MainMenu StartButton
        ↓
PlayButtonClickAcrossScene
        ↓
临时 AudioSource + DontDestroyOnLoad
        ↓
立即 LoadScene("01-Run")
        ↓
音效播完自动销毁
```

开始游戏是核心入口，可靠性优先级高于点击音完整播放。最终方案保留听觉反馈，同时立即加载 Run 场景。

## 关键取舍

### 为什么不用每个脚本自己持有 AudioSource

短音效是表现反馈，不应该让每个玩法脚本都直接管理 clip、source、音量和冷却。集中到 `SfxPlayer` 后，后续换资源、调音量或加随机只影响音频服务和配置。

### 为什么射击音效单独用 WeaponSfxId

武器类型是构筑识别的一部分。如果所有武器都只播同一个 `Shoot`，玩家听觉上感知不到手枪、步枪和霰弹枪的差异。分型音效能增强武器身份感。

### 为什么音效触发点放在成功发生后

音效会建立玩家对规则的预期。装备拾取音放在 `Grid.Place` 成功后，金币音放在金币结算后，升级确认音放在属性真正 `Apply` 后，避免“尝试失败但播成功音”的误导。

### 为什么 AdjacencyActivated 暂不接

邻接效果依赖背包重绘和布局扫描。如果直接在 `Redraw()` 播音，拖拽、刷新和补画都可能造成重复触发。正确做法是先记录上一次有效邻接签名，只在新增有效效果时播放；本模块先挂账。

## 验证记录

用户复盘记录已完成实机测试，重点覆盖：

- 三类武器射击音色可区分。
- 后期多武器开火没有明显听觉疲劳。
- 金币、经验、物品、传说物拾取音效正常。
- 背包打开 / 关闭、拖拽放下、合成成功音效正常。
- 升级出现、升级确认、宝箱打开、受伤、胜利、失败音效正常。
- 主菜单和 Run 场景 BGM 正常播放。
- 开始游戏点击后能稳定进入 Run 场景。
- UI 点击音在主菜单和结算页都能听到。
- `AdjacencyActivated` 未强行接入，避免刷新 spam。
- 危险 `using` 扫描干净。

本环境只整理复盘和知识页，没有运行 Unity、Profiler 或 Player Build。

## 面试表达

可以这样讲：

```text
V0.3.5 我把音频从零散字段升级成 SfxId / WeaponSfxId 加 Cue 表。玩法脚本只表达发生了什么，SfxPlayer 负责 clip、音量、pitch 随机和冷却。射击音效单独分型，因为它高频且和武器身份绑定；BGM 使用独立 AudioSource，避免被 SFX 的 pitch 修改污染。开始游戏按钮用跨场景一次性音源播点击音，同时立即切场景，保证入口可靠。
```

## 风险与下一步

- 当前 BGM 还不是完整 `AudioManager`，尚无 AudioMixer、淡入淡出、优先级和最大并发控制。
- 高频声音后续还可继续用 AudioMixer、优先级、最大并发数和资源预加载做防噪。
- `AdjacencyActivated` 需要状态差异检测后再接音效。
- 下一模块进入[设置菜单与基础选项](settings-menu-and-basic-options.md)，把音量设置接入 SFX / BGM。

> 标签：`Backpack Survivor` `Unity Audio` `SfxPlayer` `BGM` `项目复盘`

