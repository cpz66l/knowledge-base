# Text (TextMeshPro)

> 比 Legacy Text 更清晰的现代文字系统 - SDF 渲染，任意缩放不糊。

---

## 是什么

TextMeshPro（TMP）是 Unity 推荐的文字方案，用 **SDF（Signed Distance Field）** 渲染文字，任意字号/缩放下都保持清晰锐利，且富文本、字间距、描边阴影等功能远强于旧版 Text。

---

## 首次使用

导入 TMP 资源：菜单 `Window` -> `TextMeshPro` -> `Import TMP Essentials`。

!!! warning "没导入会怎样"
    不导入 TMP Essentials 时，新建的 TextMeshPro 控件会显示成粉色方块（材质丢失）。导入后即恢复正常。

---

## 关键属性

| 属性 | 说明 |
|------|------|
| **Text** | 显示的文字内容，支持富文本 |
| **Font Asset** | 字体资源（TMP 专用，非旧版 Font） |
| **Font Size** | 字号 |
| **Auto Size** | 自动收缩字号以适配容器 |
| **Rich Text** | 开启富文本标签 |
| **Alignment** | 对齐方式（左/中/右 + 上/中/下） |
| **Wrapping** | 自动换行 |
| **Overflow** | 溢出处理（Overflow 溢出 / Truncate 截断 / Ellipsis 省略号） |

---

## 富文本标签

开启 Rich Text 后可在文本里用标签控制样式：

| 标签 | 作用 | 示例 |
|------|------|------|
| `<b>` `<i>` | 加粗 / 斜体 | `<b>粗体</b>` |
| `<size=N>` | 指定字号 | `<size=50>大字</size>` |
| `<color=#RRGGBB>` | 指定颜色 | `<color=#FF0000>红字</color>` |
| `<u>` `<s>` | 下划线 / 删除线 | `<u>下划线</u>` |

组合示例：

```
<size=40><b>体力</b></size> <color=#00FF00>100/100</color>
```

---

## 代码控制

```csharp
using TMPro;
using UnityEngine;

public class TMPDemo : MonoBehaviour
{
    public TextMeshProUGUI hpText;   // Canvas 上的 TMP 文本

    void Start()
    {
        // 直接赋值文字（含富文本）
        hpText.text = "<b>HP</b>: <color=#00FF00>100</color>";

        // 取值
        Debug.Log(hpText.text);
    }
}
```

!!! note "两个 TMP 组件别混用"
    - `TextMeshProUGUI`：用在 Canvas 上的 UI 文本
    - `TextMeshPro`：用在 3D 世界空间（World Space）的文本

---

## 常见坑

- **中文显示方块/缺失**：默认 TMP 字体不含中文，需用 `Window -> TextMeshPro -> Font Asset Creator` 生成含中文字符的动态字体资源，或导入中文字体
- **粉色方块**：忘导入 TMP Essentials（见上文）
- **字号模糊**：旧版 Text 缩放易糊，换 TMP 即解决

---

## 核心技巧

- 新项目一律用 TMP，别再用旧版 Text
- 中文字体单独生成 Font Asset（动态 SDF）
- 富文本做"数字变色""关键字加粗"等提示

---

> 📎 标签：`UGUI` `TextMeshPro` `SDF` `富文本`
