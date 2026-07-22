# Backpack Survivor V0.1 阶段复盘

> 复盘周期：2026-07-20 ～ 2026-07-22
>
> 项目阶段：战斗核心原型 V0.1
>
> 资料来源：用户阶段复盘；用户补充说明代码与 Unity 场景已由 Kimi 检查

## 阶段结论

根据用户复盘，V0.1 的 GDD 目标已经完成，并提前交付了主动攻击、刷怪器和对象池。这个结论属于用户项目记录；Kimi 的检查属于外部验证信息，本知识库没有重新打开 Unity 工程，因此不把它写成当前环境亲自运行的结果。

| 目标 | 用户记录状态 | 对应内容 |
|---|---|---|
| 角色移动 | 已完成 | 第 0 课前置内容 |
| 怪物追击 | 已完成 | [敌人 AI](../../projects/backpack-survivor/enemy-ai-and-melee.md) |
| 自动索敌与区域危险 | 已完成 | [伤害管线](../../projects/backpack-survivor/damage-pipeline-and-hazard-zone.md)、[自动武器](../../projects/backpack-survivor/target-registry-and-auto-weapon.md) |
| 自动攻击 | 已完成 | [目标注册表与自动武器](../../projects/backpack-survivor/target-registry-and-auto-weapon.md) |
| 主动攻击 | 超额完成 | [主动武器与 WeaponBase](../../projects/backpack-survivor/active-weapons-and-weapon-base.md) |
| 刷怪器 | 超额完成 | [刷怪器与对象池](../../projects/backpack-survivor/spawner-and-object-pooling.md) |
| 对象池 | 超额完成 | [刷怪器与对象池](../../projects/backpack-survivor/spawner-and-object-pooling.md) |

## 阶段产出

用户记录的量化产出：

- 14 个 C# 文件，约 900 行，分布在 Core、Combat、Enemies、Waves、Zones、Player 模块。
- `Enemy` / `Projectile` 两个 Prefab 和包含 3 个动作的 `GameInput` 输入资产。
- 5 课项目课程记录，4 次功能提交。

这些数字来自阶段复盘，当前工作区没有对应源码清单、Git 提交或 Unity 资源，因此仅作为复盘摘要保存。

## 三条设计主线

### 接口驱动

`IDamageable` 统一伤害入口，`IPoolable` 统一池化生命周期。危险区、近战、自动武器和主动武器复用伤害管线；对象池通过钩子调用具体对象的重置逻辑。

### 事件驱动

`Health` 发布受伤与死亡事件，敌人死亡时注销注册表、归还池子，未来的掉落和结算也可以通过订阅接入。事件发布者不直接持有血条、掉落或任务系统引用。

### 生命周期对称

`Awake` / `Start` 用于一次性初始化，`OnEnable` / `OnDisable` 用于每次激活期间的登记、订阅、注销和退订。第 5 课把第 3 课发现的“Start 订阅在池化后丢失”改为激活期处理。

## 可迁移的认知

1. **变化时更新缓存**：危险区目标列表、`TargetRegistry` 和刷怪计数都使用“变化时维护，查询时读取”的模式。
2. **时间逻辑必须帧率解耦**：tick、计时器和旋转使用 `Time.deltaTime`；低帧率补发策略仍需用场景测试确认。
3. **重复之后再抽象**：危险区先配置化，第二把武器出现后再提炼 `WeaponBase`，抽象有真实重复作为依据。
4. **生命周期对称支撑池化**：登记/订阅放在 `OnEnable`，注销/退订放在 `OnDisable`，对象才能安全休眠与复生。
5. **池化不是单纯 SetActive**：完整周期包括预热、取出、状态复位、服役、归还、防重复和再次取出。

## 问题与遗留债务

- `TargetRegistry` 仍是静态单场景方案，多场景和关闭 Domain Reload 时需要清理或升级为场景服务。
- `EnemyAI` 仍通过 Tag 查找玩家，多玩家、重生和切场景时需要显式目标来源。
- 玩家死亡后的 GameManager、结算和失败流程尚未接入。
- 无敌帧仍未实现，需要重新评估 `Health` 契约与数值。
- asmdef 程序集划分、测试程序集和工程 hygiene 仍待第 6 课处理。
- 刷怪器需要明确目标阵营计数、刷怪点地形/障碍校验和半径分布语义。
- 对象池需要继续验证跨池归还、场景清理、池所有权和预热峰值。

## 阶段 2 计划

```text
第 6 课  工程 hygiene 收尾：历史债务与 asmdef 评估
第 7 课  掉落系统：权重随机与保底计数
第 8 课  拾取系统：磁吸范围与自动拾取
第 9 课  背包纯数据网格：占格、放置、移除
第 10 课 背包 UI：拖拽、预览与冲突提示
第 11 课 合并升级与第一条邻接联动
```

原则仍是先实现可独立测试的纯数据逻辑，再让 UI 订阅状态并成为数据投影。

## 证据分层

- **用户项目记录**：5 课交付清单、代码/资产数量、设计决策、踩坑和下一阶段计划。
- **用户转述的外部检查**：Kimi 已检查代码与 Unity 场景。
- **本知识库验证**：本次文章归类、链接检查和 MkDocs 构建；没有 Unity 运行时或 Profiler 复测。

> 📎 标签：`阶段复盘` `Backpack Survivor` `V0.1` `对象池` `架构` `项目实践`
