# 伤害管线与危险区

> 项目：[Backpack Survivor](index.md)
>
> 状态：已应用，存在待验证边界
>
> 日期：2026-07-20
>
> 阶段：V0.1 战斗核心原型 · 第 1 课
>
> Unity 版本：原始记录未注明

## 学习目标

- 用接口统一玩家、敌人和场景物体的受伤入口。
- 用伤害数据包承载攻击者、命中点、暴击与击退上下文。
- 让生命值逻辑通过事件通知表现层和后续系统。
- 用危险区验证阵营筛选、Trigger 缓存和周期伤害。
- 区分已经运行观察到的行为与静态检查发现的边界风险。

## 实现范围

| 模块 | 当前职责 |
|---|---|
| `IDamageable` | 定义 `TakeDamage`、位置、死亡状态和阵营查询 |
| `DamageInfo` | 传递伤害值、攻击者、命中点、暴击和击退信息 |
| `Health` | 保存生命值、阻止死亡后重复受伤、广播受伤与死亡事件 |
| `HazardZone` | 缓存 Trigger 内目标，按可配置阵营或中立规则筛选，并按 tick 施加环境伤害 |

系统数据流：

```text
HazardZone
  ↓ 创建 DamageInfo
IDamageable.TakeDamage(info)
  ↓ 当前由 Health 实现
扣减生命值
  ├─ OnDamaged(info)
  └─ OnDeath()
       ↓
后续 UI、敌人死亡流程、掉落和任务系统订阅
```

原始记录描述的运行结果是：`damagePerSecond = 10`、`tickInterval = 0.5` 时每跳扣除 5 点生命；玩家离开危险区后停止受伤；死亡事件触发后不再继续结算伤害。

## 关键设计决策

### 1. 伤害来源依赖接口

`HazardZone` 只依赖 `IDamageable`，不依赖具体的 `Health`。以后敌人、玩家、宝箱或可破坏物只要实现相同契约，就可以复用伤害来源。

当前接口还包含 `Position` 和 `Faction` 查询，这是为了满足命中点与阵营过滤的实际需求。接口继续增长时，应重新判断是否需要拆分成更小的查询能力，而不是无限增加成员。

### 2. 使用 DamageInfo 数据包

相比只传一个 `float`，数据包能让受伤反馈、击退、暴击显示和击杀归属使用同一份上下文。

当前实现使用带 `readonly` 字段的 `struct`，字段不能重新赋值，但这不代表深层对象完全不可变，例如 `attacker` 指向的 `GameObject` 仍然可以变化。下一版可以使用 `readonly struct` 和只读属性进一步表达设计意图。

### 3. Health 只发布状态变化

`Health` 定义：

```csharp
public event Action<DamageInfo> OnDamaged;
public event Action OnDeath;
```

生命值组件不直接引用血条、飘字、掉落或任务系统。第 2 课的敌人已经用 `OnDeath` 驱动一次性销毁流程，验证了最简单的订阅者路径；第 3 课改为停用对象后也暴露出新的边界：`Start` 只订阅一次，而死亡时已经退订，再次激活不会自动恢复订阅。因此一次性销毁路径已有实践记录，对象池复用路径仍未完成。

### 4. Trigger 事件维护缓存

进入和离开危险区时更新目标集合，tick 时直接遍历缓存，避免每次结算都执行全场景物理查询。这是“变化时维护状态，使用时直接读取”的工程取舍。

当前使用 `List<IDamageable>` 并通过倒序遍历删除失效目标。目标数量较小时足够清晰；只有 Profiler 证明查找或移除成为瓶颈后，才需要改成其他数据结构。

### 5. 暂缓 Zone 基类

目前只有一种危险区，没有足够案例证明多个区域共享稳定行为。第 2 课已把目标阵营改成字段，并用中立值表达“不过滤阵营”；伤害、间隔和阵营差异继续通过配置承载。等出现两到三个具有不同执行行为的真实变体后，再根据重复代码提炼基类或策略，避免为了预测未来而过早抽象。

## 当前实现中的有效做法

- `Health.TakeDamage` 使用守卫子句，死亡后不再重复触发事件。
- `Mathf.Clamp` 保证当前生命值处于 `0..maxHp`。
- 环境伤害允许 `attacker == null`，日志使用 null 兜底。
- `HazardZone` 倒序遍历缓存，删除元素时不会打乱尚未处理的索引。
- 伤害值用 `damagePerSecond * tickInterval` 表达，使配置仍以“秒伤”为语义。
- 命名空间与目录职责保持对应，脚本之间只通过公开契约通信。

## 静态检查发现的边界

### 1. 当前 tick 不是严格帧率无关

现有逻辑在计时器小于等于零时只结算一次，然后直接执行：

```csharp
tickTimer = tickInterval;
```

如果一帧跨过多个 tick，只会结算一次，多出的时间被丢弃；目标刚进入时第一次伤害的延迟也取决于区域计时器当前相位。若设计要求严格累计，可以保留超出的时间：

