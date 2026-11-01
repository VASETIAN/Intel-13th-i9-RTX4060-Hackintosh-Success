# macOS 26 升级后状态与启动恢复记录

记录终点：2026-11-01，机主明确反馈“好了，现在能正常开机了。”系统为 macOS Tahoe 26.7.1 / 25G241，OpenCore 本地构建 1.0.9 DEBUG，SMBIOS 型号 MacBookPro16,1。

本文是 [Sequoia 15 安装报告](REPORT.zh-CN.md)的后续，不把旧阶段的单核限制或 NVIDIA 2.5.4 当成当前状态，也不声称已经整理出完整可复现的 15 → 26 自动升级脚本。

## 1 主要变化

| 项目 | 15 阶段 | 26 当前组合 |
|---|---|---|
| 系统 | 15.7.9 / 24G830 | 26.7.1 / 25G241 |
| CPU 限制 | cpus=1 | 无 cpus=1，原机记录有 20 活动逻辑 CPU |
| CPU 插件 | CpuTopologyRebuild 未启用 | CpuTopologyRebuild 2.0.2 + CpuTscSync 1.1.2，仅 Darwin 25 |
| 详细启动 | 历史诊断使用 | 当前无 -v |
| NVIDIA | 四个 2.5.4 扩展 | 四个 2.6.2 扩展，有原机加载记录 |
| Wi-Fi | Sequoia AirportItlwm 2.4.0 | AirportItlwmTahoe 2.4.0，按 Darwin 范围选择 |
| 音频 | AppleALC，功能未完整验收 | 回退至原 AppleALC，新增音频 kext 不在活动 EFI |
| Windows | 默认 Windows | 已再次修复并确认，RequestBootVarRouting=false |

## 2 原机成功启动的证据

2026-10-30 14:00 左右原机采集记录显示：

```text
ProductVersion: 26.7.1
BuildVersion: 25G241
hw.model: MacBookPro16,1
hw.activecpu: 20
hw.logicalcpu: 20
hw.logicalcpu_max: 20
hw.physicalcpu: 6
hw.physicalcpu_max: 14
hw.memsize: 17179869184
```

该记录有 WindowServer、Finder、Dock，以及 Lilu 1.7.3、CpuTopologyRebuild 2.0.2、AirportItlwm 2.4.0 和四个 NVIDIA 2.6.2 实际加载信息，并完成有界的 20 worker 短时计算采集。后续原机 WindowServer CPU resource 诊断也与此一致。

hw.physicalcpu 的 6 与物理硬件的 14 核要结合拓扑重建后的呈现理解；确认 20 活动逻辑处理器不等于完整性能认证。此处来自原机，隔离 VM 结果分开处理。

11 月 1 日又收到开机恢复反馈，但没有重新取得完整成功会话遥测，不能把 10 月 30 日测量标记为本次新测试。

## 3 故障与驱动回退

### 3.1 背景和日志边界

机主回忆在 macOS 中安装麦克风、扬声器、AirDrop 相关驱动后开始不能正常进入桌面。没有完整安装事务记录来证明恰好只改了三个文件，或哪个系统卷改动是唯一根因。

不同照片先后出现 OpenCore critical halt、内核/launchd 日志、APFS trim、AMFI non-fatal、IOVersatile 依赖和 DriverKit 信息。它们不是同一失败阶段，不能仅凭最后一行统一判断成文件系统或显卡故障。

### 3.2 VoodooI2C 插件

一次启动明确报告 VoodooI2CServices.kext 的 Contents/Info.plist 缺失并停止。文件实际位于错误的短目录名下，修正目录后越过 critical halt。之后将 VoodooI2C 整树恢复为安装前备份，VoodooGPIO、VoodooInput、VoodooI2CServices 一起验证，不只复制主 kext。

### 3.3 原驱动组合

从机主保存的安装音频前 EFI 提取原件：

- 恢复 VoodooI2C.kext、AirportItlwm.kext、AirportItlwmTahoe.kext。
- AppleALC.kext、VoodooI2CHID.kext 与原件一致，核对后保留。
- SimpleHDA.kext、CirrusAudioFixup.kext 撤出活动 EFI，保留旧副本供回溯。
- 33 个启用 Kernel/Add 项的 Info.plist 和可执行文件均与原基线相符。
- OpenCore.efi、BOOTx64.efi、现存 11 个 ACPI 文件及 3 个 UEFI 驱动文件也与原备份一致；实际启用项以配置为准。

