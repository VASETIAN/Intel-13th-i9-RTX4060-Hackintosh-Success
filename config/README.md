# 脱敏配置示例

`config.pre-expansion.sample.plist` 从本项目扩容前已安装 NVIDIA 驱动的可用配置生成，只做发布所需的脱敏与删除本机专用工具入口。不是当前正在运行的 EFI，也不会被检查脚本部署到系统。

## 已去除的内容

- SMBIOS 序列号、MLB、ROM、系统 UUID 和同类身份字段置空。
- 本机专用的 Misc 自定义启动和工具入口移除。
- 不附账户数据、NVRAM dump、原始固件表、完整 EFI 或任何第三方二进制。

**文件不能直接当成完整安装包使用。** 它引用的 SSDT、kext 和 UEFI 驱动需要自行按版本取得；SMBIOS 身份必须属于自己的配置，不能使用他人的标识。独立资料中的只读 NVRAM vendor GUID 是公开变量命名空间，不是本机账户或分区 UUID。

## 保留的技术记录

- SMBIOS 型号 MacBookPro16,1；不表示实际苹果机器或硬件兼容认证。
- `cpus=1`、CPU 兼容数据和基础 quirk；CpuTopologyRebuild 未启用。
- `DevirtualiseMmio=False` 等本机 Booter 设置。
- 本机使用的 SSDT、GPIO 与 EC RTCM 定向重命名。
- AirportItlwm Sequoia 范围，及实际 Kernel/Add 启用状态。
- 安装 NVIDIA 后的 `IONDRVSupport` Exclude 与图形启动参数。
- 安装诊断菜单 `HideAuxiliary=False`、`Timeout=0`；没有在公开整理中改成新的双系统菜单方案。

示例也保留第三方驱动使用时的安全兼容设置，包括 Disabled 的 Apple SecureBootModel、SIP/AMFI 相关配置。它们会改变 macOS 的部分安全保护，不能当作原生苹果安全配置或对其他机器的默认建议。

最终 `Kernel/Block` 没有启用 AppleHDA 的临时阻断。不要依据文件夹里可能有某个 kext 就认定它已启用；以 Add 列表和实际启动日志为准。

## 使用前的检查

先读 [安装参考](../docs/REINSTALL.zh-CN.md) 和 [功能限制](../docs/STATUS.zh-CN.md)，根据自己的硬件、BIOS 和系统版本逐项比较。用匹配构建的 `ocvalidate` 和文件路径检查确认结构，再进行可回退的实机测试。仓库的只读验证只检查公开文件和脱敏条件，不能证明这份示例在另一台机器上可启动。
