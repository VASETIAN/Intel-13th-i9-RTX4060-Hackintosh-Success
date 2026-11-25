# 项目结项：安装、扩容、全核心与 Tahoe 启动恢复

归档日期：2026-11-26。本文汇总既有文件、检查回执及机主反馈，不把文档发布当作今天重新通过实机测试。下次操作从 [复用指南](REUSE.zh-CN.md)开始。

## 1 最终取得的结果

本机为 ThinkBook 16p G4 IRH / 21J8、BIOS LRCN52WW、Intel i9-13900H（6P+8E，14 核20线程）、RTX 4060 Laptop 8GB、16GB RAM、约1TB NVMe、AX203。通过 OpenCore 与 ACPI/kext 适配保留 Windows 11 双系统，最初安装 Sequoia 15.7.9，之后扩至100GiB，并原位升级至 Tahoe 26.7.1 / 25G241。

最终记录是：2026-11-01 机主确认恢复正常开机，Windows 默认启动也确认修复。2026-10-30 原机记录观察到图形会话、20活动逻辑处理器及四个 NVIDIA 2.6.2 扩展加载。最终配置不含 `cpus=1`、`-v` 或 `-nvoff`。

这不是全外设成功报告。麦克风无声音、AirDrop 不可用、Apple ID 状态不一致等历史问题没有最终通过证据；休眠、全部USB、触控手势、外接屏、功耗与长期性能也没有完整验收。详见 [功能状态](STATUS.zh-CN.md)。

## 2 按阶段看实际过程

| 阶段 | 发生了什么 | 实际处理与结果 |
|---|---|---|
| 硬件与边界 | 无可用U盘，需要保留Windows与D数据 | 先查硬件、磁盘、加密和EFI；在授权范围准备独立约2GiB引导区与macOS目标区，保留微软引导和默认Windows |
| 最初菜单 | OpenCore仅显示Windows，超时后回Windows | 检查恢复镜像、chunklist和扫描配置；安装阶段显示辅助项并等待选择，出现macOS恢复入口 |
| 早期内核启动 | panic、ACPI枚举附近停顿，多CPU对照无法稳定推进 | 按日志区分阶段，保留能进入安装器的 `cpus=1` 兼容基线；不是永久完成全核心 |
| ACPI范围 | GPIO重命名影响非目标表；维护模式SNTM反复报SystemCMOS/RTCM/AE_NOT_EXIST | 收窄GPIO补丁至目标DSDT一次匹配；定向改SNTM定义并加Darwin返回的EC RTCM overlay，保留其他系统原方法 |
| 安装器进度 | “不到一分钟”长时间停留，日志曾到解包39% | 读取真实安装日志、空间和当前阶段；后续有100%与SUCCESS。两CPU对照未成功，不把时间显示当唯一判据 |
| 选择启动项 | 多次重启、安装入口和已装系统混淆 | 有有效macOS Installer时继续该安装；收尾后转Macintosh HD。Windows默认启动导致重启回Windows不自动等于panic |
| 首次设置 | 地区页继续按钮变灰、持续转圈 | 取得线程快照；区域保存后等待服务回调。Wi-Fi等待与单核Swift调度是线索，没有证实唯一根因 |
| 本地账户替代 | 机主确认采用替代方案；标记检查和密码确认曾STOP | 修复启动参数空白比较，保留部分账户并续验；有效账户/密码/管理员/主目录/Token检查通过后才写完成标记，恢复普通EFI后机主登录成功 |
| Sequoia图形 | 基础显示缩放不协调、卡顿 | 经1401安装四个NVIDIA 2.5.4系统扩展，机主确认显卡可用；缩放按显示设置检查，不无依据改SMBIOS |
| 容量 | 原macOS约45GiB，D压缩空间位于其前方 | 不能直接扩大起点；先做完整备份与副本验证，再用原系统内容原生APFS扩容，最终写入并完整回读100GiB |
| 扩容试验入口 | 自定义100G TEST报LoadImage Not Found | 核实重启后GPT序号/设备路径变化，最终撤掉旧容量路径，使用当前自动扫描；ASR候选未作为最终系统 |
| 扩容完成 | 需要保留账户、应用、显卡设置 | 卷身份与选定文件一致，100GiB回读哈希一致，Windows保护检查通过；2026-10-27机主确认与扩容前基本一样 |
| 全核心研究 | 20虚拟CPU测试可以启动，实体机仍需验证 | VM用于隔离配置/拓扑测试，未冒充原机成功；后续转向Tahoe原位升级与原机验证 |
| 升级准备 | InstallAssistant安装成功，但resource envelope检查失败 | 旧脚本将安装应用的自定义资源规则误判；保留Apple包签名和固定哈希，用包内文件/链接对照验证既有应用后复用 |
| 升级续跑 | 只读OC卷、已有应用仍触发35GiB门槛 | 脚本先转到系统内运行，再核实卷实际可写；已有应用校验通过后跳过重复部署的空间门槛。Apple安装器准备到100%并进入升级 |
| Tahoe时钟panic | 出现unsynchronized TSC、Non-monotonic time | 增加CpuTscSync 1.1.2并限定Darwin25，保留CpuTopologyRebuild 2.0.2与ProvideCurrentCpuInfo；最终有原机20活动CPU记录 |
| 首次桌面排查 | 安全模式和无线隔离未取得桌面通过 | 临时 `-x` 后撤回；无线隔离用于定位，不写成AirDrop或地区页的修复。最终按可用原件恢复无线组合 |
| 后续驱动回归 | macOS内添加音频/AirDrop相关组件后启动失败 | 全量核对启用驱动；修正VoodooI2CServices短目录名，再回退输入、无线和AppleALC组合，撤出SimpleHDA/CirrusAudioFixup |
| 最后启动修正 | 回退后仍保留 `-v`，存在随机失败 | 复核作者说明与成功基线，仅删除开头 `-v ` 三字节，读回与ocvalidate通过；11月1日机主确认开机成功 |
| Windows默认项 | 曾出现默认进OpenCore及Boot变量读取混淆 | 核实原生Boot命名空间，保留微软加载器并恢复Windows优先，RequestBootVarRouting=False；机主确认 |
| 保存与清理 | 镜像占用大，机主决定不再保留完整系统回退点 | 保存小型私人EFI与技术资料；11月4日按40文件精确清单删除156.77GiB旧镜像/包，不动实盘双系统 |

