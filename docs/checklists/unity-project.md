# Unity 项目能力检查清单

> 用于检查 Unity 知识是否已经落到可运行项目中。未学习的系统保持未勾选。

---

## 核心系统

- [x] 能解释当前项目中关键 MonoBehaviour 的生命周期顺序
- [ ] 能正确选择 Prefab、ScriptableObject 和普通 C# 对象
- [ ] 资源加载和释放有明确的所有者
- [x] UI 不依赖无必要的每帧轮询
- [ ] 场景切换时静态状态、事件和异步任务得到处理

## 数据与依赖

- [ ] 配置数据与运行时状态区分清楚
- [ ] 模块依赖方向能够用一张图说明
- [ ] 不依赖大量隐式全局单例完成通信
- [x] 事件订阅和取消订阅能够成对追踪
- [x] Inspector 引用、运行时查找和资源加载的选择有理由

## 验证与发布

- [x] 核心流程有最小测试或可重复验证步骤
- [ ] 使用 Profiler 检查过至少一个真实场景
- [ ] 记录目标平台和关键性能预算
- [ ] Build 后验证过功能，而不只在 Editor 中运行
- [x] 项目问题已经写入复盘，而不是只保留在记忆中

## 实践证据

- 项目：[Backpack Survivor](../projects/backpack-survivor/index.md)
- 当前证据：[伤害管线](../projects/backpack-survivor/damage-pipeline-and-hazard-zone.md)、[敌人 AI](../projects/backpack-survivor/enemy-ai-and-melee.md)、[自动武器](../projects/backpack-survivor/target-registry-and-auto-weapon.md)、[主动武器](../projects/backpack-survivor/active-weapons-and-weapon-base.md)、[刷怪器与对象池](../projects/backpack-survivor/spawner-and-object-pooling.md)、[掉落系统](../projects/backpack-survivor/loot-drop-and-pity.md)、[拾取与磁吸](../projects/backpack-survivor/pickup-and-magnet.md)、[背包纯数据网格](../projects/backpack-survivor/inventory-data-grid.md)和[背包 UI 与拖拽](../projects/backpack-survivor/inventory-ui-and-drag.md)，已形成 V0.1 战斗闭环并开始 V0.2 掉落、拾取、背包数据层和 UI 投影。
- 生命周期证据：[Unity 生命周期](../unity/lifecycle.md)与第 5 课记录了 `Awake` / `Start`、`OnEnable` / `OnDisable`、池化取出/归还和事件订阅修复；用户转述 Kimi 已检查代码与 Unity 场景。
- 复盘证据：[Backpack Survivor V0.1 阶段复盘](../reviews/2026/backpack-survivor-v0.1-review.md)。
- 尚缺证据：Profiler 前后数据、目标平台 Build、多 Collider、低帧率、缓冲区满载、切场景静态状态、跨池归还、完整调用顺序矩阵、掉落概率/保底单元测试、批量拾取副作用测试、拖拽中断回滚和实际 `.asmdef` / `.meta` / Prefab / Canvas 资产复核。
- 下一项改进：为背包满时的掉落吐回、拖拽取消、容器搜刮和合并升级补齐可重复验证。
