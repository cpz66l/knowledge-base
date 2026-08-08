# 主菜单与场景流

> 学习状态：项目中使用，待复测
>
> 验证状态：用户记录称已完成实测与代码验收；本次只读复核外部 Unity 工程脚本、场景 YAML、`.meta` 和 Build Settings，未运行 Unity Editor / Play Mode / Player Build。
>
> 前置知识：[物品图标与背包可读性](item-icons-and-backpack-readability.md)、[胜负结算与重开闭环](run-result-and-restart-loop.md)、[Canvas](../../unity/ugui/canvas.md)、[Button](../../unity/ugui/controls/button.md)
>
> 对应项目：[Backpack Survivor](index.md)
>
> 下一步：[场景氛围与演示包装](scene-atmosphere-and-demo-polish.md)
>
> 日期：2026-08-07
>
> 阶段：V0.2 掉落与背包构筑 · 第 32 课

## 学习目标

- 把项目从“直接进入 Run 测试场景”推进到“Build 启动有主菜单入口”。
- 用 `MainMenuController` 让开始游戏、退出程序和制作者声明面板各有明确职责。
- 让结算页从程序终点变成场景流节点：重开一局或返回主菜单。
- 用 Build Settings 固定 `MainMenu -> 01-Run` 的启动顺序，清理旧场景路径风险。
- 用 `CanvasScaler`、`ScrollRect` 和按钮事件订阅修复主菜单的分辨率适配和长文本阅读问题。

## 当前理解

第 32 课真正补的是 Demo 交付链路，而不是单纯多做一个 UI 页面。外部试玩者打开 Build 时，第一眼应该看到可理解的入口，而不是直接掉进开发期测试场景。

当前场景流是：

```text
Build 启动
  -> MainMenu
  -> 开始游戏
  -> 01-Run
  -> 胜利 / 失败结算
  -> 重开 01-Run 或返回 MainMenu
```

这节课也修正了课程优先级：原计划的“新手目标提示”后移，主菜单与场景闭环前置。原因是当前 Demo 已经通过宝箱距离、波次压力、掉落反馈和背包整理形成目标感，继续堆提示的收益低于补齐交付入口。

## 交付范围

| 模块 | 当前职责 |
|---|---|
| `MainMenu.unity` | Build 第 0 个场景，承载主菜单背景、开始、退出和制作者声明入口 |
| `MainMenuController` | 订阅按钮事件，开始游戏加载 `01-Run`，退出调用 `Application.Quit()`，声明面板开关显隐 |
| `ResultView` | 结算后重开 Run 或返回 MainMenu，切场景前恢复 `Time.timeScale = 1f` |
| `EditorBuildSettings.asset` | 固定 `MainMenu.unity` 在前、`01-Run.unity` 在后，替换旧 `Run1.unity` 路径 |
| `AboutPanel` | 默认隐藏，使用 Scroll View 承载制作者声明和 Demo 边界说明 |
| `CanvasScaler` | 使用 `Scale With Screen Size`、`1920x1080`、`Match 0.5` 适配常见横屏分辨率 |

## 最小示例

### MainMenuController

```csharp
private void OnEnable()
{
    if (startButton != null)
        startButton.onClick.AddListener(StartButton);
    if (quitButton != null)
        quitButton.onClick.AddListener(QuitButton);
    if (aboutButton != null)
        aboutButton.onClick.AddListener(AboutButton);
    if (closeAboutButton != null)
        closeAboutButton.onClick.AddListener(CloseAboutButton);
}

private void OnDisable()
{
    if (startButton != null)
        startButton.onClick.RemoveListener(StartButton);
    if (quitButton != null)
        quitButton.onClick.RemoveListener(QuitButton);
    if (aboutButton != null)
        aboutButton.onClick.RemoveListener(AboutButton);
    if (closeAboutButton != null)
        closeAboutButton.onClick.RemoveListener(CloseAboutButton);
}

private void StartButton()
{
    Time.timeScale = 1f;
    SceneManager.LoadScene("01-Run");
}

private void QuitButton() => Application.Quit();
private void AboutButton() => aboutPanel.SetActive(true);
private void CloseAboutButton() => aboutPanel.SetActive(false);
```

主菜单控制器只处理“按钮意图 -> 场景或面板动作”的映射，不管理局内状态。

### ResultView 返回主菜单

```csharp
private void HandleRestartClicked()
{
    Time.timeScale = 1f;
    SceneManager.LoadScene("01-Run");
}

private void HandleQuitClicked()
{
    Time.timeScale = 1f;
    SceneManager.LoadScene("MainMenu");
}
```

第 20 课原先的退出按钮是 `Application.Quit()`；第 32 课把它改成返回主菜单。当前外部工程中，重开也已在第 33 课后改为显式加载 `"01-Run"`，避免依赖 buildIndex。

### Build Settings

```text
0: Assets/BackpackSurvivor/Scenes/MainMenu/MainMenu.unity
1: Assets/BackpackSurvivor/Scenes/Run/01-Run.unity
```

Build Settings 是场景流的一部分，不能只看 Project 面板里有没有场景文件。旧 `Run1.unity` 路径残留会让 Build 启动或场景加载行为变得不可复现。

### CanvasScaler

```text
UI Scale Mode: Scale With Screen Size
Reference Resolution: 1920 x 1080
Screen Match Mode: Match Width Or Height
Match: 0.5
```

主菜单是全屏 UI，不能停留在 `Constant Pixel Size`。如果根 Canvas 不缩放，逐个调 RectTransform 只能临时遮住问题。

