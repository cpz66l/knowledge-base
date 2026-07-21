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
- 当前阶段：V0.1 战斗核心原型
- 已记录：[第 1 课：伤害管线与危险区](../projects/backpack-survivor/damage-pipeline-and-hazard-zone.md)
- 已记录：[第 2 课：敌人追击、近战与死亡流程](../projects/backpack-survivor/enemy-ai-and-melee.md)
- 已记录：[第 3 课：目标注册表、自动武器与投射物](../projects/backpack-survivor/target-registry-and-auto-weapon.md)
- 下一步：主动武器接入；随后修复对象复用、静态注册表与物理查询边界

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
