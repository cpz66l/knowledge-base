# 战斗反馈快包

> 项目：[Backpack Survivor](index.md)
>
> 状态：用户课程记录描述已实现 `DamageFlashView`、`DamageNumberView`、`SfxPlayer`、`PlayerHitFeedbackView` 和 Cinemachine 震屏；本环境完成静态审阅、项目文件只读复核与文档验证，未运行 Unity Editor / Play Mode
>
> 日期：2026-07-30
>
> 阶段：V0.2 掉落与背包构筑 · 第 19 课

## 学习目标

- 让战斗事实用闪色、伤害数字、音效和震屏立刻反馈给玩家。
- 把表现层接到 `Health.OnDamaged`、开火、拾取、升级和开箱等事实入口，而不是重新计算规则。
- 用对象池承载高频短生命周期的伤害数字，避免命中反馈变成分配尖峰来源。
- 用 World Space Canvas 和 Billboard 解决伤害数字的世界坐标显示。
- 用 `SfxPlayer` 集中播放短音效，避免音效入口散落在各个业务脚本里。
- 在 Cinemachine 3 管线内做轻量震屏，而不是直接改 `Main Camera` 的 Transform。
- 让缺失音效、缺失震屏或缺失池引用时独立降级，不拖死其他反馈。

## 交付范围

| 模块 | 当前职责 |
|---|---|
| `DamageFlashView` | 订阅 `Health.OnDamaged`，受击时临时改 Renderer 颜色，并在禁用时停止协程和恢复原色 |
| `DamageNumberSpawner` | 订阅敌人 `Health.OnDamaged`，从场景对象池取出伤害数字，并播放命中音效 |
| `DamageNumberView` | 显示伤害文本、上浮、渐隐、面向主摄像机，并在生命周期结束时归还对象池 |
| `DamageNumberPoolProvider` | 把场景级 `ObjectPool` 显式暴露给敌人预制体上的 Spawner |
| `SfxPlayer` | 集中封装开火、命中、经验拾取、升级、受伤和开箱音效 |
| `PlayerHitFeedbackView` | 订阅玩家 `Health.OnDamaged`，同时触发受伤音效和相机震动 |
| `CameraShakePlayer` | 控制 `CinemachineBasicMultiChannelPerlin` 的 `AmplitudeGain` / `FrequencyGain`，用协程衰减震屏 |

第 18 课已经让敌人压力随时间上升。第 19 课不再继续堆规则，而是补上“游戏会说话”的一层：命中要能看见，受伤要有感知，升级和开箱要有声音反馈。

## 反馈不是规则

这一课最重要的边界是：

```text
规则层：Health / WeaponBase / GameSession / LootChest
表现层：DamageFlashView / DamageNumberView / SfxPlayer / CameraShakePlayer
```

表现层只消费已经发生的事实。`DamageFlashView` 和 `DamageNumberSpawner` 都订阅 `Health.OnDamaged`，但它们不改血量、不决定死亡，也不参与伤害计算。

这样后续替换伤害数字样式、音效资源或震屏参数时，不会碰到战斗规则。

## 受击闪色

`DamageFlashView` 挂在可受伤对象上，激活期订阅 `Health.OnDamaged`：

```csharp
private void OnEnable()
{
    if (health != null)
        health.OnDamaged += HandleDamaged;
}

private void OnDisable()
{
    if (health != null)
        health.OnDamaged -= HandleDamaged;

    if (flashRoutine != null)
    {
        StopCoroutine(flashRoutine);
        flashRoutine = null;
    }

    RestoreColors();
}
```

这里的关键不是“闪一下白色”，而是对象池纪律：

- 每次启用重新订阅事件；
- 每次禁用取消订阅；
- 回收时停止未结束协程；
- 回收时恢复原色，避免带着上一轮受击颜色复活。

当前实现通过 `renderer.material.color` 改色。它适合 Demo 阶段快速验证，但大量敌人高频受击时，后续应结合 Profiler 观察材质实例化、内存和渲染成本；如果成为瓶颈，再考虑 `MaterialPropertyBlock` 等方案。

## 伤害数字池

伤害数字是典型的高频短生命周期对象：

