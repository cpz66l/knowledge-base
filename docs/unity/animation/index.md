# 动画系统

> Unity 动画方案全景 — Animation · Animator · Timeline · DOTween

---

## 学习路线

```
阶段一 ──→ 阶段二 ──→ 阶段三 ──→ 阶段四
Animation    Animator    Timeline    程序化动画
(1天)        (3~5天)     (2天)       (3~4天)
```

> 四种方案不是替代关系，而是不同场景适用不同工具。实际项目中经常组合使用。

---

## 阶段一：Animation 组件

> Unity 最原始的动画系统。先理解它，才能理解 Animator 为什么要进化。

| 主题 | 要点 | 优先级 |
|------|------|--------|
| **Animation Clip** | 动画剪辑概念、关键帧、曲线编辑、Loop/循环 | 🔴 必学 |
| **Animation 组件** | 挂载 Clip、自动播放、Play() 方法 | 🔴 必学 |
| **Animation Event** | 在某一帧触发函数回调（脚步声、攻击判定） | 🔴 必学 |
| **AnimationCurve** | 代码中使用曲线、自定义曲线序列化 | 🟡 了解 |

**练习**：用 Animation 组件做一个"宝箱打开"动画 — 旋转盖子 + 触发 Animation Event 播放音效 + 粒子。

---

## 阶段二：Mecanim Animator

> Unity 主力动画系统，基于状态机。角色动画的核心方案。

| 主题 | 要点 | 优先级 |
|------|------|--------|
| **Animator 组件** | Avatar、Controller 指定、Apply Root Motion、Update Mode | 🔴 必学 |
| **Animator Controller** | 状态机界面、创建/删除状态和过渡 | 🔴 必学 |
| **参数 (Parameters)** | Float/Int/Bool/Trigger 四种类型、SetFloat/SetBool 等 API | 🔴 必学 |
| **过渡条件** | Has Exit Time、Conditions、Transition Duration、Interruption Source | 🔴 必学 |
| **Blend Tree** | 1D Blend(速度→走/跑)、2D Blend(角度+速度)、Direct Blend | 🟡 进阶 |
| **子状态机** | 嵌套状态机组织复杂逻辑 | 🟡 进阶 |
| **层 (Layers)** | 多轨道叠加(下半身跑 + 上半身开枪)、Avatar Mask 遮罩 | 🟡 进阶 |
| **StateMachineBehaviour** | 状态机上挂脚本、OnStateEnter/OnStateExit 回调 | 🟡 进阶 |
| **IK / Animation Rigging** | 脚部适配地形、手部瞄准、Multi-Aim/Rig 组件 | 🟢 可选 |
| **Root Motion** | 动画驱动物体移动、旋转 | 🟢 可选 |

**练习**：做一个第三人称角色控制器 — Idle/Walk/Run/Jump 状态机 + 速度控制 Blend Tree，上下半身分层。

---

## 阶段三：Timeline

> 非线性动画编辑，适合过场动画、CG 演出、游戏内剧情编排。

| 主题 | 要点 | 优先级 |
|------|------|--------|
| **Playable Director** | Timeline 播放总控、Play/Pause/Stop 方法 | 🔴 必学 |
| **Animation Track** | 直接控制 GameObject 的 Transform/Animator | 🔴 必学 |
| **Activation Track** | 控制 GameObject 的显示/隐藏 | 🔴 必学 |
| **Signal Track** | 在时间点触发自定义函数（对话显示、场景加载） | 🟡 进阶 |
| **Cinemachine 集成** | 运镜切换、Virtual Camera 绑定到 Timeline | 🟡 进阶 |
| **自定义 Playable Track** | 扩展 Timeline 实现自定义行为 | 🟢 可选 |

**练习**：做一个"开门进入房间"过场 — 镜头推进 + 门打开 + 灯亮起 + 对话信号触发。

---

## 阶段四：程序化动画 (DOTween)

> 代码驱动的 Tween 动画，无需预录制 Clip。UI 动画、简单物体动画的主力方案。

| 主题 | 要点 | 优先级 |
|------|------|--------|
| **核心方法** | DOMove/DORotate/DOScale/DOFade/DOPunch/DOShake | 🔴 必学 |
| **链式调用** | SetEase、SetDelay、SetLoops、OnComplete、OnUpdate | 🔴 必学 |
| **Sequence** | Append/Join/Insert/Prepend 编排多个动画 | 🔴 必学 |
| **Ease 曲线** | Ease.InOutQuad/Cubic/Elastic/Bounce 等效果对比 | 🟡 进阶 |
| **DOTween Path** | 沿路径运动、LookAt 朝向 | 🟢 可选 |
| **UI 动画** | 按钮 Hover/Click 反馈、窗口弹出/淡入、列表项入场 | 🟡 进阶 |

**练习**：做一个"卡牌翻转"效果 — 卡牌旋转 180 度 + 缩放弹入 + UI 面板弹性弹出。

---

## 四种方案对比

| | Animation | Animator | Timeline | DOTween |
|------|------|------|------|------|
| **适用场景** | 单一物体的简单动画 | 角色动画、状态驱动 | 过场、CG、多物体编排 | UI 动画、代码驱动补间 |
| **编辑方式** | 录制/手动关键帧 | 状态机可视化 | 时间线拖拽 | 纯代码 |
| **学习门槛** | ⭐ 低 | ⭐⭐⭐ 中高 | ⭐⭐ 中 | ⭐⭐ 中 |
| **运行性能** | 一般 | 较高(优化后) | 一般 | 高 |

---

> 📎 标签：`Animation` `Animator` `Timeline` `DOTween` `Mecanim`
