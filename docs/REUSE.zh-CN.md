# 下次使用：从这里开始

整理日期：2026-11-26。技术基线仍是 **2026-11-01 机主确认可启动的 macOS Tahoe 26.7.1 / 25G241**，不是今天重新安装或重新验收过的系统。

本页把已有材料按再次使用的顺序串起来。全过程与失败经验见 [项目结项报告](PROJECT-CLOSEOUT.zh-CN.md)，原始细节保留在各专题文档中。

## 1 先分清要做哪件事

| 你的情况 | 应该使用的材料 | 不应照搬的旧流程 |
|---|---|---|
| 原来的 Tahoe 系统还在，只是 EFI 丢失或改坏 | 自己保存的私人完整 EFI、当前 Tahoe 配置与下面的只读检查 | Sequoia 单核配置、创建账户、重新分区 |
| 同一台电脑重新安装 macOS | 安装参考、版本清单、自己的 EFI/身份、目标磁盘的当前清单 | 旧 disk 编号、旧分区 UUID、旧扇区提取命令 |
| 想复现当时的升级路径 | 15 安装参考 → 本地账户替代说明（仅确有需要时）→ 26 升级故障记录 → 当前基线 | 未修正的升级脚本、同时更换多个驱动 |
| 想直接全新安装 Tahoe | 当前配置可作研究起点，但本项目没有验收过这条全新安装路径 | 把 15→26 原位升级成功写成 26 全新安装成功 |
| 用另一台同 CPU/显卡的电脑 | 硬件对照、上游资料、自己的 ACPI/USB/显卡线路分析 | 把本机 21J8/LRCN52WW 的固件补丁当通用补丁 |

本仓库可以重新取得修复说明、脱敏配置和原创源码；**不能仅下载仓库就恢复原来装好的系统、应用和个人设置**。

## 2 取得这份资料