```text
命中发生
  -> 从池中取 DamageNumber
  -> 显示 0.6 秒
  -> 上浮 / 渐隐
  -> 回池
```

`DamageNumberSpawner` 不直接 `Instantiate`，而是从 `DamageNumberPoolProvider` 暴露的场景池取对象：

```csharp
private void Start()
{
    DamageNumberPoolProvider provider = FindAnyObjectByType<DamageNumberPoolProvider>();
    if (provider != null)
        damageNumberPool = provider.DamageNumberPool;
}
```

敌人是 Prefab，不能稳定保存对场景实例的引用。Provider 方案把依赖显式留在场景对象上，比按名字 `GameObject.Find("DamageNumberPool")` 更稳，也便于在 Inspector 中检查。

当前静态场景检查可见：

- `Enemy.prefab` 挂了 `DamageFlashView` 和 `DamageNumberSpawner`；
- `DamageNumber.prefab` 是 World Space Canvas，缩放约 `0.01`，带 `DamageNumberView` 和 `CanvasGroup`；
- `01-Run.unity` 中存在 `DamageNumberPool`，预热数量为 `30`，并挂了 `DamageNumberPoolProvider`。

## DamageNumberView

`DamageNumberView` 自己管理短生命周期：

```csharp
private IEnumerator PlayRoutine()
{
    float t = 0f;
    startPosition = transform.position;

    while (t < lifetime)
    {
        t += Time.deltaTime;
        float ratio = Mathf.Clamp01(t / lifetime);

        transform.position = Vector3.Lerp(
            startPosition,
            startPosition + Vector3.up * riseDistance,
            ratio);

        FaceCamera();

        if (canvasGroup != null)
            canvasGroup.alpha = 1f - ratio;

        yield return null;
    }

    playRoutine = null;

    if (pool != null)
        pool.Return(gameObject);
    else
        gameObject.SetActive(false);
}
```

这里有三个沉淀点：

| 点 | 说明 |
|---|---|
| World Space Canvas | 伤害数字属于敌人附近的世界反馈，不能停留在屏幕中心 |
| Billboard | World Space UI 不会自动面向摄像机，需要在播放过程中对齐 `Camera.main` |
| 自己回池 | Spawner 只负责生成，不持有数字后续状态，生命周期结束由 View 归还 |

池化对象取出和归还时继续做状态清理：

- `OnGetFromPool()` 停止旧协程、重置 `alpha`、清空文本并面向相机；
- `OnReturnPool()` 停止旧协程并置空 `playRoutine`。

## SfxPlayer

`SfxPlayer` 把短音效统一收口：

```csharp
private void PlayOneShot(AudioClip clip)
{
    if (audioSource == null || clip == null) return;

    audioSource.PlayOneShot(clip);
}
```

调用方表达的是反馈意图：

| 调用点 | 音效意图 |
|---|---|
| `WeaponBase.Fire()` | 开火 |
| `DamageNumberSpawner.HandleDamaged()` | 命中 |
| `GameSession.HandleXpCollected()` | 经验拾取、升级 |
| `LootChest.Interact()` | 开宝箱 |
| `PlayerHitFeedbackView.HandleHitFeedBack()` | 玩家受伤 |

当前只读场景 YAML 里，`SfxPlayer` 已挂在 `System` 对象上，`GameSession` 引用了它；但 `audioSource` 和各个 `AudioClip` 字段显示为 `{fileID: 0}`，且 `System` 对象片段中未看到 `AudioSource` 组件。因此本环境只能证明音效入口已写入代码和场景，不能证明实际有声音播放，后续需要在 Unity Inspector 和 Play Mode 中确认资源接线。

## 玩家受击反馈

玩家受击时，音效和震屏来自同一个事实：玩家 `Health.OnDamaged`。

```csharp
private void HandleHitFeedBack(DamageInfo info)
{
    sfx?.PlayHurt();

    if (cameraShakePlayer != null)
        cameraShakePlayer.Shake(duration, amplitude, frequency);
}
```

这里的写法有一个重要习惯：两个反馈分支互不阻塞。缺 `SfxPlayer` 时，震屏仍然可以执行；缺 `CameraShakePlayer` 时，受伤音效仍然可以播放。

