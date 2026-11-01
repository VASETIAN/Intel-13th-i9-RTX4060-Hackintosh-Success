# 依赖版本与来源

## Tahoe 26 当前组合（2026-11-01）

当前为 26.7.1 / 25G241。基础扩展沿用下方版本，新增/切换情况如下；所有 Kernel/Add 条目的版本、启用状态、Darwin 范围与 Info.plist/可执行文件 SHA256 见 [当前驱动清单](../evidence/tahoe26-drivers.json)。启用条目共 33 项，不表示受不同内核范围约束的驱动会同时加载。

| 项目 | 当前版本及范围 | 来源与核验 |
|---|---|---|
| NVIDIA NVRM/NVRMFB/NVRMAGDC/NVAccel | 2.6.2，macOS 卷内扩展 | 安装与缓存元数据、10 月 30 日原机加载记录；[作者 2.6.2 发布页](https://github.com/nullmoth/nvidia-macos-driver/releases/tag/v2.6.2) |
| CpuTopologyRebuild | 2.0.2，Darwin 25.0.0–25.99.99 | [固定版本说明](https://github.com/b00t0x/CpuTopologyRebuild/blob/2.0.2/README.md)；保留无 -v 组合 |
| CpuTscSync | 1.1.2，Darwin 25.0.0–25.99.99 | [acidanthera/CpuTscSync](https://github.com/acidanthera/CpuTscSync)；按本机元数据记录，不猜测同名 release 资产 |
| AirportItlwmTahoe | 2.4.0，Darwin 25.0.0–25.99.99 | 安装前备份恢复的实际文件；[分支仓库](https://github.com/laobamac/itlwm)，未据名称猜测 Tahoe ZIP 地址 |
| AirportItlwm（Sequoia 项） | 2.4.0，Darwin 24.2.0–24.99.99 | 保留供对应内核范围使用，不作为 Tahoe 同时加载项 |
| AppleALC | 1.9.9 | 原版保留，音频未完整验收；SimpleHDA/CirrusAudioFixup 不在当前活动 EFI |

2026-11-01 读取作者 v2.6.2 release API，发布资产摘要为：

| 资产 | 发布页声明的 SHA256 |
|---|---|
| nullmoth-nvidia-2.6.2.tar.gz | `ce896ae6a870ad340b52e2d8df9accf7daa003943eb53304a85d238f7a13da11` |
| 1401-Mac-2.6.2.zip | `72a99f0859b5c0c89f580c71052c04f0b4ea627d68457fd18d61d3a555449428` |

这里记录发布服务器声明，不声称本次重新下载并验证了这两个归档；当前安装的四个扩展版本与加载证据单独核对。原机使用本地 DBG109 / 1.0.9 OpenCore，继续保留下文对构建来源的限制，不分发二进制。

下面为原始 Sequoia 15 安装阶段的材料，2.5.4、单核与“拓扑未启用”等描述仅属于该历史阶段，不能覆盖当前 Tahoe 组合。

## Sequoia 15 历史依赖

下列版本来自本机扩容前配置、扩展元数据及当时发布材料。它们用于记录本次组合，不代表当前最新推荐。下载前核对作者来源和实际 SHA256，不把压缩包放入 EFI 就视为已安装。

## 固定下载与校验和

| 材料 | 固定来源 | SHA256 |
|---|---|---|
| NVIDIA 驱动 2.5.4 | [作者发布页](https://github.com/nullmoth/nvidia-macos-driver/releases/tag/v2.5.4) · [tar.gz](https://github.com/nullmoth/nvidia-macos-driver/releases/download/v2.5.4/nullmoth-nvidia-2.5.4.tar.gz) | `648280bea54fa57809e3bf3b312bdb6709a00fa0292af3b37c665e111fe27eaa` |
| 1401 Mac 2.5.4 | [Mac ZIP](https://github.com/nullmoth/nvidia-macos-driver/releases/download/v2.5.4/1401-Mac-2.5.4.zip) | `945fb8c599a3bd631a07d624143cdbf0249d1b455cccc322a100c87f7f64fc8f` |
| AirportItlwm Sequoia 2.4.0 alpha RELEASE 738d4c6 | [发布页](https://github.com/laobamac/itlwm/releases/tag/v2.4.0-alpha) · [RELEASE ZIP](https://github.com/laobamac/itlwm/releases/download/v2.4.0-alpha/AirportItlwm-Sequoia-v2.4.0-RELEASE-alpha-738d4c6.zip) | `865d0096dc3dc36b4ac5f60a5896216bfde5774e2c1f175e66ac4761f834937e` |

1401 Mac ZIP 实际放在 `nullmoth/nvidia-macos-driver` 的 release 中，不应按应用名称猜测 `nullmoth/1401` 下的 Mac 下载地址。1401 是安装与配置工具，NVIDIA 系统扩展是它部署的驱动内容。

## OpenCore 构建来源限制

本机启动日志与本地工具显示 DBG109 / 1.0.9 系列构建标识；本地 `ocvalidate` 1.0.9 对项目配置通过。公开整理时官方 `1.0.9` release 网页及 API 返回 404，不能据此提供一个未经证实的同版本下载资产。

查证入口为 [OpenCore 官方仓库](https://github.com/acidanthera/OpenCorePkg)、[官方发布列表](https://github.com/acidanthera/OpenCorePkg/releases)及[配置文档源码](https://github.com/acidanthera/OpenCorePkg/blob/master/Docs/Configuration.tex)。本仓库不分发该本地构建二进制。优先保留自己的可用 EFI；使用其他构建必须重新验证，不能认为是完全相同的复现条件。

## 最终启用的扩展

| 分组 | 元数据版本 | 上游查证入口 |
|---|---|---|
| Lilu | 1.7.3 | [acidanthera/Lilu](https://github.com/acidanthera/Lilu) |
| VirtualSMC 及传感器插件 | 1.3.9 | [acidanthera/VirtualSMC](https://github.com/acidanthera/VirtualSMC) |
| RestrictEvents | 1.1.7 | [acidanthera/RestrictEvents](https://github.com/acidanthera/RestrictEvents) |
| WhateverGreen | 1.7.2 | [acidanthera/WhateverGreen](https://github.com/acidanthera/WhateverGreen) |
| AMFIPass | 1.4.1 | [Dortania 相关项目](https://github.com/dortania/OpenCore-Legacy-Patcher) |
| AppleALC | 1.9.9 | [acidanthera/AppleALC](https://github.com/acidanthera/AppleALC) |
| AirportItlwm | 2.4.0，Sequoia alpha 分支 | [laobamac/itlwm](https://github.com/laobamac/itlwm) |
| BlueToolFixup | 2.7.3 | [acidanthera/BrcmPatchRAM](https://github.com/acidanthera/BrcmPatchRAM) |
| IntelBTPatcher / IntelBluetoothFirmware | 2.5.0 | [OpenIntelWireless/IntelBluetoothFirmware](https://github.com/OpenIntelWireless/IntelBluetoothFirmware) |
| NVMeFix | 1.1.4 | [acidanthera/NVMeFix](https://github.com/acidanthera/NVMeFix) |
| USBToolBox / UTBDefault | 1.2.0 / 1.0 | [USBToolBox/kext](https://github.com/USBToolBox/kext) |
| XHCI-unsupported | 0.9.2 | 以所用生成工具附带版本与配置核对，非完整 USB 映射替代品 |
| VoodooI2C | 2.9.1 | [VoodooI2C/VoodooI2C](https://github.com/VoodooI2C/VoodooI2C) |
| VoodooPS2Controller 及插件 | 2.3.8 | [acidanthera/VoodooPS2](https://github.com/acidanthera/VoodooPS2) |
| Sinetek-rtsx | 9.0.0 | 读卡器扩展已配置；没有完整读卡器验收结论 |
| BrightnessKeys / YogaSMC | 1.0.4 / 1.5.3 | 对应笔记本功能配置记录，不等于全部功能通过 |

表中没有逐一确认每个元数据版本都存在同名独立 release 标签，因此不构造猜测下载链接。EFI 中文件存在与实际启用列表分开核对；最终没有启用 CpuTopologyRebuild、itlwm 或 NootedGreen。

## 其他一手技术资料

- [Dortania Windows 恢复介质准备](https://dortania.github.io/OpenCore-Install-Guide/installer-guide/windows-install.html)。
- [OpenCore 安装阶段说明](https://github.com/dortania/OpenCore-Install-Guide/blob/master/installation/installation-process.md)。
- [Apple macOS 安装说明](https://support.apple.com/102655)。
- [NullMoth 2.5.4 驱动说明](https://github.com/nullmoth/nvidia-macos-driver/blob/v2.5.4/README.md)。
- [1401 2.5.4 Mac 安装脚本](https://github.com/nullmoth/1401/blob/v2.5.4/mac/Resources/nullmoth-setup.sh)。
- [XNU 11417.140.69 的 CPU 参数读取](https://github.com/apple-oss-distributions/xnu/blob/xnu-11417.140.69/osfmk/i386/i386_init.c)。
- [ACPICA 20160930 区域处理](https://github.com/open-acpica/acpica/blob/R09_30_16/source/components/events/evregion.c)。
- [Mandiant macOS 统一日志解析器 0.7.0](https://github.com/mandiant/macos-UnifiedLogs/releases/tag/v0.7.0)。
- [CpuTopologyRebuild 2.0.2 作者说明](https://github.com/b00t0x/CpuTopologyRebuild/blob/2.0.2/README.md)。
- [OpenCore custom slide 实现](https://github.com/acidanthera/OpenCorePkg/blob/master/Library/OcAfterBootCompatLib/CustomSlide.c)。

公开软件资料解释技术机制，本机的实际结果仍以[最小证据摘要](../evidence/summary.json)与报告中的验证层级为准。
