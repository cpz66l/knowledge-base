# Profiler 快扫与低风险优化

> 学习状态：项目中使用，待复测
>
> 验证状态：用户记录称已完成 Profiler 快扫、Build 试玩和 BUG-025 修复；本次只读复核外部项目证据包、脚本、Prefab、材质引用和忽略规则，未运行 Unity Editor / Profiler / Player Build。
>
> 前置知识：[完整 15 分钟通关验收](full-run-acceptance.md)、[刷怪器与对象池](spawner-and-object-pooling.md)、[战斗反馈快包](combat-feedback-pack.md)、[优化小 Tips](../../performance/perf-tips.md)
>
> 对应项目：[Backpack Survivor](index.md)
>
> 下一步：[Build 与演示包](build-and-demo-package.md)
>
> 日期：2026-08-08
>
> 阶段：V0.2 掉落与背包构筑 · 第 35 课

## 学习目标

- 用 Profiler 快扫判断卡顿嫌疑来自游戏逻辑、资源加载、Editor，还是 Profiler 观察本身。
- 区分 Editor/Playmode 尖刺和 Player Build 真实体验，避免为错误瓶颈做大重构。
- 为 Demo 打包前留下轻量证据链：截图、结论、Build 试玩反馈和后续挂账。
- 修复 Build 中暴露的子弹 / 装备掉落物颜色异常。
- 明确大体积 Profiler 原始捕获不进入作品集仓库。

## 当前理解

第 35 课的核心不是“看到尖刺就优化”，而是判断尖刺是否属于要处理的运行时瓶颈。

本次证据链是：

```text
Editor 里感觉后期会顿
  -> Profiler 截图显示 Render Thread / Loading / EditorLoop 尖刺
  -> Timeline / Hierarchy 区分 PlayerLoop、EditorLoop、资源上传
  -> Build 试玩到约 6000 分无明显卡顿
  -> 不做玩法代码大重构
  -> 修复 Build 中真实暴露的材质颜色问题
```

这是一条“优化前先归因”的实践记录。决定不优化某些代码，同样是一种性能决策。

## 交付范围

| 模块 | 当前职责 |
|---|---|
| `Docs/ProfilerEvidence/` | 外部项目中的轻量 Profiler 截图与 README 证据包 |
| `.gitignore` | 忽略 `BackpackSurvivor/ProfilerCaptures/` 大体积原始捕获 |
| `Projectile` | 使用显式运行时视觉材质和 `MaterialPropertyBlock` 设置子弹颜色 |
| `DropItem` | 使用显式运行时视觉材质和 `MaterialPropertyBlock` 设置稀有度颜色 |
| `M_RuntimeVisual_Unlit_Base.mat` | 课程记录中的运行时视觉材质事实源；本次静态确认 Prefab 已引用该材质 GUID |

## 最小示例

### 不把 EditorLoop 当作游戏热点

```text
EditorLoop 99.2%
PlayerLoop 1.30ms
```

这类帧不能直接驱动玩法代码优化。它更像 Editor 和 Profiler 窗口自身的观察开销，需要用 Development Build + Autoconnect Profiler 或直接 Player Build 体验再确认。

### 资源上传尖刺的判断口径

```text
EarlyUpdate.UpdatePreloading
Application.WaitForAsyncOperationToComplete
Gfx.CreateTexture / Gfx.UploadTexture
```

这类调用更接近资源预加载、贴图上传、字体或界面首次展开，不等同于敌人 AI、子弹、掉落或背包重绘的每帧热点。

### 子弹显式材质和 MPB

```csharp
[SerializeField] private Material visualMaterial;

private static readonly int BaseColorId = Shader.PropertyToID("_BaseColor");
private static readonly int ColorId = Shader.PropertyToID("_Color");
private MaterialPropertyBlock propertyBlock;

private void ApplyVisualColor(Color color)
{
    if (visualRenderer == null) return;

    if (visualMaterial == null)
    {
        visualRenderer.material.color = color;
        return;
    }

    visualRenderer.sharedMaterial = visualMaterial;
    propertyBlock ??= new MaterialPropertyBlock();
    visualRenderer.GetPropertyBlock(propertyBlock);
    propertyBlock.SetColor(BaseColorId, color);
    propertyBlock.SetColor(ColorId, color);
    visualRenderer.SetPropertyBlock(propertyBlock);
}
```

Build 中不要依赖运行时 `CreatePrimitive` 的默认材质表现。显式材质资产负责 Shader/材质链路，`MaterialPropertyBlock` 负责每个实例的颜色差异。

## 项目中的应用

### 低风险优化优先级

当前 Build 试玩没有复现后期明显卡顿，因此不做大重构。继续优化前，需要更稳定的复现实验和前后对照数据。

本课实际采取的是低风险动作：保存证据、忽略大文件、修复 Build 颜色异常、清理明显运行时日志，不重写波次、背包或武器系统。

