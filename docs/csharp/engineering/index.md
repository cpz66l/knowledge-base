# C# 工程实践路线

> 状态：项目驱动学习。此页只建立工程能力目录，不提前补写“最佳实践”结论。

## 学习顺序

1. MonoBehaviour 与纯 C# 类的职责划分
2. 数据、状态、依赖与模块边界
3. 日志、断言、异常和失败流程
4. 命名空间、目录结构与程序集
5. 可测试性、单元测试与回归验证
6. Editor、Build、IL2CPP 与平台差异

## 已有入口

- [C# 工程能力清单](../../checklists/csharp-engineering.md)
- [Unity 专题](../../unity/index.md)
- [Unity 项目能力清单](../../checklists/unity-project.md)
- [项目复盘模板](../../reviews/project-review-template.md)

## 已有实践证据

- [Backpack Survivor：伤害管线与危险区](../../projects/backpack-survivor/damage-pipeline-and-hazard-zone.md)：接口边界、事件发布、伤害数据包、Trigger 缓存和防御式处理。
- [Backpack Survivor：敌人追击、近战与死亡流程](../../projects/backpack-survivor/enemy-ai-and-melee.md)：组件依赖、条件状态分支、跨对象查找缓存和一次性死亡事件闭环。
- [Backpack Survivor：目标注册表、自动武器与投射物](../../projects/backpack-survivor/target-registry-and-auto-weapon.md)：静态注册表、生命周期对称、热路径缓冲区和灰盒实现的演进边界。

## 最小产出

- 一张模块依赖图
- 一个可脱离场景测试的纯 C# 模块
- 一次 Build 环境验证
- 一份真实工程问题复盘