静态场景 YAML 中，玩家对象上可见受击闪色和玩家受击反馈字段，参数为 `duration = 0.12`、`amplitude = 1.5`、`frequency = 15`。同时，`PlayerHitFeedbackView.cs.meta` 的 GUID 已被场景引用，但 `m_EditorClassIdentifier` 仍显示旧名 `HurtSfxView`，这可能是脚本重命名后的序列化残留，需在 Unity Editor 中复核 Inspector 是否正常显示脚本名和字段。

## Cinemachine 震屏

项目当前使用 Cinemachine 3.1.7。`CM_PlayerCamera` 挂了：

- `CinemachineCamera`
- `CinemachineFollow`
- `CameraShakePlayer`
- `CinemachineBasicMultiChannelPerlin`

`Main Camera` 由 Cinemachine Brain 输出最终画面。震屏应接在虚拟相机管线里，而不是直接摇 `Main Camera`：

```csharp
public void Shake(float duration, float amplitude, float frequency)
{
    if (noise == null)
        return;

    if (shakeRoutine != null)
        StopCoroutine(shakeRoutine);

    shakeRoutine = StartCoroutine(ShakeRoutine(duration, amplitude, frequency));
}
```

`ShakeRoutine` 使用 `Time.unscaledDeltaTime`，意味着即使普通时间缩放受暂停影响，震屏衰减仍按真实时间走完。它只衰减 `AmplitudeGain`，保持 `FrequencyGain` 不变：强度应该消失，频率不需要跟着“软掉”。

## 周期链路

### 敌人受击

```text
Projectile 命中敌人
  -> IDamageable.TakeDamage(DamageInfo)
  -> Health 扣血并触发 OnDamaged
  -> DamageFlashView 闪白
  -> DamageNumberSpawner 从池中取伤害数字
  -> DamageNumberView 上浮、渐隐、回池
  -> SfxPlayer.PlayHit()
```

### 玩家受击

```text
敌人近战 / 其他伤害来源
  -> playerHealth.TakeDamage(DamageInfo)
  -> Health.OnDamaged
  -> PlayerHitFeedbackView
  -> SfxPlayer.PlayHurt()
  -> CameraShakePlayer.Shake()
  -> CinemachineBasicMultiChannelPerlin 输出短震屏
```

### 开箱与成长音效

```text
经验球收集
  -> GameSession.HandleXpCollected()
  -> PlayPickupXp()
  -> 如升级则 PlayLevelUp()

LootChest.Interact()
  -> PlayChestOpen()
  -> 生成掉落并散落
```

## 常见错误

| 问题 | 根因 | 处理方式 |
|---|---|---|
| 伤害数字总在屏幕中间 | Canvas 仍是 Screen Space | 伤害数字 Prefab 改成 World Space Canvas |
| 数字在敌人附近但斜着 | World Space UI 不会自动面向摄像机 | 播放期间执行 Billboard，对齐主摄像机 |
| 池化数字复用后透明或文本残留 | `OnGetFromPool()` 没重置 `CanvasGroup` / 文本 / 协程 | 取出时重置 alpha、文本和协程状态 |
| 对象回收后仍在闪色 | 禁用时没有停止协程和恢复原色 | `OnDisable()` 停协程、退订、恢复颜色 |
| 缺音效导致震屏不触发 | 一个反馈分支 `return` 掉整个处理函数 | 音效和震屏分别判空、分别执行 |
| 直接改 `Main Camera` 无效或抖动异常 | Cinemachine Brain 每帧接管主相机 | 在虚拟相机上用 Perlin / Impulse 做镜头反馈 |
| 音效入口存在但听不到声音 | `AudioSource` 或 `AudioClip` 未接线 | 检查 `SfxPlayer` 所在对象是否有 `AudioSource`，Clip 是否非空 |
| 重命名脚本后 Inspector 异常 | 场景 YAML 保留旧 `m_EditorClassIdentifier` | 打开 Unity 复核脚本字段，必要时重新挂载或保存场景 |

## 如何验证

### 受击与数字

- 敌人被投射物命中时闪白，玩家受击时闪红。
- 连续受击不会让闪色协程叠加失控。
- 敌人回池再取出后颜色恢复正常。
- 伤害数字出现在命中点或目标附近，而不是屏幕中心。
- 伤害数字上浮、渐隐、面向摄像机，并在播放结束后回池。

