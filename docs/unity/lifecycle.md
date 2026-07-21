# Unity 生命周期：初始化、启用与禁用

> 状态：已在 Backpack Survivor 项目中应用；完整调用顺序矩阵仍待独立实验

## 学习目标

- 区分一次性初始化、每次启用、首帧启动、逐帧更新与清理阶段。
- 让事件订阅、注册表和对象池复用使用匹配的生命周期。
- 不把常见的项目约定误写成 Unity 在所有场景下都保证的顺序。

## 当前理解

对于一个正常激活、启用的 `MonoBehaviour` 实例，最常用的主线可以先记成：

```text
Awake
  ↓
OnEnable
  ↓
Start
  ↓
Update ...
  ↓
LateUpdate ...
  ↓
OnDisable
  ↓
OnDestroy（真正销毁时）
```

这张图只表示常见主线，不覆盖切场景、运行时实例化、脚本禁用、对象从未激活、编辑器脚本重载和应用退出等所有分支。不同对象的同名回调之间也不应依赖默认先后顺序；确有依赖时，优先改成显式初始化或依赖注入，其次才考虑 Script Execution Order。

## 回调职责

| 回调 | 调用特征 | 适合承担 | 常见风险 |
|---|---|---|---|
| `Awake` | 每个实例一次，早于该实例第一次 `OnEnable` | 缓存自身组件、建立不依赖外部顺序的内部状态 | 假设其他对象已经完成初始化 |
| `OnEnable` | 每次组件启用且对象激活时调用 | 注册服务、订阅本次激活期间需要的事件、启动可重复行为 | 重复订阅、依赖尚未准备的外部服务 |
| `Start` | 第一次启用后、首个 `Update` 前调用一次 | 需要在首帧前完成的一次性跨对象连接 | 误以为对象池再次启用时会重跑 |
| `Update` | 启用期间通常每帧调用 | 输入、非物理逐帧逻辑、状态推进 | 每帧查找组件或创建临时对象 |
| `LateUpdate` | 本帧 `Update` 阶段之后 | 相机跟随、依赖本帧最终姿态的瞄准或表现 | 多个 `LateUpdate` 继续争夺同一 Transform |
| `OnDisable` | 组件禁用、对象停用或销毁流程中可能调用 | 注销、取消本次激活期订阅、停止可重复行为 | 从未启用的对象、脚本重载等边界未经测试 |
| `OnDestroy` | 实例真正销毁时调用，不用于普通池化归还 | 释放实例终身资源、最后清理 | 池对象只停用不销毁，因此不会在每次归还时调用 |

## 项目应用 1：Awake 缓存自身组件

[Backpack Survivor 的敌人 AI](../projects/backpack-survivor/enemy-ai-and-melee.md)在 `Awake` 缓存同对象上的组件：

```csharp
private void Awake()
{
    characterController = GetComponent<CharacterController>();
    health = GetComponent<Health>();
}
```

这种写法减少逐帧 `GetComponent`，也让后续 `OnEnable` 可以使用已经缓存的 `health`。

“Awake 只碰自己，Start 才碰别人”可以作为降低时序耦合的团队约定，但不是必须遵守的引擎规则。跨对象依赖是否安全，取决于依赖建立方式和对象的创建时机；显式传入引用通常比猜测不同对象的回调顺序更可靠。

## 项目应用 2：启用期间登记，禁用时注销

[目标注册表](../projects/backpack-survivor/target-registry-and-auto-weapon.md)让敌人在激活期间可被索敌：

```csharp
private void OnEnable()
{
    TargetRegistry.Register(health);
}

private void OnDisable()
{
    TargetRegistry.Unregister(health);
}
```

这组对称关系比 `Awake` / `OnDestroy` 更适合反复启用和停用的对象。前提是注册与注销都具有幂等性：重复调用不会加入重复项，也不会因目标已移除而失败。

## 项目应用 3：Update 后再修正枪口朝向