```csharp
tickTimer -= Time.deltaTime;

while (tickTimer <= 0f)
{
    tickTimer += tickInterval;
    ApplyDamageTick();
}
```

使用 `while` 前必须保证 `tickInterval > 0`，并决定卡顿后是否允许同一帧补发多跳伤害。

### 2. 接口引用可能绕过 Unity 的销毁判空

缓存类型是 `IDamageable`。Unity 对已销毁对象的特殊 `== null` 行为依赖 `UnityEngine.Object`，通过接口引用直接比较 null 可能无法可靠识别“托管对象还在、原生对象已销毁”的状态。

处理前应同时考虑普通 null 与 Unity 对象销毁状态，或在缓存中保留一个明确的 `UnityEngine.Object` / `MonoBehaviour` 引用用于生命周期判断。

### 3. 多 Collider 可能提前移除目标

`Contains` 可以阻止同一目标重复加入，但只要任意一个 Collider 执行 `OnTriggerExit`，当前实现就会直接移除目标。角色存在多个 Collider 时，其他 Collider 可能仍在区域内。

需要明确约束“每个目标只能有一个参与危险区的 Collider”，或按目标记录进入区域的 Collider 引用计数，计数归零后再移除。

### 4. GetComponent 只查当前 Collider 对象

如果 Collider 位于角色子物体，而 `Health` 位于父物体，`other.GetComponent<IDamageable>()` 无法找到目标。项目应统一组件布局，或使用能够向父级查找接口实现的封装。

### 5. Health 契约仍需补充

- 代码注释提到“无敌帧”，但当前只实现了死亡守卫，尚无无敌状态。
- 没有限制负伤害；负值会增加生命值并触发 `OnDamaged`。应明确伤害必须非负，或单独设计治疗接口。
- `OnDamaged` 只传入攻击上下文，没有暴露当前和最大生命值。接入血条前需要增加只读属性，或扩充事件数据。
- 热路径上的 `Debug.Log` 适合原型调试，进入性能测试或发布版本前应提供开关。

## 踩坑记录

- 中文脚本编码曾受系统默认 ANSI / GBK 影响；项目使用 `.editorconfig` 统一编码。
- IDE 自动导入了 `NUnit.Framework`，导致 `List<T>` 类型解析错误；自动导入必须人工检查，玩法代码不引用测试命名空间。
- 未初始化的暴击倍率可能默认为 0，使暴击伤害变为零；倍率计算应由攻击方负责，`Health` 只执行最终伤害。
- 环境伤害没有攻击者，读取 `attacker.name` 前必须处理 null。
- Unity 序列化字段改名可能丢失 Inspector 数据；需要稳定命名或使用 `FormerlySerializedAs` 迁移。

## 如何验证

原始记录提供了基础运行观察，但以下测试仍应在 Unity 工程中保留可重复证据：

- 单一 Collider 进入、停留、离开和再次进入。
- 多 Collider 角色只在全部 Collider 离开后停止受伤。
- 目标在区域内被销毁，不产生 `MissingReferenceException`。
- 低帧率或人工卡顿时，总伤害是否符合设计语义。
- `tickInterval` 为零或负数时能够被配置校验阻止。
- 玩家、敌人和环境阵营过滤符合预期。
- `OnDamaged` 每次伤害触发，`OnDeath` 只触发一次。
- 订阅者禁用或销毁时能够正确取消事件订阅。

当前知识库环境使用 .NET SDK 和最小 Unity API 桩完成了三个脚本的编译，并通过 `Health` 扣血/死亡守卫、危险区进入/tick/退出的逻辑冒烟测试。该验证不包含 Unity 物理回调、序列化和销毁语义；真实场景运行结果仍来自本次原始学习记录。

## 下一步

- 敌人近战和投射物已经成为新的伤害来源，后续验证所有来源的阵营、击退和日志语义一致。
- 修复敌人从一次性销毁改为停用复用后，死亡事件与生命值状态没有完整恢复的问题。
- 增加 `CurrentHp` / `MaxHp` 只读接口，为 UI 订阅提供状态。
- 根据多 Collider 和低帧率测试结果修正 `HazardZone`。
- 补充场景结构、Collider 布局和可重复测试证据。

## 相关内容

- [委托与事件](../../csharp/oop/delegates-and-events.md)
- [值类型 vs 引用类型](../../csharp/oop/value-vs-reference.md)
- [敌人追击、近战与死亡流程](enemy-ai-and-melee.md)
- [目标注册表、自动武器与投射物](target-registry-and-auto-weapon.md)
- [C# 工程实践路线](../../csharp/engineering/index.md)
- [Unity 项目能力检查清单](../../checklists/unity-project.md)

> 📎 标签：`Unity` `战斗系统` `IDamageable` `事件` `Trigger` `伤害管线` `项目实践`