## 项目中的应用

### Demo 入口闭环

第 32 课后，Backpack Survivor 已具备可展示 Demo 的最小入口：主菜单启动、开始一局、结算后重开或返回主菜单。这个链路让项目从“编辑器测试工程”更接近“可交付试玩包”。

### 制作者声明放在低压力区

制作者声明不进入战斗 HUD，而是放在主菜单的 `AboutPanel`。这样玩家或面试官可以在开始前了解项目性质、当前版本内容、开发目标和素材使用边界，不打断战斗节奏。

### 按钮订阅保持镜像

按钮没有依赖 Inspector 常驻 OnClick 绑定，而是在 `OnEnable()` / `OnDisable()` 中用代码订阅与退订。这个习惯和项目里事件驱动 UI 的做法一致，也更容易在代码审阅中看到订阅边界。

## 常见错误

| 问题 | 根因 | 处理方式 |
|---|---|---|
| Build 启动进入旧场景 | Build Settings 残留旧路径或顺序错误 | 检查 `EditorBuildSettings.asset`，确认 MainMenu 为场景 0 |
| 下一场景继承暂停状态 | 结算或暂停后切场景前未恢复 `Time.timeScale` | 所有场景跳转入口先写 `Time.timeScale = 1f` |
| Button 漏引用时空引用 | 判空对象和实际使用对象不一致 | 判空必须判马上要使用的 Button / Panel |
| Scrollbar 拖不动 | Viewport、Content、Scrollbar 尺寸或引用没有形成 ScrollRect 三件套 | 先查 Viewport 可视面积、Content 高度和 ScrollRect 引用 |
| 主菜单在不同分辨率漂移 | CanvasScaler 仍是 `Constant Pixel Size` | 改为 `Scale With Screen Size` 并配合锚点组织 |
| 退出按钮在 Editor 中没反应 | `Application.Quit()` 在 Editor 中通常不退出 | Player Build 中复核，Editor 只能用日志确认按钮触发 |

## 如何验证

### 当前已记录证据

| 结论 | 证据等级 | 说明 |
|---|---|---|
| 用户记录已通过主菜单声明开关、开始游戏、结算重开、返回主菜单、再次开始游戏和多分辨率 UI 稳定性验收 | B | 来自用户放入 Inbox 的第 32 课课程记录 |
| 用户记录称 `dotnet build` 通过，危险 using 扫描干净 | B | 来自课程记录；本次未重复运行外部工程构建 |
| 外部工程静态可见 `MainMenuController.cs`，按钮订阅/退订镜像，Start 加载 `"01-Run"`，Quit 调 `Application.Quit()`，About 面板显隐 | C | 本环境只读查看外部 Unity 工程脚本 |
| `EditorBuildSettings.asset` 静态可见 MainMenu 为第 0 个场景，`01-Run` 为第 1 个场景，旧 `Run1.unity` 路径已不在列表中 | C | 本环境只读查看 ProjectSettings YAML |
| `MainMenu.unity` 静态可见 `MainMenuController` 挂载、`AboutPanel` 默认未激活、Scroll View / Viewport / Content / Vertical Scrollbar 引用存在 | C | 本环境只读查看场景 YAML |
| `MainMenu.unity` 静态可见 CanvasScaler 使用 `Scale With Screen Size`、参考分辨率 `1920x1080`、Match `0.5` | C | 本环境只读查看场景 YAML |
| `ResultView.cs` 静态可见返回主菜单前恢复 `Time.timeScale` 并加载 `"MainMenu"` | C | 本环境只读查看外部 Unity 工程脚本 |
| Unity Editor / Play Mode / Player Build 主菜单和 Build 行为验证 | D | 当前环境未启动 Unity，未实际点击按钮或打包运行 |

### 待补验证

- 在 Unity Play Mode 中实际点击开始、制作者声明、关闭声明、结算重开和返回主菜单。
- 在 Player Build 中复核 Build 首场景、退出按钮行为、场景名加载和中文声明文本显示。
- 在 16:9 以外比例下复核主菜单背景是否需要 Cover / 裁切策略。
- 补一条完整录像或截图作为作品集展示证据。

## 复盘

- 原来的理解：下一步应该继续补新手目标提示，让玩家更知道该做什么。
- 实践后的结论：Demo 冲刺期优先补交付链路。当前目标感已经能由宝箱距离、波次压力和背包整理自然提供，主菜单和结算回流更影响外部试玩的第一体验。
- 仍未理解：当前环境没有亲自跑 Player Build，不能确认目标平台下退出按钮、窗口分辨率和场景加载的最终表现。

## 相关内容

- 前置：[物品图标与背包可读性](item-icons-and-backpack-readability.md)
- 前置：[胜负结算与重开闭环](run-result-and-restart-loop.md)
- 后续：[场景氛围与演示包装](scene-atmosphere-and-demo-polish.md)
- 后续：[完整 15 分钟通关验收](full-run-acceptance.md)
- 后续：[Build 与演示包](build-and-demo-package.md)
- UGUI：[Canvas](../../unity/ugui/canvas.md)
- UGUI：[Button](../../unity/ugui/controls/button.md)
- UGUI：[Scrollbar](../../unity/ugui/controls/scrollbar.md)
- 检查清单：[Unity 项目能力](../../checklists/unity-project.md)

> 标签：`Unity` `MainMenu` `SceneManager` `Build Settings` `CanvasScaler` `ScrollRect` `Button` `项目实践`
