# 安装与重装参考

> 版本范围：下文保留 Sequoia 15.7.9 首次安装流程，不是已验收的 Tahoe 26 全新安装指南。当前 26.7.1 已能开机，无 cpus=1，NVIDIA 为 2.6.2；先读 [macOS 26 记录](TAHOE26.zh-CN.md)、[当前依赖](DEPENDENCIES.zh-CN.md)和[两套配置的区别](../config/README.md)。恢复现有 26 系统不要套用历史单核配置、降回 2.5.4 或重做已完成的账户流程。

本文描述本项目实际采用的路径和再次安装时需要重新确认的条件。适用记录为 i9-13900H、RTX 4060 Laptop、21J8/LRCN52WW、Sequoia 15.7.9。不要将这里的顺序理解为所有相近硬件都能直接启动。

## 1 保留恢复能力

先保留原 Windows 的 EFI、启动记录、分区清单、个人文件备份，以及自己已验证可用的私人 OpenCore EFI。私人 EFI 中的身份信息不应上传公共仓库。本仓库中的脱敏示例不能代替它。

如果将来重新安装，磁盘号、分区号、APFS UUID 和账户状态都可能变化。不能使用历史照片中的 `disk0s5`、扇区号或账户 UUID 当作新系统的定位信息。每次都按容量、文件系统、分区身份和实际内容确认目标；不抹除顶层物理 SSD、Windows EFI、C 盘或 D 盘已有数据。

修改 Secure Boot 等固件设置前，核对自己的加密状态与恢复资料。原项目的某次检查结果不代表将来重装时仍然相同。项目没有刷写 BIOS，也不建议为复现而随意刷固件。

## 2 准备匹配组件

参考[依赖表](DEPENDENCIES.zh-CN.md)，准备 OpenCore、配套 `ocvalidate`、HfsPlus/OpenRuntime、需要的 kext 和本机 ACPI。先核对来源、版本与 SHA256，再处理 EFI。

本项目实际使用本地 DBG109 构建。公开整理时没有可确认的官方 1.0.9 release 资产，因此原样重装应优先依赖自己保存的已验证 EFI。若改用其他可追溯版本，需要重新检查配置 schema、驱动兼容性和启动结果；不能只更换 OpenCore 文件后称为完全复现。