打开 [GitHub 仓库](https://github.com/VASETIAN/Intel-13th-i9-RTX4060-Hackintosh-Success)，点击 **Code → Download ZIP**，解压到工作目录。Windows 本机项目约定使用 `D:\Codex`；macOS 可放在自己可写的目录。也可使用：

```text
git clone https://github.com/VASETIAN/Intel-13th-i9-RTX4060-Hackintosh-Success.git
cd Intel-13th-i9-RTX4060-Hackintosh-Success
python tools/validate_publication.py --self-test
python tools/validate_publication.py
```

macOS 通常把最后两行中的 `python` 换为自己安装的 `python3`。Python 仅用于这些检查，不是 OpenCore 启动的前提。`SHA256SUMS` 记录随仓库发布的文件完整性；Git 提交历史用于固定资料版本，它们不构成第三方签名认证。

## 3 选择正确的配置和组件

| 用途 | 配置 | 关键区别 |
|---|---|---|
| 当前最终技术基线 | [Tahoe 示例](../config/config.tahoe26.known-good.sample.plist) | 无 `cpus=1`、无 `-v`、无 `-nvoff`；拓扑/TSC 插件仅 Darwin 25 |
| 复查最初安装 | [Sequoia 历史示例](../config/config.pre-expansion.sample.plist) | 当时使用 `cpus=1`；不是最终性能配置 |

两份示例都不是完整可启动 EFI。依照 [配置说明](../config/README.md)使用：同机恢复优先保留自己已有的 SMBIOS 身份；更换机器时使用属于新配置的身份，不拿别人的序列号。公开样例的身份字段为空，不应直接覆盖实盘配置。

按 [依赖表](DEPENDENCIES.zh-CN.md)准备固定版本和 [驱动清单](../evidence/tahoe26-drivers.json)中的文件。当前还提供 [引导组件哈希清单](../evidence/tahoe26-boot-components.json)，覆盖 BOOT/OpenCore、启用的 ACPI 与 UEFI 驱动。哈希可以识别文件是否与历史原件一致，不能从哈希还原文件。

本机的 OpenCore 是本地 DBG109 / 1.0.9 构建。现有记录没有建立可确认的同版本官方发行下载来源；不能虚构链接或用任意新版冒充原件。完整复现优先使用自己保留的原件，改版需要重新验证。第三方 kext、NVIDIA 安装器和 Apple 系统安装资源按各自可信来源取得，仓库不重新分发。

## 4 先在副本里检查 EFI

将**自己的 EFI 副本**放入可读目录，例如 Windows 的 `D:\Codex\work\my-efi\EFI`，其中应有 `BOOT` 和 `OC`。在仓库目录运行：

```text
python tools/check_efi.py "D:\Codex\work\my-efi\EFI"
```

在 macOS 使用 `python3 tools/check_efi.py`，再拖入 EFI 副本文件夹并回车即可。这个工具：

- 对照 Tahoe 基线的配置内容；先在内存中忽略个人身份、蓝牙本机数据和本机专用菜单/工具，不输出这些值。
- 检查 33 个启用 kext 条目的 Info.plist/执行文件哈希，以及 BOOT/OpenCore、启用 ACPI、UEFI 驱动的路径、大小和哈希。
- 拒绝越出 EFI 目录的引用；发现不同就报告相对路径，不自动替换。
- 不挂载磁盘、不修改文件、不写 EFI/账户/NVRAM、不重新启动。私有菜单工具、禁用项和图标不属于其完整性检查范围。

返回 `PASS` 只代表所列文件和脱敏后的配置与历史基线一致。仍需用匹配 OpenCore 构建的 `ocvalidate` 检查，并进行可回退的原机启动；它不检查 macOS 卷内的 NVIDIA 驱动或整个 APFS 系统。计划改用其他组件版本时，差异是预期结果，不能为让检查通过而盲目覆盖新配置。

## 5 最终组合中不要漏掉的内容

1. **CPU**：`ProvideCurrentCpuInfo=True`；CpuTopologyRebuild 2.0.2、CpuTscSync 1.1.2 按 Darwin 25 范围启用，Lilu 先加载。最终 force-HT 补丁禁用，没有 `cpus=` 限制。`-v` 与这一版拓扑插件存在作者已记录的随机启动失败问题，保留本机成功的无 `-v` 组合。
2. **显卡**：NVIDIA 系统扩展最终为 2.6.2，安装在 macOS 卷内；只复制 EFI 无法替代它们和 AuxKC。保留当前显卡参数、IONDRVSupport Exclude、GPU BAR 设置，不添加 `-nvoff`。本机独显模式及内屏线路是前提，不能把 Intel 核显研究当成可用替代驱动。
3. **输入**：VoodooI2C 整树及其 VoodooI2CServices、VoodooGPIO、VoodooInput 插件一起保留；目录名必须和配置一致，不能是拷贝后产生的短文件名。
4. **无线**：Sequoia 与 Tahoe 的 AirportItlwm 使用不同 Darwin 范围；不能同时随意加载。Wi-Fi 联网不等于 AirDrop 可用。
5. **ACPI**：保留本机目标明确的 GPIO 修正、EC RTCM overlay 与匹配的 SNTM→XNTM 定向重命名。源码和限定条件见 [补丁说明](../patches/README.md)。BIOS 改变后重新核对，不能全局替换方法名。
6. **Windows**：保留 Microsoft 引导、Windows 优先和 `RequestBootVarRouting=False`；从 F12（必要时 Fn+F12）进入自己的 OpenCore，再选 Macintosh HD。不要为复现增加新默认菜单或覆盖 Windows EFI。

完整参数以 Tahoe 示例为准，避免从不同阶段各抄一段拼成新配置。SIP、AMFI 等历史兼容设置也保留在示例中，它们不是苹果原生安全配置。

## 6 安装、升级和恢复的顺序

最初安装见 [Sequoia 安装参考](REINSTALL.zh-CN.md)。按实际安装阶段选择恢复环境、macOS Installer 或 Macintosh HD；不要每次重启都回最初恢复安装。需要账户替代流程时先读 [账户恢复说明](ACCOUNT-RECOVERY.zh-CN.md)，不得在已有正常账户的系统重跑创建步骤。

15→26 曾遇到升级脚本的整包 `codesign` 检查误判、已有安装应用仍触发初始空间要求、引导卷以只读方式挂载等问题。处理方式与实际证据见 [结项报告](PROJECT-CLOSEOUT.zh-CN.md)和 [Tahoe 记录](TAHOE26.zh-CN.md)。原脚本绑定本机当次安装包、卷身份和文件清单，没有作为通用升级工具发布；下次应重新取得 Apple 安装资源并验证，不能跳过签名/内容检查强行运行。

如果现在只剩空盘，仓库本身无法补回已删除的安装包和系统镜像。若保留原来的已装系统而仅 EFI 失败，应先排查 EFI，避免为了恢复引导而重装或改分区。

## 7 原机验收和保存

先确认正常登录、Windows 默认启动、CPU 活动线程数、驱动实际加载和可用空间，再分别验收网络、图形、输入、声音、AirDrop、睡眠及外接设备。CPU 可只读查看：

```text
sysctl hw.activecpu hw.logicalcpu hw.logicalcpu_max hw.physicalcpu hw.physicalcpu_max
```

本机历史原机记录为 20 活动逻辑处理器；拓扑重建会影响物理核心数的呈现，所以单看一个“6 核”显示不能直接判为只有 6 个线程。短时记录也不等于长期稳定或与 Windows 相同的性能。

新一轮真正可用后保存自己的完整 EFI、版本/哈希、关键修复和独立个人数据备份。公共仓库继续只存脱敏技术资料。**2026-11-04 已按机主明确选择删除 40 个备份/测试镜像和旧包，约 156.77GiB；这些原系统、应用和设置无法从 GitHub 重新下载。**

本次 2026-11-26 整理重新只读验证了本地私人 EFI 的 171 个文件，未发现哈希不一致；没有重新测试系统启动或麦克风、AirDrop 等功能，状态仍以 [功能表](STATUS.zh-CN.md)为准。