### Build 问题优先于 Editor 感觉

Build 中真实暴露的问题是子弹和装备掉落物颜色异常。它比 Editor 中无法稳定归因的尖刺更值得马上修，因为它直接影响演示包可见质量。

### 证据包只保留轻量材料

外部项目 `Docs/ProfilerEvidence/` 保留了 README 和 PNG 截图；`BackpackSurvivor/ProfilerCaptures/` 大体积 `.data` 捕获由 `.gitignore` 忽略。知识库只记录结论和证据归属，不把外部原始捕获搬入正式文档目录。

## 常见错误

| 问题 | 根因 | 处理方式 |
|---|---|---|
| 看到 1000ms 尖刺就重构业务代码 | 没有区分 Editor / Profiler / PlayerLoop 来源 | 先看 Timeline / Hierarchy，再用 Build 体验裁决 |
| 把首次贴图上传当成每帧脚本热点 | 只看总耗时，不看调用栈 | 识别 `UpdatePreloading`、`CreateTexture`、`UploadTexture` 等资源链路 |
| 作品集仓库提交 `.data` 原始捕获 | 原始 Profiler 文件体积巨大，不适合长期仓库 | 提交轻量截图和 README，原始捕获本地保留 |
| Build 中颜色消失 | 运行时默认材质、Shader stripping 或属性映射不稳定 | 使用显式材质资产 + Prefab 引用 + `MaterialPropertyBlock` |
| 过早优化小规模数据结构 | 没有证明 HashSet、局部刷新等能带来收益 | 保留当前简单实现，等规模和数据证明后再改 |

## 如何验证

### 当前已记录证据

| 结论 | 证据等级 | 说明 |
|---|---|---|
| 用户记录 Build 后期波次打到约 `6000` 分，没有明显卡顿 | B | 来自用户放入 Inbox 的第 35 课课程记录和外部项目 Profiler 证据 README |
| 用户记录 BUG-025 已修复，Build 中子弹与装备掉落物颜色恢复正常 | B | 来自用户放入 Inbox 的第 35 课课程记录 |
| 外部项目 `Docs/ProfilerEvidence/README.md` 静态记录了 Render Thread、Loading/Texture Upload、EditorLoop 和 Live Display 观察结论 | C | 本环境只读查看外部项目证据包 |
| `.gitignore` 静态可见 `BackpackSurvivor/ProfilerCaptures/` 被忽略 | C | 本环境只读查看外部项目 `.gitignore` |
| `Projectile.cs` 与 `DropItem.cs` 静态可见 `visualMaterial`、`MaterialPropertyBlock` 和 `ApplyVisualColor()` | C | 本环境只读查看外部 Unity 工程脚本 |
| `Projectlie.prefab` 与 `DropItem.prefab` 静态可见 `visualMaterial` 指向同一运行时视觉材质 GUID | C | 本环境只读查看外部 Unity 工程 Prefab YAML |
| 本次静态扫描未见 `Unity.VisualScripting`、`UnityEditor` 或 `ShadowCascadeGUI` using；仍可见 `ObjectPool` 警告/错误日志和 `PickupLogger` 临时日志 | C | 本环境只读 `rg` 扫描脚本；日志是否保留需按交付策略继续判断 |
| 当前环境亲自运行 Profiler 或 Player Build | D | 当前环境未启动 Unity，未重新采样或运行 exe |

### 待补验证

- 后续若要宣称性能优化完成，需要保存同一场景、同一波次、同一平台的优化前后数据。
- 若 Build 中再次出现卡顿，应使用 Development Build + Autoconnect Profiler 或 Player 日志定位，不只看 Editor 录制。
- 对 TMP 字体、玩法说明面板和图标资源做一次开局预热策略评估，确认是否需要避免首次展开上传尖刺。
- 明确哪些 `Debug.LogWarning/Error` 属于保留诊断，哪些 `Debug.Log` 属于发布前应清理的临时日志。

## 复盘

- 原来的理解：Profiler 看到尖刺，就应该马上找热点优化。
- 实践后的结论：先确认尖刺归属。EditorLoop、Live Display 和资源上传不能直接等价为游戏逻辑卡顿；Build 体验和可重复数据才是交付判断依据。
- 仍未理解：当前缺少系统化前后对照实验，不能把“Build 无明显卡顿”写成“性能已经充分优化”。

## 相关内容

- 前置：[完整 15 分钟通关验收](full-run-acceptance.md)
- 后续：[Build 与演示包](build-and-demo-package.md)
- 专题：[性能优化](../../performance/index.md)
- 专题：[优化小 Tips](../../performance/perf-tips.md)
- 记录：[性能优化记录](performance-optimization-log.md)
- 记录：[Bug 记录簿](bug-log.md)

> 标签：`Unity` `Profiler` `EditorLoop` `Build 验证` `MaterialPropertyBlock` `性能优化` `项目实践`
