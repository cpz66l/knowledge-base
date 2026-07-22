# Unity

> Unity 引擎核心概念与实战 — 生命周期 · ScriptableObject · Prefab · 资源管理 · UGUI · 动画

---

## 学习定位

> 路线：C# / Unity 主线
> 前置：基础 C#、面向对象与事件
> 路线入口：[C# / Unity 主线](../roadmap/csharp-unity.md)
> 项目检查：[Unity 项目能力清单](../checklists/unity-project.md)

推荐按“生命周期 → 数据与 Prefab → UI/动画 → 资源 → 工具”的顺序学习，并为每组知识保留一个可运行 Demo。

---

## 已有内容

| 专题 | 当前内容 | 学习出口 |
|---|---|---|
| 核心生命周期 | [初始化、启用与禁用](lifecycle.md) | 能说明一次性初始化与每次复用的区别 |
| UI | [UGUI](ugui/index.md) | 可交互界面 Demo |
| 动画 | [动画系统](animation/index.md) | 动画状态或表现流程 |
| 战斗与物理 | [伤害管线与危险区](../projects/backpack-survivor/damage-pipeline-and-hazard-zone.md) | Trigger、组件缓存和战斗契约实践 |
| 战斗与物理 | [敌人 AI](../projects/backpack-survivor/enemy-ai-and-melee.md) · [自动武器与投射物](../projects/backpack-survivor/target-registry-and-auto-weapon.md) | 状态分支、注册表、LateUpdate 与扫掠检测实践 |
| 输入与武器 | [主动武器与 WeaponBase](../projects/backpack-survivor/active-weapons-and-weapon-base.md) | Input System 状态位、瞄准与重复后抽象 |
| 生成与复用 | [刷怪器与对象池](../projects/backpack-survivor/spawner-and-object-pooling.md) | Prefab、OnEnable/OnDisable、预热和池化复位 |

## 计划主题

以下内容仍处于规划阶段，完成最小实验后再建立正式文章：

- 生命周期完整调用顺序矩阵与对象池回归实验
- ScriptableObject、Prefab 与数据关系
- Addressables 加载、释放和资源所有权
- Editor 工具、测试、程序集与 Build 验证

---

## 学习闭环

1. 阅读当前系统的已有文章
2. 在独立场景完成最小示例
3. 记录生命周期、引用关系或资源所有权
4. 应用到[项目实践](../projects/index.md)
5. 使用[项目复盘模板](../reviews/project-review-template.md)记录问题与下一步
