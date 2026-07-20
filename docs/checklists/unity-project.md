# Unity 项目能力检查清单

> 用于检查 Unity 知识是否已经落到可运行项目中。未学习的系统保持未勾选。

---

## 核心系统

- [ ] 能解释当前项目中关键 MonoBehaviour 的生命周期顺序
- [ ] 能正确选择 Prefab、ScriptableObject 和普通 C# 对象
- [ ] 资源加载和释放有明确的所有者
- [ ] UI 不依赖无必要的每帧轮询
- [ ] 场景切换时静态状态、事件和异步任务得到处理

## 数据与依赖

- [ ] 配置数据与运行时状态区分清楚
- [ ] 模块依赖方向能够用一张图说明
- [ ] 不依赖大量隐式全局单例完成通信
- [ ] 事件订阅和取消订阅能够成对追踪
- [ ] Inspector 引用、运行时查找和资源加载的选择有理由

## 验证与发布

- [ ] 核心流程有最小测试或可重复验证步骤
- [ ] 使用 Profiler 检查过至少一个真实场景
- [ ] 记录目标平台和关键性能预算
- [ ] Build 后验证过功能，而不只在 Editor 中运行
- [ ] 项目问题已经写入复盘，而不是只保留在记忆中

## 实践证据

- 项目：[Backpack Survivor](../projects/backpack-survivor/index.md)
- 当前证据：[伤害管线与危险区](../projects/backpack-survivor/damage-pipeline-and-hazard-zone.md)，已记录接口、事件、Trigger 缓存和基础运行观察。
- 尚缺证据：Profiler 数据、目标平台 Build、多 Collider、低帧率和销毁对象测试。
- 下一项改进：敌人系统接入 `IDamageable`，首次验证 `OnDeath` 的订阅与取消订阅。
