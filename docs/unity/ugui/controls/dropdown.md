# Dropdown

> 下拉选择 - 收起显示当前项，展开列表选一项。

---

## 是什么

Dropdown 收起时显示当前选中项，点击展开一个列表供选择。展开的列表是一个 `Template`（模板）子对象，含 ScrollRect + 若干 Toggle 项。

!!! note "TMP 版本"
    用 TextMeshPro 的项目选 `Dropdown (TextMeshPro)`（`TMP_Dropdown`），文字渲染才清晰。普通 Dropdown 用旧版 Text。

---

## 关键属性

| 属性 | 说明 |
|------|------|
| **Template** | 展开列表的模板（子对象，默认已建好） |
| **Caption Text** | 收起时显示当前项的文字 |
| **Item Text** | 列表项的文字 |
| **Options** | 选项列表（OptionData，含 text + 可选 sprite） |
| **Value** | 当前选中项的索引（0 开始） |
| **On Value Changed (Int32)** | 选项变化事件，参数是新索引 |

---

## 代码控制

```csharp
using UnityEngine;
using UnityEngine.UI;

public class DropdownDemo : MonoBehaviour
{
    public Dropdown dropdown;   // 用 TMP 时换成 TMP_Dropdown

    void Start()
    {
        // 动态添加选项
        dropdown.options.Add(new Dropdown.OptionData { text = "新选项" });

        // 监听选择变化，参数 int = 新索引
        dropdown.onValueChanged.AddListener(index =>
        {
            Debug.Log("选择了第 " + index + " 项：" + dropdown.options[index].text);
        });

        // 代码设置当前选中
        dropdown.value = 2;
        dropdown.RefreshShownValue();   // 刷新显示
    }
}
```

---

## 常见坑

- **点不开列表**：Template 被删或没赋值，Dropdown 展不开
- **中文显示方块**：普通 Dropdown 用旧版 Text 不含中文字体 -> 改用 TMP_Dropdown + 中文字体资源
- **改了 value 不更新显示**：代码设值后调 `RefreshShownValue()` 刷新
- **清空选项**：`dropdown.ClearOptions()`，再 `RefreshShownValue()`

---

## 核心技巧

- TMP 项目用 TMP_Dropdown
- 动态选项用 `options.Add` / `ClearOptions`
- 代码改值后 `RefreshShownValue()` 刷新显示

---

> 📎 标签：`UGUI` `Dropdown` `下拉选择` `TMP_Dropdown`
