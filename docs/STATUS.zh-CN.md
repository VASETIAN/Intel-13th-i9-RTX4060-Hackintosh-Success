# 当前功能状态与已知限制

更新日期：2026-11-01。本表对应 **macOS Tahoe 26.7.1 / 25G241**，不再使用 Sequoia 阶段的单核限制表示当前状态。旧状态保留于 [Sequoia 证据摘要](../evidence/sequoia15.pre-expansion.json)及[原始安装报告](REPORT.zh-CN.md)。

| 项目 | 当前结果 | 证据与边界 |
|---|---|---|
| 系统版本 | 26.7.1 / 25G241 | 系统版本文件、本次只读检查和 10 月 30 日原机记录一致 |
| 原机启动 | **机主 11 月 1 日确认正常开机** | 最后移除 -v 后的直接反馈；不是用 ocvalidate 或 VM 代替验收 |
| 图形桌面 | 10 月 30 日原机有 WindowServer、Finder、Dock；本次反馈开机恢复 | 本次没有重新采集完整成功会话遥测或性能数据 |
| CPU | 当前无 cpus=1；10 月 30 日有 **20 活动逻辑 CPU** | 原机记录 activecpu/logicalcpu=20 及短时 20 worker；无完整性能/长期负载认证 |
| CPU 拓扑和同步 | CpuTopologyRebuild 2.0.2、CpuTscSync 1.1.2，Darwin 25 范围启用 | ProvideCurrentCpuInfo=True；当前 force-HT 补丁禁用；不重新加入 -v |
| NVIDIA | NVRM、NVAccel、NVRMFB、NVRMAGDC 均 **2.6.2** | 安装/缓存元数据与原机加载 UUID 对照；无本轮 Metal/编解码基准 |
| Intel 核显 | 未验证 macOS 加速 | 当前 BIOS 独显模式；核显原型研究不属于本仓库可用驱动结果 |
| Windows 默认启动 | **机主确认修复** | 保留微软引导和原生 Windows 优先；RequestBootVarRouting=false |
| Wi-Fi | 恢复 Tahoe 2.4.0 驱动，有原机加载记录 | 历史曾确认联网；本轮没有重新做完整联网测试，不能代替 AirDrop 验收 |
| 蓝牙 | BlueToolFixup、IntelBTPatcher、IntelBluetoothFirmware 已配置 | 无本轮扫描、配对、音频、连续互通的逐项通过记录 |
| 扬声器、功放、麦克风 | **未完整验收**；恢复 AppleALC 1.9.9 | SimpleHDA、CirrusAudioFixup 撤回；开机恢复不等于音频恢复 |
| AirDrop | **仍未确认修复** | 历史机主反馈不可用，本次没有成功收发证据 |
| Apple ID | **仍未闭环** | 历史界面与登录记录不一致，本次没有新增最终通过反馈 |
| 键盘/鼠标 | 历史可操作安装、维护和桌面 | 输入依赖完整回退；不代表所有快捷键或触控手势正常 |
| 触摸板手势 | 待验证 | VoodooI2C 插件与 VoodooI2CHID 已恢复，不等于全部功能通过 |
| USB 全端口 | 待逐端口验收 | USBToolBox/UTBDefault 仍为当前组合，不表示定制映射完成 |
| 睡眠、唤醒、摄像头、外接屏 | 待验证 | 没有本轮完整测试记录 |
| 原始地区页卡死 | 根因未证实修复 | 15 阶段以本地账户替代流程进入桌面，升级不自动证明设置助手已修好 |
| APFS | 诊断副本原生只验证通过，exit 0 | 原盘后端只读，写入仅在 COW 层；未执行原卷修复或制作新全盘镜像 |

## 本轮已处理的启动故障

1. VoodooI2CServices Info.plist 缺失的 critical halt：恢复正确目录和文件，越过该阶段。
2. 安装新驱动后的启动回归：恢复安装前 EFI 组合，将新增音频 kext 撤出活动目录。
3. 回退时保留 -v 的遗漏：移除 CpuTopologyRebuild 作者指出可能随机失败的详细启动参数，随后收到机主成功反馈。
4. 默认进入 OpenCore：纠正 Boot* 变量路由造成的读取混淆，恢复原生 Windows 优先，机主已确认。

详细经过和未证实解释见 [Tahoe 故障记录](TAHOE26.zh-CN.md)。

## 后续验证

先保留当前可开机基线，再分别测试扬声器、麦克风、Wi-Fi/蓝牙、AirDrop、睡眠唤醒、USB 和外接屏。取得实际结果后更新本表，不为一次外设尝试同时替换 CPU、输入、音频和无线多组组件。

20 活动 CPU 不等于原生 Windows 等效性能；驱动加载、Wi-Fi 可用、文件系统只验证和配置静态校验也不等于其他功能通过。