当前配置内容恢复为安装前组合，额外保留 Windows 修复需要的 RequestBootVarRouting=false。没有从 Windows 对 macOS 系统卷批量删除或写回文件。

### 3.4 最后遗漏：-v

回退时曾为观察报错保留 -v。复核发现安装前配置和 10 月 30 日成功记录均无此参数；[CpuTopologyRebuild 2.0.2 作者说明](https://github.com/b00t0x/CpuTopologyRebuild/blob/2.0.2/README.md#current-problems)明确记录详细启动可能导致随机失败。

2026-11-01 15:49 仅从 boot-args 开头移除 `-v ` 三字节，其余配置不动，读回并通过匹配的 ocvalidate。随后机主手动启动并确认成功。

当前基线不重新加入 -v、cpus=1 或 -nvoff。这形成了恢复记录，但不能说明全部此前日志都出自单一原因，也没有反复开关对照来量化随机失败概率。

## 4 当前配置要点

完整脱敏示例见 [Tahoe 配置](../config/config.tahoe26.known-good.sample.plist)，版本、顺序和范围见 [驱动清单](../evidence/tahoe26-drivers.json)。以下是本机组合记录，不是通用建议。

```text
debug=0x108 keepsyms=1 -vi2c-force-polling nvfb=1 nvaccel=1 nvfbheads=4 -nvkmsnosmooth amfi_get_out_of_my_way=0x1 amfi=0x80 gfxrst=4 ipc_control_port_options=0 -dbgenhoff -topo mmio_uart=0 pcie_mmio_uart=0 -ibtcompatbeta
```

- ProvideCurrentCpuInfo=True，AppleXcpmCfgLock=True，DevirtualiseMmio=False。
- CpuTopologyRebuild 2.0.2、CpuTscSync 1.1.2 仅 Darwin 25；当前 force-HT Kernel/Patch 保持禁用，不套用其他候选的启用状态。
- IONDRVSupport 使用 Exclude；ResizeGpuBars=-1，ResizeAppleGpuBars=0，保留已观察到成功的组合。
- RequestBootVarRouting=False；NVRAM/Delete 包含 boot-args，使参数替换旧值。本轮最终修正没有执行整机 Reset NVRAM。
- 包含 Disabled 的 Apple SecureBootModel、SIP/AMFI 相关兼容调整，不能描述为原生苹果安全配置。

## 5 Windows 默认启动

机主曾反映 F12 中 OpenCore 排在 Windows 前，无操作也进 OpenCore。早期“读取到 Windows 优先但固件仍选 OpenCore”的结论混入了 OpenCore Boot* 路由命名空间，不能据此认定 BIOS 锁定。

修复保留微软加载器，读取并调整原生启动变量，使 Windows Boot Manager 优先、OpenCore 条目保留；配置保持 RequestBootVarRouting=false。机主已明确确认 Windows 解决。本次发布不再调整固件或启动顺序。

## 6 APFS 与未证实的解释

APFS trim、挂载/卸载、快照信息不足以确认事务回滚死循环，也不足以排除 CPU 或图形因素。原生 fsck_apfs 在只读原盘后端加独立 COW 层的诊断副本上只验证完成，容器和各卷通过，exit 0；没有修复原卷。

Windows 第三方 APFS 读取器曾返回不可靠的近期日志负载；原生读取确认部分 launchd.log、轮转文件和近期 Persist trace 实际为空。基于错误负载作出的进程推断不能继续沿用。

NVIDIA 保护计数当次为 0，未触发停用，因此没有清计数。Karabiner 的 crashed 0 time(s) 不是崩溃证据，没有据此删除它。IOVersatile、缺失的 ARM 专用服务、AMFI non-fatal 或 AGPMController 末行都没有单独被证明是阻塞原因。

## 7 基线与仍存在的问题

成功反馈后私人备份完整保存 EFI/OC、EFI/BOOT，共 171 个文件、72,789,956 字节，SHA256 逐项一致；另存 NVIDIA 系统驱动参考、配置、版本和硬件记录。身份、私人备份路径、分区 UUID、原始日志和二进制不随公开仓库上传。

公开示例清空身份并移除本机工具入口，哈希与私人原件不同，不能替代完整 EFI 或整个系统备份。

仍待处理/验证：扬声器、麦克风、AirDrop、Apple ID、蓝牙功能、触控板手势、USB 全端口、睡眠唤醒、摄像头、外接屏、完整图形接口/视频编解码和长期负载。见 [当前状态表](STATUS.zh-CN.md)。后续先保存可回退基线，再逐项变更，不为一个外设同时替换多组组件。
