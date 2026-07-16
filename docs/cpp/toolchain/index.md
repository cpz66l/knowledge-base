# 构建、链接与调试

> 会写语法不等于会做 C++ 工程。编译单元、库、CMake、ABI、警告和 Sanitizer 是开发与排错的基本功。

---

## 1. 从源码到程序

```text
源文件
  ↓ 预处理（#include、宏、条件编译）
翻译单元
  ↓ 编译
目标文件（.obj / .o）
  ↓ 链接
可执行文件或静态/动态库
```

常见错误定位：

| 阶段 | 常见信息 | 优先检查 |
|------|----------|----------|
| 编译 | 类型不匹配、名称不存在、模板实例化失败 | 语法、头文件、作用域、约束 |
| 链接 | unresolved external / undefined reference | 缺少定义、库未链接、签名不一致 |
| 链接 | multiple definition / already defined | 头文件中重复定义、ODR 违规 |
| 运行 | 崩溃、数据损坏、随机行为 | 生命周期、越界、数据竞争、ABI |

---

## 2. 头文件、编译单元与 ODR

- 头文件放声明、模板定义、`inline` 函数和必要的类型定义
- `.cpp` 放非模板函数和全局对象的单一定义
- 头文件使用 `#pragma once` 或 include guard
- 能前向声明时可减少依赖，但按值成员、继承和需要完整布局时必须包含完整定义
- One Definition Rule（ODR）要求某些实体在整个程序中只能有一个定义，或所有允许的多重定义保持一致

!!! warning "不要在头文件滥用 using namespace"
    头文件中的 `using namespace std;` 会污染所有包含者的名称空间，容易造成冲突。示例代码也尽量写出 `std::`。

---

## 3. CMake：以 target 为中心

最小项目：

```cmake
cmake_minimum_required(VERSION 3.24)
project(GameCore LANGUAGES CXX)

add_executable(game_core
    src/main.cpp
    src/world.cpp
)

target_compile_features(game_core PRIVATE cxx_std_20)
target_include_directories(game_core PRIVATE include)
```

推荐习惯：

- 使用 `target_*` 命令表达依赖，不使用全局 include/link 配置污染其他目标
- 区分 `PRIVATE`、`PUBLIC`、`INTERFACE` 依赖传播范围
- 使用 out-of-source build：构建产物不要混进源码目录
- 不在 CMakeLists 中硬编码某台电脑的绝对路径
- 依赖库优先提供标准 CMake config；包管理器可按项目选择 vcpkg 或 Conan

---

## 4. 静态库、动态库与 ABI

| 类型 | 特点 | 常见关注点 |
|------|------|------------|
| 静态库 | 链接时合入目标程序 | 体积、重复代码、链接时间 |
| 动态库 | 运行时加载 DLL/.so/.dylib | 导出符号、部署、版本与 ABI |

ABI 涉及名称修饰、调用约定、对象布局、异常、运行库和编译器版本等二进制约定。跨模块边界应避免随意传递：

- 不同编译器/运行库创建和释放的 STL 对象
- 布局可能变化的 C++ 类
- 未固定调用约定或导出宏的函数

跨语言或插件边界常使用稳定的 C ABI：

```cpp
extern "C" {
    int add_numbers(int a, int b);
}
```

这也是 Unity 原生插件常见的入口形式；C# 侧再通过 P/Invoke 调用。还需处理平台库命名、调用约定、结构体布局和内存所有权。

---

## 5. 编译器警告与静态检查

建议把警告当作开发反馈，而不是发布前才处理：

- MSVC：`/W4`，团队成熟后再评估 `/WX`
- Clang/GCC：`-Wall -Wextra -Wpedantic`
- 静态分析：clang-tidy、MSVC Code Analysis、IDE inspections
- 格式化：clang-format，避免在评审中争论机械格式

`-Werror` / `/WX` 在多平台、第三方依赖较多时要谨慎配置，通常只对自己的目标启用。

---

## 6. Sanitizer 与调试器

| 工具 | 主要发现的问题 |
|------|----------------|
| AddressSanitizer (ASan) | 越界、use-after-free、部分泄漏 |
| UndefinedBehaviorSanitizer (UBSan) | 多类未定义行为 |
| ThreadSanitizer (TSan) | 数据竞争（平台支持情况不同） |
| 调试器 | 断点、调用栈、内存、线程与寄存器状态 |

排错顺序建议：

1. 保留第一个错误现场，不要只看连锁报错的最后一条
2. 使用带调试符号的构建复现
3. 阅读调用栈，确认对象是否仍处于有效生命周期
4. 开启对应 Sanitizer
5. 写最小复现或回归测试

---

## 7. 测试与持续集成

- 单元测试覆盖纯算法、容器边界、资源生命周期和错误处理
- 集成测试覆盖库边界、文件、网络、线程和平台差异
- Debug、Release 和至少一个 Sanitizer 配置进入 CI
- 对随机崩溃保存日志、构建版本、符号文件和崩溃转储
- 性能优化前先建立基准，避免只凭直觉改代码

---

## 面试检查清单

- 编译错误与链接错误如何区分？
- 声明与定义有什么区别？ODR 是什么？
- 静态库与动态库的优缺点是什么？
- C++ 模板为什么影响编译时间和代码体积？
- ABI 不兼容会表现为什么问题？
- ASan、UBSan、TSan 分别解决什么问题？
- Debug 能运行而 Release 崩溃时，应优先怀疑什么？
- CMake 中 `PRIVATE`、`PUBLIC`、`INTERFACE` 的含义是什么？

---

## 推荐练习

1. 用 CMake 建立 `app + static library + tests` 三目标项目
2. 故意制造越界和 use-after-free，用 ASan 定位
3. 把一个简单 C++ 函数导出为 C ABI，并从 C# P/Invoke 调用
4. 在 Debug/Release 下比较断言、优化与调用栈差异

---

## 参考资料

- [CMake Tutorial](https://cmake.org/cmake/help/latest/guide/tutorial/index.html)
- [C++ Core Guidelines：Source files](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines#S-source)
- [Clang AddressSanitizer](https://clang.llvm.org/docs/AddressSanitizer.html)
- [Unity Native plug-ins](https://docs.unity3d.com/Manual/NativePlugins.html)

> 📎 标签：`C++` `CMake` `链接` `调试` `Sanitizer` `Unity Native Plug-in`