角色身体在 `Update` 中转向，武器在 `LateUpdate` 中设置枪口朝向：

```csharp
private void LateUpdate()
{
    // 读取身体在本帧 Update 后的最终姿态，再设置枪口世界旋转
}
```

这适合“先更新主体，再更新依附表现”的依赖。但同一 Transform 最好只有一个明确所有者；如果动画、武器和相机都在后期回调中写同一节点，仅更换回调并不能消除竞争。

## 对象池中的关键区别

`Awake` 和 `Start` 都是实例级的一次性阶段；`OnEnable` 和 `OnDisable` 才会随 `SetActive` 反复出现。因此对象池需要把状态分成两类：

```text
实例终身只做一次
  ├─ 缓存组件
  ├─ 创建不变资源
  └─ 建立实例级结构

每次取出/归还都要做
  ├─ 重置生命值、计时器和目标
  ├─ 注册/注销外部服务
  ├─ 恢复/取消激活期事件订阅
  └─ 清理协程、特效与外部引用
```

项目当前暴露了一个典型边界：敌人在 `Start` 中订阅死亡事件，在死亡时退订并 `SetActive(false)`。再次启用时 `Start` 不会重跑，死亡处理不会自动恢复；生命值的死亡状态也仍需重置。只把 `Destroy` 改成 `SetActive(false)` 还不等于完成对象池。

## 常见错误

### 重复订阅

```csharp
private void OnEnable()
{
    health.OnDeath += Die;
}

private void OnDisable()
{
    health.OnDeath -= Die;
}
```

如果采用这组写法，必须保证每次启用只订阅一次，并考虑发布者是否可能先于订阅者销毁。若事件需要覆盖实例整个生命期，也可以选择一次性订阅，但必须让退订阶段与真实生命期一致。

### 在 Start 中放置每次复用都需要的初始化

`Start` 只执行一次。对象池的生命值重置、目标清空和计时器复位不能只放在 `Start`，应由明确的 `ResetForReuse` / `Initialize` 协议或 `OnEnable` 驱动。

### 假设所有 Awake 都绝对早于所有 Start

初始场景加载中的常见顺序不代表运行时任何时刻都可以依赖“全场所有对象已 Awake”。运行时实例化的新对象会立即进入自己的初始化流程，可能发生在其他对象已经开始更新之后。需要跨对象顺序时，应建立显式入口。

### 把 OnDisable 当成只在手动 SetActive(false) 时调用

组件禁用、父对象停用、销毁、脚本重载和退出流程都可能影响禁用回调。清理逻辑应可重复、尽量不依赖其他对象仍然存在，并在目标平台和编辑器配置下验证。

## 如何验证

建立一个独立测试场景，为每个回调记录实例 ID、帧号和启用状态，然后覆盖：

- 场景初始激活对象与初始禁用对象。
- 运行时 `Instantiate` 激活和非激活 Prefab。
- 单独切换组件 `enabled` 与切换整个对象 `SetActive`。
- 反复取出、归还同一个池对象。
- 销毁激活对象、禁用对象以及从未激活的对象。
- 切场景、退出 Play Mode，并分别测试开启和关闭 Domain Reload。
- 两个脚本同时修改同一 Transform 时的 `Update` / `LateUpdate` 顺序。

目前 Backpack Survivor 已提供 `Awake` 缓存、`OnEnable` / `OnDisable` 注册和 `LateUpdate` 瞄准的实践记录，但尚未完成上述独立调用顺序矩阵，因此边界仍标记为待验证。

## 相关内容

- [敌人追击、近战与死亡流程](../projects/backpack-survivor/enemy-ai-and-melee.md)
- [目标注册表、自动武器与投射物](../projects/backpack-survivor/target-registry-and-auto-weapon.md)
- [委托与事件](../csharp/oop/delegates-and-events.md)
- [对象池](../performance/memory/object-pool.md)

> 📎 标签：`Unity` `生命周期` `Awake` `Start` `OnEnable` `OnDisable` `LateUpdate` `对象池`
