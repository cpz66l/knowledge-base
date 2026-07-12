# Button 与点击事件

> 可点击交互 - 包装 Image + 文字 + onClick 事件。

---

## 是什么

Button 是最常用的交互控件，本质上是一个可点击的容器（自带 Image + 子级文字）。核心是 `onClick` 事件 -- 点击时触发你绑定的方法。

---

## 关键属性

| 属性 | 说明 |
|------|------|
| **Interactable** | 是否可交互（false 时变灰、不响应点击） |
| **Transition** | 状态切换效果（Color Tint 颜色 / Sprite Swap 换图 / Animation 动画） |
| **Navigation** | 键盘/手柄焦点导航方向 |
| **OnClick** | 点击事件列表（UnityEvent） |

---

## 绑定点击事件（两种方式）

### 方式一：Inspector 拖拽

1. 选中 Button，Inspector 找到 `Button (Script)` -> `On Click ()`
2. 点 `+` 新增一项
3. 把含目标脚本的对象拖入 `Object` 槽
4. 下拉选择要调用的方法（必须是参数签名兼容的 `public` 实例方法）

!!! note "为什么找不到方法"
    `[SerializeField]` 只能让私有字段参与序列化，不能让私有方法出现在事件下拉框中。需要调用私有逻辑时，可以提供一个 `public` 包装方法，或者在代码中使用 `onClick.AddListener` 绑定该方法。方法参数还必须与 Button 的 `UnityEvent` 签名兼容。

### 方式二：代码动态绑定

```csharp
using UnityEngine;
using UnityEngine.UI;

public class ButtonDemo : MonoBehaviour
{
    public Button startBtn;

    void Start()
    {
        // 绑定：点击时调用 OnStartClick
        startBtn.onClick.AddListener(OnStartClick);

        // 也可用 Lambda 直接写逻辑
        startBtn.onClick.AddListener(() =>
        {
            Debug.Log("Lambda 形式点击");
        });
    }

    void OnStartClick()
    {
        Debug.Log("开始按钮被点击");
    }

    void OnDestroy()
    {
        // 销毁前移除监听，避免残留引用（好习惯）
        startBtn.onClick.RemoveListener(OnStartClick);
    }
}
```

| API | 作用 |
|------|------|
| `onClick.AddListener(action)` | 添加一个点击监听 |
| `onClick.RemoveListener(action)` | 移除指定监听 |
| `onClick.RemoveAllListeners()` | 清空所有监听 |
| `onClick.Invoke()` | 代码手动触发一次点击 |

---

## 常见坑

- **点了没反应**：99% 是场景缺 EventSystem（Canvas 创建时自动带，误删就没反应）
- **目标方法选不到**：方法不是 `public`，或目标对象没挂在场景里
- **监听重复叠加**：每次 `AddListener` 都会叠加，重复订阅会让一次点击触发多次。重订阅前先 `RemoveAllListeners()`
- **Interactable = false 时点击无效**：按钮变灰，事件不触发，排查时别漏这一项

---

## 核心技巧

- Inspector 拖拽适合静态 UI；动态生成的按钮用代码 `AddListener`
- 面板销毁前 `RemoveListener`，养成习惯
- 按钮状态切换用 Transition = Color Tint 最省事

---

> 📎 标签：`UGUI` `Button` `onClick` `UnityEvent`
