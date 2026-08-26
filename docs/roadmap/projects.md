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
- 已完成阶段：V0.3.11 / V0.3 Release 文案与发布验收；V0.2 正式演示包已完成
- 项目中使用：[第 1 课：伤害管线与危险区](../projects/backpack-survivor/damage-pipeline-and-hazard-zone.md)
- 项目中使用：[第 2 课：敌人追击、近战与死亡流程](../projects/backpack-survivor/enemy-ai-and-melee.md)
- 项目中使用：[第 3 课：目标注册表、自动武器与投射物](../projects/backpack-survivor/target-registry-and-auto-weapon.md)
- 项目中使用：[第 4 课：主动武器与 WeaponBase 提炼](../projects/backpack-survivor/active-weapons-and-weapon-base.md)
- 项目中使用：[第 5 课：刷怪器与对象池](../projects/backpack-survivor/spawner-and-object-pooling.md)
- 项目中使用：[第 7 课：掉落系统与保底机制](../projects/backpack-survivor/loot-drop-and-pity.md)
- 项目中使用：[第 8 课：拾取与磁吸](../projects/backpack-survivor/pickup-and-magnet.md)
- 项目中使用：[第 9 课：背包纯数据网格](../projects/backpack-survivor/inventory-data-grid.md)
- 项目中使用：[第 10 课：背包 UI 与拖拽](../projects/backpack-survivor/inventory-ui-and-drag.md)
- 项目中使用：[第 11 课：掉落分层与交互拾取](../projects/backpack-survivor/loot-layering-and-interaction.md)
- 项目中使用：[第 12 课：容器搜刮与宝箱系统](../projects/backpack-survivor/container-looting-and-chests.md)
- 项目中使用：[第 13 课：背包交互补丁](../projects/backpack-survivor/inventory-interaction-patches.md)
- 项目中使用：[第 14 课：合并升级与邻接联动](../projects/backpack-survivor/merge-upgrade-and-adjacency.md)
- 项目中使用：[第 15 课：背包武器激活](../projects/backpack-survivor/backpack-weapon-activation.md)
- 项目中使用：[第 16 课：单局框架与基础 HUD](../projects/backpack-survivor/run-session-and-basic-hud.md)
- 项目中使用：[第 17 课：经验成长与三选一](../projects/backpack-survivor/level-progression-and-choice.md)
- 项目中使用：[第 18 课：波次导演与 15 分钟节奏](../projects/backpack-survivor/wave-director-and-run-pacing.md)
- 项目中使用：[第 19 课：战斗反馈快包](../projects/backpack-survivor/combat-feedback-pack.md)
- 项目中使用：[第 20 课：胜负结算与重开闭环](../projects/backpack-survivor/run-result-and-restart-loop.md)
- 项目中使用：[第 21 课：构筑最小兑现](../projects/backpack-survivor/build-payoff-dual-wield.md)
- 项目中使用：[第 22 课：内容面铺开](../projects/backpack-survivor/content-expansion-fire-rate-boost.md)
- 项目中使用：[第 23 课：精英宝箱与终局压力强化](../projects/backpack-survivor/elite-chests-endgame-pressure.md)
- 项目中使用：[第 24 课：金币掉落与局内经济 HUD](../projects/backpack-survivor/gold-drops-and-economy-hud.md)
- 项目中使用：[第 25 课：背包价值与物品价值显示](../projects/backpack-survivor/backpack-value-and-item-value-display.md)
- 项目中使用：[第 26 课：合并升级收益兑现](../projects/backpack-survivor/merge-upgrade-reward-payoff.md)
- 项目中使用：[第 27 课：数值调参台与首轮平衡](../projects/backpack-survivor/balance-tuning-and-first-playtest.md)
- 项目中使用：[第 28 课：旋转邻接方向修正](../projects/backpack-survivor/rotation-adjacency-direction-fix.md)
- 项目中使用：[第 29 课：武器稀有度与等级差异](../projects/backpack-survivor/weapon-rarity-and-level-scaling.md)
- 项目中使用：[第 30 课：攻击芯片效果实装](../projects/backpack-survivor/attack-damage-chip-effect.md)
- 项目中使用：[第 31 课：物品图标与背包可读性](../projects/backpack-survivor/item-icons-and-backpack-readability.md)
- 项目中使用：[第 32 课：主菜单与场景流](../projects/backpack-survivor/main-menu-and-scene-flow.md)
- 项目中使用：[第 33 课：场景氛围与演示包装](../projects/backpack-survivor/scene-atmosphere-and-demo-polish.md)
- 项目中使用：[第 34 课：完整 15 分钟通关验收](../projects/backpack-survivor/full-run-acceptance.md)
- 项目中使用：[第 35 课：Profiler 快扫与低风险优化](../projects/backpack-survivor/profiler-sweep-and-low-risk-optimization.md)
- 项目中使用：[第 36 课：Build 与演示包](../projects/backpack-survivor/build-and-demo-package.md)
- 项目中使用：[第 37 课：升级候选池模块](../projects/backpack-survivor/level-up-option-pool.md)
- 项目中使用：[第 38 课：邻接效果架构升级](../projects/backpack-survivor/adjacency-effect-architecture.md)
- 项目中使用：[第 39 课：背包构筑效果扩展](../projects/backpack-survivor/backpack-build-effects-extension.md)
- 项目中使用：[第 40 课：内容池扩展与价值平衡](../projects/backpack-survivor/content-pool-and-value-balance.md)
- 项目中使用：[第 41 课：基础音频系统与 BGM](../projects/backpack-survivor/audio-system-and-bgm.md)
- 项目中使用：[第 42 课：设置菜单与基础选项](../projects/backpack-survivor/settings-menu-and-basic-options.md)
- 项目中使用：[第 43 课：敌人寻路与群体移动优化](../projects/backpack-survivor/enemy-movement-steering.md)
- 项目中使用：[第 44 课：远程敌人与波次混编](../projects/backpack-survivor/ranged-enemies-and-wave-mix.md)
- 项目中使用：[第 45 课：本地存档与最高纪录](../projects/backpack-survivor/local-save-and-records.md)
- 项目中使用：[第 46 课：V0.3 Release 文案与发布验收](../projects/backpack-survivor/v0.3-release-notes.md)
- 项目记录：[Bug 记录簿](../projects/backpack-survivor/bug-log.md)
- 项目记录：[性能优化记录](../projects/backpack-survivor/performance-optimization-log.md)
- 阶段复盘：[Backpack Survivor V0.1](../reviews/2026/backpack-survivor-v0.1-review.md)
- 阶段复盘：[Backpack Survivor V0.3 内容深度、反馈与留存](../reviews/2026/backpack-survivor-v0.3-review.md)
- 当前阶段：V0.3.11，项目中使用，已整理至第 46 课；V0.3 Release、Build、Profiler 和试玩结论来自用户阶段复盘，本环境未重新运行 Unity / Profiler / Windows Build
- 下一步：把 V0.3 压缩成作品集与面试表达；项目后续优先围绕内容深度、经济出口、构筑展示和可验证性能数据推进。第 6 课工程 hygiene 资料收到后再补入库

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