## 3 关键修复的复用方式和限制

### 3.1 ACPI与安装入口

RTCM刷屏来自本机EC的SNTM访问SystemCMOS区域；处理是目标限定的SNTM→XNTM方法定义重命名，配合 [SSDT-EC-RTCM.dsl](../patches/SSDT-EC-RTCM.dsl)。Darwin下不执行原时间同步，其他系统保留原调用。完整匹配长度、OEM条件与GPIO补丁区别见 [补丁文档](../patches/README.md)。不得只加载overlay而遗漏rename，也不得将补丁扩展到所有同名方法。

OpenCore菜单、安装阶段与UEFI错误分别检查：LoadImage Not Found是选定加载路径问题，不能直接推断APFS损坏；进入内核或用户空间后停顿也不再是同一菜单问题。OpenCore日志不等于完整macOS内核/用户空间日志，增加OpenCore文件日志不能保证留下卡死点之后的内核记录。

### 3.2 设置助手与本地账户

国家地区页的原始根因未闭环。不能把论坛建议中的Swift环境变量、`.skipbuddy` 或 pycreateuserpkg 写为本机采用的修复，因为没有这样实施。结束Setup Assistant反而触发临时设置会话退出；因此不再用killall反复重试。

最终采用授权后的本地账户替代流程。一次STOP出现在启动参数空白差异，修正为规范空白后的有序严格匹配；另一次密码认证失败后保留了部分账户，后续只续验已有账户，没有删除重建或重置密码。详情见 [账户恢复说明](ACCOUNT-RECOVERY.zh-CN.md)。旧脚本绑定具体安装状态，不作为通用工具发布。

### 3.3 扩容不是直接向前合并

D释放的空间在旧macOS前方，而APFS容器不能靠Windows压缩D就自动向前扩展。最终用原系统完整备份作为源，在副本的同版本恢复环境原生扩容，经APFS检查后部署100GiB并全部回读，未采用试验的ASR候选。

当时回读哈希、卷身份、账户/驱动/用户偏好文件与Windows保护检查支持迁移结果；之后机主实机确认。现在完整镜像已按要求删除，**上述迁移脚本的输入条件已不再存在**，不能在今天直接重跑。未来再改布局需要新的备份、当前分区检查和独立授权；本仓库没有自动分区/搬移工具。

### 3.4 升级脚本的签名与空间处理

