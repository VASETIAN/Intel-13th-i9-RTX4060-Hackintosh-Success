# Intel 13代 i9 + RTX 4060 黑苹果：macOS 15 → 26

本项目记录一台 **Lenovo ThinkBook 16p G4 IRH（21J8），i9-13900H + RTX 4060 Laptop** 的原机双系统安装和适配过程，从 macOS Sequoia 15.7.9 到目前的 **macOS Tahoe 26.7.1，build 25G241**。

**2026-11-01 更新：机主已确认 macOS 26 恢复正常开机。** 当前配置不含 `cpus=1` 和 `-v`；2026-10-30 的原机记录已观察到 WindowServer、Finder、Dock、20 个活动逻辑处理器，以及四个 NVIDIA 2.6.2 扩展加载。11 月 1 日反馈确认的是启动恢复，没有重新逐项完成全部硬件和性能验收。

Windows 默认启动也已修复并由机主确认；进入 macOS 时使用 F12 → OpenCore → Macintosh HD。这是单机实践记录，不是对所有 13 代 i9、RTX 4060 或其他 BIOS 的兼容承诺，也不是苹果或 NVIDIA 官方支持声明。

## 从哪里开始

- [macOS 26 升级后状态、故障与修复记录](docs/TAHOE26.zh-CN.md)：本次更新的主要内容。
- [当前功能状态和未解决问题](docs/STATUS.zh-CN.md)：区分已确认、历史证据和待验证项。
- [macOS 15 原始安装与故障报告](docs/REPORT.zh-CN.md)：保留当时单核、NVIDIA 2.5.4 的历史，不作为当前配置。
- [安装与重装参考](docs/REINSTALL.zh-CN.md)及[首次设置与账户恢复说明](docs/ACCOUNT-RECOVERY.zh-CN.md)。
- [当前与历史依赖版本](docs/DEPENDENCIES.zh-CN.md)。
- [两套脱敏配置示例](config/README.md)和 [EC RTCM 修补源码](patches/README.md)。
- [当前脱敏证据摘要](evidence/summary.json)、[EFI 驱动清单](evidence/tahoe26-drivers.json)及[证据说明](evidence/README.md)。

## 实际硬件

| 项目 | 本机配置 |
|---|---|
| CPU | Intel Core i9-13900H，6P + 8E，14 核 20 线程 |
| 独显 | NVIDIA GeForce RTX 4060 Laptop GPU，PCI `10DE:28E0` |
| 核显 | Intel Iris Xe，历史硬件标识 `8086:A7A0`；未取得 macOS 加速验证 |
| 整机与主板 | Lenovo ThinkBook 16p G4 IRH，21J8；LNVNB161216 |
| BIOS | LRCN52WW；本次读取为 Discrete Graphics；未刷写 BIOS |
| 内存 | 16 GB |
| SSD | Samsung MZVL21T0HCLR-00BL2，约 1 TB，NVMe，GPT |
| Wi-Fi | Intel AX203，PCI `8086:51F1` |
| 内屏 | 3200 × 2000；Windows 历史实测活动 eDP 路由由 NVIDIA 输出，约 165 Hz |
| 原有系统 | Windows 11，UEFI，保留为默认启动系统 |

机型、固件和显卡输出线路影响 ACPI、显示和输入适配，仅 CPU 或显卡相同不足以直接复用配置。

## 当前与历史基线

| 项目 | Sequoia 历史阶段 | Tahoe 当前记录（2026-11-01） |
|---|---|---|
| 系统 | 15.7.9 / 24G830 | **26.7.1 / 25G241** |
| 启动与桌面 | 已完成安装，可登录使用 | **机主确认恢复正常开机**；10 月 30 日有原机图形会话记录 |
| CPU | 保留 cpus=1 | 无该限制；10 月 30 日原机观察到 **20 活动逻辑 CPU**；无完整性能认证 |
| CPU 扩展 | CpuTopologyRebuild 未启用 | CpuTopologyRebuild 2.0.2、CpuTscSync 1.1.2，按 Darwin 25 范围启用 |
| NVIDIA | 四个系统扩展 2.5.4 | 四个系统扩展 **2.6.2**，原机记录观察到加载 |
| Wi-Fi | 机主确认正常 | Tahoe 用 AirportItlwmTahoe 2.4.0；有加载记录，11 月 1 日未重新做联网全项验收 |
| Windows 默认引导 | 当时正常 | 再次修复后机主确认正常，保留 RequestBootVarRouting=false |
| 音频 | 未完整验收 | 已回退新增音频驱动，恢复 AppleALC；麦克风/扬声器仍待测试 |
| Apple ID / AirDrop | 登录状态未闭环 / AirDrop 不可用 | **没有新增修复通过证据，保留问题记录** |
| 睡眠、USB、蓝牙、触摸板、外接屏 | 未完整验收 | 不因升级或开机成功自动变为通过 |

## 本次恢复启动的关键

机主反馈故障发生在 macOS 内安装麦克风、扬声器和 AirDrop 相关驱动之后。排查先恢复缺失/目录名错误的 VoodooI2C 插件，再回退到安装前保存的驱动组合；SimpleHDA、CirrusAudioFixup 撤出活动 EFI，AppleALC 和输入、无线驱动恢复原版。

驱动回退后曾保留 `-v` 观察错误，但 [CpuTopologyRebuild 2.0.2 作者已记录详细启动可能随机失败](https://github.com/b00t0x/CpuTopologyRebuild/blob/2.0.2/README.md#current-problems)。安装前配置和 10 月 30 日成功记录都没有它。最终移除开头 `-v ` 三字节后，机主确认正常启动。该先后关系支持保留当前组合，不能证明此前每条错误都由同一个原因造成。

原生 fsck_apfs 在只读原盘后端加写时复制层的诊断副本上只验证通过（exit 0）；未对原 APFS 执行修复。没有根据 APFS trim 或日志末行直接格式化、重装系统。详细经过见 [macOS 26 记录](docs/TAHOE26.zh-CN.md)。

## 仓库范围

包含文档、脱敏配置、驱动版本和哈希摘要、原创补丁与只读检查代码。私人完整 EFI 已另行备份并逐文件核验，共 171 个文件、72,789,956 字节；**公开仓库不包含完整 EFI、系统镜像、驱动二进制、密码、账户数据库、实际 SMBIOS 身份、个人分区 UUID、原始 NVRAM 或原始日志。**

两套配置示例都不能直接启动：需自行取得匹配组件、建立自己的身份、核对固件与设备路径。当前本地 OpenCore 标识为 DBG109 / 1.0.9；旧记录未建立可确认的同版本官方 release 下载来源，仓库继续不分发该构建或编造下载地址。

第三方软件保持各自许可证。原创文档、独立示例和定制补丁采用 [MIT License](LICENSE)。

## English summary

This repository records one bare-metal ThinkBook 16p G4 IRH / 21J8 with an i9-13900H and RTX 4060 Laptop, from Sequoia 15.7.9 to **Tahoe 26.7.1 / 25G241**. The owner confirmed normal boot on November 1, 2026 after driver rollback and removal of verbose -v from the CpuTopologyRebuild 2.0.2 profile. An October 30 native record observed GUI processes, 20 active logical CPUs and four NVIDIA 2.6.2 kexts. The current profile has no cpus=1; this is not a full performance or peripheral certification. Apple ID, AirDrop, audio, sleep and other unverified functions remain explicitly tracked.

Run the repository-only checks with Python 3:

```text
python tools/validate_publication.py --self-test
python tools/validate_publication.py
```

These checks read repository files only. They do not mount disks, write EFI, modify firmware, create accounts, or prove a physical boot.
