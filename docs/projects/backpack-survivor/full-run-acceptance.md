# 完整 15 分钟通关验收

> 学习状态：项目中使用，待复测
>
> 验证状态：用户记录称已完成完整链路试玩、外部试玩反馈和基础构建检查；本次只读复核外部 Unity 工程脚本与场景 YAML，未运行 Unity Editor / Play Mode / Profiler / Player Build。
>
> 前置知识：[场景氛围与演示包装](scene-atmosphere-and-demo-polish.md)、[主菜单与场景流](main-menu-and-scene-flow.md)、[背包武器激活](backpack-weapon-activation.md)、[旋转邻接方向修正](rotation-adjacency-direction-fix.md)
>
> 对应项目：[Backpack Survivor](index.md)
>
> 下一步：[Profiler 快扫与低风险优化](profiler-sweep-and-low-risk-optimization.md)
>
> 日期：2026-08-08
>
> 阶段：V0.2 掉落与背包构筑 · 第 34 课

## 学习目标

- 把 V0.2 Demo 当成外部玩家会真实试玩的版本，而不是只按功能清单逐项验收。
- 检查 `MainMenu -> Run -> Result -> Restart / MainMenu` 的完整游戏链路。
- 从外部试玩反馈中识别“系统已经存在，但玩家不知道如何进入”的理解门槛。
- 修正主动射击中鼠标地面点、枪口高度和角色朝向不一致的问题。
- 判断当前 Demo 是否适合冻结功能并进入 Profiler 与 Build 交付阶段。

## 当前理解

第 34 课的重点不是开新系统，而是把已有系统串成玩家视角的一局：玩家从主菜单进入、读懂玩法说明、战斗、整理背包、利用邻接构筑、经历胜负结算，再选择重开或返回主菜单。

当前完整链路是：

```text
MainMenu
  -> 玩法说明 / 制作者声明
  -> Start -> 01-Run
  -> 移动、瞄准、主动射击、自动武器
  -> 波次、精英敌人、宝箱压力
  -> 掉落、拾取、背包整理、合并、邻接、武器激活
  -> 升级三选一、金币、背包价值
  -> 胜利 / 失败结算
  -> Restart / 返回 MainMenu / 再开始
```

这节课的有效信号不是“所有玩家都能无脑通关”，而是玩家已经能因为构筑选择、背包整理和终局压力产生可复盘的失败故事。

## 交付范围

| 模块 | 当前职责 |
|---|---|
| `MainMenuController` | 增加玩法说明按钮与面板，保留制作者声明和开始 / 退出入口 |
| `GameplayGuidePanel` | 在开局前解释武器入包、左上优先级、灰边 / 金边、双持和芯片邻接 |
| `InputReader.TryGetMousePointOnPlane(float y, out Vector3 point)` | 按指定高度平面取鼠标射线交点，避免只有地面点一种语义 |
| `ActiveWeapon` | 按枪口高度平面取得主动射击方向 |
| `PlayerController` | 按角色身体高度平面取得转向目标 |
| `GameSession / ResultView` | 保持胜负结算、重开和返回主菜单链路闭合 |

## 最小示例

### 主菜单玩法说明入口

```csharp
[SerializeField] private Button gameplayGuideButton;
[SerializeField] private GameObject gameplayGuidePanel;
[SerializeField] private Button closeGuideButton;
```

玩法说明放在主菜单，而不是战斗 HUD。原因是它解决的是开局前理解门槛，不应该在战斗中持续抢屏。

### 按高度取鼠标平面交点

```csharp
public bool TryGetMousePointOnPlane(float y, out Vector3 point)
{
    point = default;

    if (mainCam == null)
        return false;

    Ray ray = mainCam.ScreenPointToRay(mouseVector2);
    Plane plane = new Plane(Vector3.up, new Vector3(0f, y, 0f));

    if (!plane.Raycast(ray, out float enter))
        return false;

    point = ray.GetPoint(enter);
    return true;
}
```

等距相机下，同一屏幕点打到 `y = 0` 地面和打到枪口高度平面，得到的 XZ 位置不同。主动武器和角色朝向需要按各自高度解释鼠标位置。

### 主动武器按枪口高度瞄准

```csharp
if (!ir.TryGetMousePointOnPlane(firePoint.position.y, out Vector3 aimPoint))
    return;

Vector3 direction = aimPoint - firePoint.position;
direction.y = 0f;
```

这比“先取地面点再把 y 清零”更符合枪口出弹的视觉语义。

## 项目中的应用