`InstallAssistant`成功仅证明安装应用部署完毕，不等于Tahoe已安装。最初的 `codesign --verify --deep --strict` 对Apple安装应用报 `resource envelope is obsolete (custom omit rules)`；这里不能等同于包损坏，也不能据此关闭全部校验。Apple对不同签名结构的说明见 [TN2206](https://developer.apple.com/library/archive/technotes/tn2206/)。

实际修复保留原始包SHA256及Apple签名验证，再对已装应用核对696个普通文件、26个链接，共18,435,551,555字节；内容符合才复用。该版本SharedSupport来自完整原始包，不能用一个同名内部成员擅自替换。已存在应用不再重复套部署前35GiB门槛，续跑仍检查基础余量并由Apple安装器判定精确需求。

OC引导卷曾只读挂载；修正版先把脚本及校验材料转入系统内执行，避免占用该卷，再检查卸载/读写挂载与实际写入能力。没有强制卸载、格式化、重签Apple应用或关掉Gatekeeper来掩盖失败。安装准备100%之后继续同一OpenCore的安装入口，最终系统版本与启动结果另行核实。

### 3.5 全核心、TSC与随机启动

最终组合不是只删除 `cpus=1`。它包括当前CPUID兼容值、ProvideCurrentCpuInfo、Lilu、CpuTopologyRebuild 2.0.2、CpuTscSync 1.1.2及其Darwin25范围；最终force-HT补丁保持禁用。遇到明确TSC/Non-monotonic panic时处理时钟同步，不能仅凭ACPI最后一行叠加未知APIC补丁。

[CpuTopologyRebuild固定版本说明](https://github.com/b00t0x/CpuTopologyRebuild/blob/2.0.2/README.md)要求Alder/Raptor Lake配合ProvideCurrentCpuInfo，并记录 `-v` 可能造成随机启动失败。[CpuTscSync固定版本说明](https://github.com/acidanthera/CpuTscSync/blob/1.1.2/README.md)说明其TSC同步用途和适用限制。公开说明提供依据，本机结果仍来自记录与实测，不能承诺同型号以外必然成功。

历史的虚拟机20CPU成功、静态ocvalidate通过、原机20活动CPU、机主最终启动确认属于不同层次。最终保留无CPU数量限制和无 `-v` 的组合，不把其中某一项宣布为所有故障的唯一根因。

### 3.6 NVIDIA与后期驱动回退

Sequoia使用NVIDIA 2.5.4；Tahoe最终记录为2.6.2的NVRM/NVRMFB/NVRMAGDC/NVAccel。它们属于macOS卷内系统扩展，不在EFI。更新后的AuxKC与扩展版本/UUID一起检查，不能仅凭复制成功判定加速成功。原机日志有加载记录，机主历史上确认显卡可用，但本次结项没有新增Metal/视频/功耗基准。

后期一次OpenCore关键停止明确对应VoodooI2CServices路径：文件存在于短目录名中，修复正确名称并核对整树。随后完整回退安装音频前的输入、无线、AppleALC组合，撤回SimpleHDA/CirrusAudioFixup，避免只修一项后漏掉其他启用文件。最终移除冲突 `-v` 后机主确认开机。

音频驱动撤回意味着恢复可启动组合，**不意味着麦克风已修好**。AirDrop和Apple ID也没有新增通过证据，不提供“装上Wi-Fi就一定修好”的结论。

## 4 归档和备份的真实范围

公开：完整过程说明、两阶段脱敏配置、EC补丁源码、组件版本/路径/哈希、只读检查代码、验证边界和未解决项。

私人本地保留：当次确认的完整EFI/OC和EFI/BOOT，共171文件、72,789,956字节，及驱动参考/证据。2026-11-26只读重新核对这171个文件，哈希均匹配；不代表重新测试了原机。该包含身份和第三方二进制，不放公共仓库。

已删除：2026-11-04授权清单B01–B04的40个完整备份、VM/扩容测试盘与旧安装包，实际占用168,330,342,400字节（156.77GiB）。删除回执显示40个均完成、293个受保护文件未改变、没有写实盘系统或EFI。公开GitHub从未包含这些完整系统镜像。历史报告写“备份仍保留”只说明当时，已被后续删除记录取代。

## 5 阅读索引

- [下次使用指南](REUSE.zh-CN.md)：如何取得材料、选版本、检查EFI与安排验收。
- [Sequoia原始报告](REPORT.zh-CN.md)与[安装参考](REINSTALL.zh-CN.md)：早期单核安装阶段。
- [账户替代流程](ACCOUNT-RECOVERY.zh-CN.md)：地区页工作绕过及其限制。
- [Tahoe启动恢复](TAHOE26.zh-CN.md)：最终配置、原机证据、驱动回退与Windows修复。
- [依赖来源](DEPENDENCIES.zh-CN.md)、[配置区别](../config/README.md)、[固件补丁](../patches/README.md)。
- [功能状态](STATUS.zh-CN.md)：继续保留未验收项，不把进入桌面等同于全设备成功。

本次结项不写实盘EFI、macOS、Windows、分区表或固件，不自动重启，也不执行新的系统清理。