### 音效与震屏

- 开火、命中、拾取经验、升级、玩家受伤和开箱各自触发对应音效。
- `SfxPlayer` 的 `AudioSource` 与各个 `AudioClip` 已正确接线。
- 玩家受击时有短促震屏，且幅度不会长期残留。
- 缺少某个音效 Clip 时不影响其他反馈。
- 普通暂停或升级选择期间，如需要播放 UI / 受击反馈，应确认 `Time.unscaledDeltaTime` 与 `PlayOneShot` 行为符合预期。

### 性能与工程

- 波次高压下伤害数字池不会频繁扩容。
- Profiler 中观察伤害数字、闪色材质访问、音效播放和 Cinemachine 震屏的 GC Alloc / 帧耗时。
- `DamageNumberPool` 的预热数量与实际峰值匹配。
- 场景中 `SfxPlayer`、`CameraShakePlayer`、`DamageNumberPoolProvider` 的引用都能在 Inspector 中正常显示。
- 本环境只做项目文件只读复核，没有运行 Unity Editor / Play Mode；仍需在 Unity 中复核真实画面、声音、震屏强度、资源接线和性能数据。

## 当前证据分层

| 结论 | 证据等级 | 说明 |
|---|---|---|
| 第 19 课实现了受击闪色、池化伤害数字、短音效入口、玩家受伤反馈和 Cinemachine 震屏 | B | 来自用户放入 Inbox 的课程记录 |
| 项目工作区存在 `DamageFlashView.cs`、`DamageNumberView.cs`、`DamageNumberSpawner.cs`、`DamageNumberPoolProvider.cs`、`SfxPlayer.cs`、`PlayerHitFeedbackView.cs`、`CameraShakePlayer.cs` 及 `.meta` | C | 本环境对 `E:\YouXiKaiFa\Backpack Survivor` 做只读文件扫描 |
| `DamageFlashView`、`DamageNumberSpawner` 和 `PlayerHitFeedbackView` 都订阅 / 退订 `Health.OnDamaged` | C | 本环境只读查看脚本，未编译或运行 Unity |
| `DamageNumberView` 实现了上浮、渐隐、Billboard、`OnGetFromPool()` 和 `OnReturnPool()` 清理 | C | 本环境只读查看脚本和 DamageNumber Prefab |
| `manifest.json` 中 Cinemachine 版本为 `3.1.7`，场景中可见 `CM_PlayerCamera` 挂有 `CinemachineCamera`、`CinemachineFollow`、`CameraShakePlayer` 和 `CinemachineBasicMultiChannelPerlin` | C | 本环境只读检查包清单和场景 YAML |
| `SfxPlayer` 入口已经接到 `WeaponBase`、`DamageNumberSpawner`、`GameSession`、`LootChest` 和 `PlayerHitFeedbackView` | C | 本环境只读查看脚本 |
| 本课音效资源已在场景中完整接线并能播放 | D | `01-Run.unity` 中 `SfxPlayer` 的 `AudioSource` 与 Clip 字段显示为空，本环境未运行 Unity 复核 |
| 当前环境已在 Unity Editor / Play Mode 中验证战斗反馈效果 | D | 未启动 Unity，未运行 Play Mode，未观察真实闪色、数字、音效或震屏 |

## 相关内容

- 前置：[波次导演与 15 分钟节奏](wave-director-and-run-pacing.md)
- 前置：[单局框架与基础 HUD](run-session-and-basic-hud.md)
- 前置：[刷怪器与对象池](spawner-and-object-pooling.md)
- 系统：[伤害管线与危险区](damage-pipeline-and-hazard-zone.md)
- 后续：[胜负结算与重开闭环](run-result-and-restart-loop.md)
- C#：[委托与事件](../../csharp/oop/delegates-and-events.md)
- UGUI：[UGUI 总览](../../unity/ugui/index.md)
- 性能：[对象池](../../performance/memory/object-pool.md)
- 性能：[优化小 Tips](../../performance/perf-tips.md)

> 📎 标签：`Unity` `战斗反馈` `伤害数字` `音效` `Cinemachine` `对象池` `事件驱动表现` `项目实践`
