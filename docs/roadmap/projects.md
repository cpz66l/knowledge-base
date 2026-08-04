# 项目实践路线

> 项目是验证知识的地方，不是把所有新技术一次塞进去。每个项目只选择少量明确目标，并保留问题、验证和复盘记录。

---

## 项目分级

### 1. 最小练习

规模：数十行到一个小场景。
目的：验证单个知识点。

示例：

- 一个泛型对象池实验
- 一个 UGUI 控件组合
- 一个 Shader 效果
- 一个 TCP 消息收发实验

### 2. 专题 Demo

规模：一个可独立运行的功能。
目的：串联同一专题中的多个知识点。

示例：

- 背包或任务系统
- Addressables 资源加载 Demo
- 状态同步 Demo
- 热更新流程 Demo

### 3. 综合项目

规模：可展示、可复盘。
目的：把语言、Unity、性能和专项能力形成闭环。

---

## 每个项目必须记录

1. 项目目标
2. 使用了哪些已有知识
3. 为什么选择当前方案
4. 遇到什么问题
5. 如何验证功能与性能
6. 哪些地方仍不理解
7. 下一次会如何改进

项目完成后使用[项目复盘模板](../reviews/project-review-template.md)，达到可展示标准后再从[项目实践](../projects/index.md)建立正式项目页。

---

## 当前项目

- [Backpack Survivor（背包幸存者）](../projects/backpack-survivor/index.md)
- 已完成阶段：V0.1 战斗核心原型
- 已记录：[第 1 课：伤害管线与危险区](../projects/backpack-survivor/damage-pipeline-and-hazard-zone.md)
- 已记录：[第 2 课：敌人追击、近战与死亡流程](../projects/backpack-survivor/enemy-ai-and-melee.md)
- 已记录：[第 3 课：目标注册表、自动武器与投射物](../projects/backpack-survivor/target-registry-and-auto-weapon.md)
- 已记录：[第 4 课：主动武器与 WeaponBase 提炼](../projects/backpack-survivor/active-weapons-and-weapon-base.md)
- 已记录：[第 5 课：刷怪器与对象池](../projects/backpack-survivor/spawner-and-object-pooling.md)
- 已记录：[第 7 课：掉落系统与保底机制](../projects/backpack-survivor/loot-drop-and-pity.md)
- 已记录：[第 8 课：拾取与磁吸](../projects/backpack-survivor/pickup-and-magnet.md)
- 已记录：[第 9 课：背包纯数据网格](../projects/backpack-survivor/inventory-data-grid.md)
- 已记录：[第 10 课：背包 UI 与拖拽](../projects/backpack-survivor/inventory-ui-and-drag.md)
- 已记录：[第 11 课：掉落分层与交互拾取](../projects/backpack-survivor/loot-layering-and-interaction.md)
- 已记录：[第 12 课：容器搜刮与宝箱系统](../projects/backpack-survivor/container-looting-and-chests.md)
- 已记录：[第 13 课：背包交互补丁](../projects/backpack-survivor/inventory-interaction-patches.md)
- 已记录：[第 14 课：合并升级与邻接联动](../projects/backpack-survivor/merge-upgrade-and-adjacency.md)
- 已记录：[第 15 课：背包武器激活](../projects/backpack-survivor/backpack-weapon-activation.md)
- 已记录：[第 16 课：单局框架与基础 HUD](../projects/backpack-survivor/run-session-and-basic-hud.md)
- 已记录：[第 17 课：经验成长与三选一](../projects/backpack-survivor/level-progression-and-choice.md)
- 已记录：[第 18 课：波次导演与 15 分钟节奏](../projects/backpack-survivor/wave-director-and-run-pacing.md)
- 已记录：[第 19 课：战斗反馈快包](../projects/backpack-survivor/combat-feedback-pack.md)
- 已记录：[第 20 课：胜负结算与重开闭环](../projects/backpack-survivor/run-result-and-restart-loop.md)
- 已记录：[第 21 课：构筑最小兑现](../projects/backpack-survivor/build-payoff-dual-wield.md)
- 已记录：[第 22 课：内容面铺开](../projects/backpack-survivor/content-expansion-fire-rate-boost.md)
- 已记录：[第 23 课：精英宝箱与终局压力强化](../projects/backpack-survivor/elite-chests-endgame-pressure.md)
- 已记录：[第 24 课：金币掉落与局内经济 HUD](../projects/backpack-survivor/gold-drops-and-economy-hud.md)
- 已记录：[第 25 课：背包价值与物品价值显示](../projects/backpack-survivor/backpack-value-and-item-value-display.md)
- 已记录：[第 26 课：合并升级收益兑现](../projects/backpack-survivor/merge-upgrade-reward-payoff.md)
- 已记录：[第 27 课：数值调参台与首轮平衡](../projects/backpack-survivor/balance-tuning-and-first-playtest.md)
- 阶段复盘：[Backpack Survivor V0.1](../reviews/2026/backpack-survivor-v0.1-review.md)
- 当前阶段：V0.2 数值调参台与首轮平衡已记录
- 下一步：第 28 课新手目标提示与局内可读性；第 6 课工程 hygiene 资料收到后再补入库

---

## 推荐推进方式

```text
最小练习
  ↓
专题 Demo
  ↓
综合项目
  ↓
性能 / 测试 / 架构复盘
  ↓
作品集表达
```

当前项目入口：[项目实践](../projects/index.md)。
