# 图形学

> 实时渲染基础与 Unity Shader 编程 — 管线 · 光照 · PBR · 阴影

---

## 学习定位

> 路线：专项能力，按项目需求进入
> 前置：Unity 基础；数学与 Shader 语法按实际进度补充
> 路线入口：[专项能力路线](../roadmap/specializations.md)
> 掌握检查：[专项能力清单](../checklists/specializations.md)

未做过画面实验或工具验证的内容保持“学习中”，不要只凭概念文章标记完成。

---

## 目录

| 文章 | 内容 |
|------|------|
| [渲染管线](rendering-pipeline.md) | 应用阶段、几何阶段、光栅化、逐片元 |
| [Shader 基础](shader-basics.md) | HLSL/ShaderLab 语法、顶点/片元着色器 |
| [光照与着色](lighting-and-shading.md) | Lambert、Blinn-Phong、法线贴图 |
| [PBR 理论](pbr-theory.md) | BRDF、金属度/粗糙度工作流、IBL |
| [阴影技术](shadow-techniques.md) | Shadow Map、CSM、软阴影 |

---

## 最小闭环

```text
理解管线位置 → 修改 Shader / 参数 → 观察画面 → 使用工具验证 → 记录成本与限制
```