恢复环境从 Apple 来源取得。可参考 [Dortania Windows 安装介质准备](https://dortania.github.io/OpenCore-Install-Guide/installer-guide/windows-install.html)，使用 OpenCore 上游的 `macrecovery.py` 下载恢复资源。核对恢复镜像与 chunklist；仓库不重新分发 macOS 镜像。Apple 当时提供的安装目标可能变化，不能保证未来下载仍自动得到 15.7.9。

## 3 组织 EFI

示意结构如下；实际二进制、上游生成表及各驱动由自己的已验证 EFI 或可信上游取得：

```text
EFI/
├── BOOT/BOOTx64.efi
└── OC/
    ├── OpenCore.efi
    ├── config.plist
    ├── ACPI/
    ├── Drivers/HfsPlus.efi
    ├── Drivers/OpenRuntime.efi
    └── Kexts/
```

先阅读[配置示例说明](../config/README.md)。为自己的机器生成 SMBIOS 标识，不使用他人的序列号、MLB、ROM 或 UUID。将配置与匹配版本的 `ocvalidate` 检查，再核对 ACPI/Add、Kernel/Add、UEFI/Drivers 中每个启用路径确实存在。

本机可用基线保留 `cpus=1`、`DevirtualiseMmio=False`、`ProvideCurrentCpuInfo=True`，CpuTopologyRebuild 和配套优化不启用。不要同时叠加 TSC、CPU、存储、音频等多个未经验证的改动。BIOS 更新后应重新提取并检查 ACPI，尤其是 EC RTCM 的定向重命名条件。

## 4 无 U 盘路径

原项目没有可用 U 盘，所以在批准的空闲空间内准备独立约 2 GiB FAT32/EFI 引导区，并在同一 GPT SSD 上保留单独的 macOS 目标区。不要为了照搬历史布局重新调整已经正常工作的系统。

独立区保存 EFI，以及 `com.apple.recovery.boot` 内的 `BaseSystem.dmg` 和匹配 chunklist。空间需要同时考虑恢复资源、EFI 和后续暂存材料，不能只看 OpenCore 二进制大小。实际空闲不足时优先改用可用的外部安装介质，不能删除个人文件或挤占 Windows EFI 来凑空间。

新增的是独立 OpenCore 启动入口，Windows Boot Manager 保留默认优先级。进入安装时从固件启动菜单选择 OpenCore。本机使用 F12，必要时 Fn+F12；其他设备按自己的固件说明操作。F2 通常用于固件设置，二者不要混淆。

## 5 先确认恢复环境

若菜单只显示 Windows，先检查恢复资源和扫描设置。本项目为安装阶段将 `HideAuxiliary=False`、`Timeout=0`，恢复项直接显示并等待选择。

进入恢复界面后，先确认键盘鼠标、目标磁盘和网络，再开始安装。AX203 在本例使用 AirportItlwm Sequoia 分支；仅看到 en0 不等于已经联网。恢复安装需要下载资源时，应先确认实际连通。

磁盘工具只操作事先确认的 macOS 目标区域，并采用适合该目标的 APFS 布局。报告没有提供自动删除、格式化或重新分区脚本；对已有双系统的重装尤其应避免选择整块 SSD。

## 6 跟随安装阶段选择正确入口

安装过程中可能依次出现恢复环境、`macOS Installer`、安装更新环境和 `Macintosh HD`。应根据当前安装阶段和实际日志继续同一安装，不要每次重启都从最初 BaseSystem 重新开始。

“不到一分钟”长时间不变时，检查安装日志是否还增长、是否有空间或 I/O 错误。原项目曾停在解包子阶段 39%，后来日志明确到达 100% 和 SUCCESS；不能把旧日志最后一行当成永久失败原因。

Windows 默认优先时，安装阶段重启回到 Windows 不必然表示 panic。重新从 OpenCore 选择当前有效的安装或已安装系统项。出现明确 SUCCESS 并完成收尾后，选择 Macintosh HD。

## 7 完成首次设置和账户

优先使用正常 Setup Assistant。只有复现相同地区页卡死且已安装系统完好时，才考虑本项目的[账户替代流程说明](ACCOUNT-RECOVERY.zh-CN.md)。

不要直接结束 Setup Assistant 期待在原会话重开：本机这样做触发了 sessionlogoutd 关机。不要仅创建 `.AppleSetupDone` 标记而没有有效账户，也不要使用历史扇区读取命令。部分账户已经存在时，先检查和续验，而不是重复创建、删除或重置密码。

维护完成后确认普通 EFI 已恢复，不再含临时 `-s`、失败的内存探针或诊断项，然后再验证图形登录。原项目最终仍保留 `cpus=1`，不要把移除维护模式误解成应同时移除 CPU 限制。

## 8 在 macOS 中安装 NVIDIA 系统驱动

使用[固定版本的 1401 Mac 和 NVIDIA 2.5.4](DEPENDENCIES.zh-CN.md)，将材料放到可访问位置；需要管理员密码时由本人在原生提示中输入。

项目当时通过 1401 只选择 NVIDIA driver，先查看更改，再安装驱动并重启；选择当前实际使用的 OpenCore 分区，不选择 Windows EFI。不在这个步骤同时切换系统版本、执行其他硬件重映射或运行未验证的 GPU 分支。

驱动安装应在 macOS 原生执行，遵循该固定版本的缓存和配置处理流程。随后检查扩展版本、实际显示状态及 1401 的运行提示。原项目扩容前记录的四个扩展为 NVRM、NVAccel、NVRMFB、NVRMAGDC，均为 2.5.4；这不是完整 Metal 性能认证。

内屏 3200 × 2000 下文字很小时，在显示器设置检查缩放与较大文字选项，必要时检查合适的 HiDPI 模式。不要把显示缩放问题直接当成 SMBIOS 型号错误。

## 9 保存自己的新基线

确认桌面、联网、账户、显示和 Windows 启动后，保存这一轮有效 EFI、版本清单、重要补丁及回退资料。自己的身份配置和个人系统备份继续私人保管；公共 GitHub 文档不能恢复其中的个人文件。

保留[功能状态表](STATUS.zh-CN.md)中的未完成项。没有新增测试证据时，不将音频、睡眠、全部 USB、触摸板手势、Apple ID 或 AirDrop 自动改为成功。