### 外部试玩暴露的是理解门槛

外部试玩者不清楚的重点不是“怎么移动”，而是背包构筑规则：武器必须放进背包才会自动攻击，左上位置决定激活优先级，灰色接边代表可连接，金色接边代表已生效，双持和芯片邻接是当前 Demo 的主要构筑深度。

这说明系统深度已经存在，但入口提示不足。因此第 34 课优先补玩法说明，而不是继续堆新机制。

### 高价值失败局比无脑通关更有意义

用户记录中出现了一局约 `4000￥` 的失败：玩家在最后阶段贪心整理背包，被敌人偷袭死亡。这类失败很有价值，因为它证明玩家已经在权衡战斗压力和背包收益，而不是只被系统错误打断。

### Demo 冻结点

第 34 课收官时，当前没有记录到阻断级断点。更合理的下一步不是再开功能，而是做 Profiler 快扫、Build 验证和演示包整理。

## 常见错误

| 问题 | 根因 | 处理方式 |
|---|---|---|
| 玩家不知道武器为什么没生效 | 背包武器激活规则只在系统里存在，没有进入玩家认知 | 主菜单玩法说明先解释“武器入包才自动攻击”和左上优先级 |
| 灰边 / 金边无法理解 | UI 表现没有对应规则说明 | 用玩法说明解释“灰边可连接，金边已生效” |
| 主动射击视觉方向偏移 | 鼠标地面交点被拿来驱动枪口高度弹道 | 用 `TryGetMousePointOnPlane(firePoint.position.y, ...)` |
| 玩家不复盘失败原因 | 失败来自不可理解 Bug 或纯数值碾压 | 保持压力曲线、构筑收益和提示入口，使失败能被解释 |
| 验收只看功能清单 | 忽略外部玩家能否理解系统 | 用外部试玩反馈检查规则入口、UI 语言和结算回流 |

## 如何验证

### 当前已记录证据

| 结论 | 证据等级 | 说明 |
|---|---|---|
| 用户记录已完成 V0.2 全链路验收，并记录外部试玩理解门槛 | B | 来自用户放入 Inbox 的第 34 课课程记录 |
| 用户记录称主动瞄准高度错层已修复，玩法说明面板已加入主菜单 | B | 来自用户放入 Inbox 的第 34 课课程记录 |
| 外部 Unity 工程静态可见 `MainMenuController` 新增 `gameplayGuideButton`、`gameplayGuidePanel`、`closeGuideButton` 和 `preloadTexts` | C | 本环境只读查看外部 Unity 工程脚本 |
| 外部 Unity 工程静态可见 `InputReader.TryGetMousePointOnPlane(float y, out Vector3 point)` | C | 本环境只读查看外部 Unity 工程脚本 |
| 外部 Unity 工程静态可见 `ActiveWeapon` 使用 `firePoint.position.y`，`PlayerController` 使用 `bodyPivot.position.y` | C | 本环境只读查看外部 Unity 工程脚本 |
| Unity Editor / Play Mode / Player Build 中的完整 15 分钟复测 | D | 当前环境未启动 Unity，未亲自跑一局 |

### 待补验证

- 录制一条完整 15 分钟试玩或通关 / 失败片段，用作作品集素材。
- 再找一位外部试玩者，确认玩法说明是否能显著降低背包规则误解。
- 在 Player Build 中复核主动射击方向、角色朝向和鼠标位置是否仍一致。
- 为背包武器激活、双持、攻击芯片和金色接边补少量可重复样本。

## 复盘

- 原来的理解：功能做完以后，主要验收点是自己能否顺利跑完整局。
- 实践后的结论：Demo 进入交付期后，外部玩家能不能理解系统更重要；解释入口、失败故事和结算回流都是验收内容。
- 仍未理解：当前环境没有亲自运行 Unity 和 Player Build，不能把用户试玩记录升级成当前模型的运行验证。

## 相关内容

- 前置：[场景氛围与演示包装](scene-atmosphere-and-demo-polish.md)
- 前置：[主菜单与场景流](main-menu-and-scene-flow.md)
- 系统：[背包武器激活](backpack-weapon-activation.md)
- 系统：[旋转邻接方向修正](rotation-adjacency-direction-fix.md)
- 后续：[Profiler 快扫与低风险优化](profiler-sweep-and-low-risk-optimization.md)
- 记录：[Bug 记录簿](bug-log.md)

> 标签：`Unity` `Demo 验收` `外部试玩` `主动瞄准` `MainMenu` `背包构筑` `项目实践`
