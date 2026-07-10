# Toggle（单选与多选）

> 开关控件 - 复选框 / 单选按钮全靠它 + Toggle Group。

---

## 是什么

Toggle 是一个开关控件，核心是 `isOn` 布尔值和 `OnValueChanged` 事件。配合 `Toggle Group` 组件，能实现**多选（复选框）**和**单选（单选按钮）**两种模式。

---

## 关键属性

| 属性 | 说明 |
|------|------|
| **Is On** | 当前是否选中（`isOn`） |
| **Toggle Transition** | 切换时的过渡效果（Fade 淡入淡出） |
| **Graphic** | 勾选标记的 Image（默认是个 ✓ 图标） |
| **Group** | 所属的 Toggle Group（留空 = 多选模式） |
| **On Value Changed (Boolean)** | 值变化事件，参数是新 `isOn` |

---

## 多选（复选框）

每个 Toggle 独立，不设 Group，各自维护 `isOn`。典型：设置菜单的"全屏""音效"等独立开关。

```csharp
using UnityEngine;
using UnityEngine.UI;

public class MultiToggleDemo : MonoBehaviour
{
    public Toggle fullscreenToggle;
    public Toggle soundToggle;

    void Start()
    {
        // 监听变化，参数 bool = 新的 isOn
        fullscreenToggle.onValueChanged.AddListener(isOn =>
        {
            Debug.Log("全屏：" + isOn);
        });

        soundToggle.onValueChanged.AddListener(isOn =>
        {
            Debug.Log("音效：" + isOn);
        });
    }
}
```

---

## 单选（单选按钮）

在父节点挂 `Toggle Group` 组件，把同组各 Toggle 的 `Group` 指向它。**同组内只能有一个 Toggle 处于选中状态**，选新的会自动取消旧的。典型：难度选择、画质档位。

```
DifficultyPanel (Toggle Group)
  ├─ Easy (Toggle, Group = DifficultyPanel)
  ├─ Normal (Toggle, Group = DifficultyPanel)
  └─ Hard (Toggle, Group = DifficultyPanel)
```

```csharp
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class SingleToggleDemo : MonoBehaviour
{
    public ToggleGroup difficultyGroup;

    public void ConfirmDifficulty()
    {
        // 取当前选中的 Toggle
        IEnumerable<Toggle> active = difficultyGroup.ActiveToggles();
        foreach (Toggle t in active)
        {
            Debug.Log("选择了：" + t.name);
            break;   // 单选组里通常只有一个
        }
    }
}
```

| API | 作用 |
|------|------|
| `toggle.isOn` | 读 / 写选中状态 |
| `toggle.onValueChanged.AddListener(Action<bool>)` | 监听值变化 |
| `group.ActiveToggles()` | 取组内当前选中的 Toggle |
| `group.SetAllTogglesOff()` | 全部取消选中 |

!!! tip "Toggle Group 的 Allow Switch Off"
    默认单选组总有一个被选中。若想允许"全部不选"，勾选 Toggle Group 的 `Allow Switch Off`。

---

## 常见坑

- **单选不生效**：Toggle 的 `Group` 字段没拖进去，变成各自独立多选
- **多个同时选中**：没用 Group，或 Group 没生效
- **取值时机**：`OnValueChanged` 触发时，参数 `isOn` 是**新值**，直接用参数别去读旧状态
- **初始状态混乱**：单选组里多个 Toggle 都勾了 Is On，运行时只保留一个。手动只勾一个

---

## 核心技巧

- 独立开关 -> 不设 Group（多选）
- 互斥选项 -> 同父挂 Toggle Group，各 Toggle 指向它（单选）
- 用 `OnValueChanged` 的 `bool` 参数拿新值，别去读 `isOn`

---

> 📎 标签：`UGUI` `Toggle` `ToggleGroup` `单选` `多选`
