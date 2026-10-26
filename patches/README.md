# EC RTCM 定向修补和 GPIO 范围修正

## EC RTCM overlay

`SSDT-EC-RTCM.dsl` 是本项目的独立小表源码。目标环境为 21J8、LRCN52WW 中的 `\_SB.PC00.LPCB.EC0`。它处理 EC 的 SNTM 方法访问 AWAC SystemCMOS 字段时出现缺少 handler 的错误，不是通用 AWAC/RTC 方案，也不是 Setup Assistant 地区页根因修复。

必须先确认目标方法的路径与内容一致，再在匹配的 DSDT 中把原 SNTM **定义**改名为 XNTM，最后加入这个 overlay。只有 overlay 而没有正确 rename，会因方法冲突或缺少 XNTM 而不成立。

| OpenCore ACPI/Patch 字段 | 本项目最终 EC RTCM 值 |
|---|---|
| TableSignature | Data `44534454`，即 DSDT |
| TableLength | `638783` |
| OemTableId | Data `43422D3031202020`，即 CB-01 后三个空格 |
| Find | Data `534E544D005B28` |
| Replace | Data `584E544D005B28` |
| Count | `1` |
| Base / BaseSkip / Skip / Limit | 空字符串 / 0 / 0 / 0 |
| Mask / ReplaceMask | 空 Data |

DSL 在 Darwin 下直接返回，其他系统调用原 XNTM。原厂方法仅复制时间字段这一判断来自本机表分析，不能对另一份固件直接假设。换 BIOS 后重新核对；无法唯一匹配就停止，不扩大成全局 SNTM 替换。

使用可信 ACPICA `iasl` 可编译该源码，生成的 AML 再按自己的配置加入 ACPI/Add。仓库不附完整 DSDT、OEM SSDT 或第三方编译器。源码编译与配置结构通过也不替代实机验证。

## GPIO rename 的准确记录

早期无表过滤的 GPIO `_STA` 重命名曾误匹配另两张 SSDT 的 TPM 和 NVIDIA 平台设备。最终配置收窄为 DSDT、一次匹配：

| 字段 | GPIO 最终值 |
|---|---|
| TableSignature | `44534454` |
| Find | `145F535441` |
| Replace | `1458535441` |
| Count | `1` |
| TableLength | `0` |
| OemTableId | 空 Data |

**不要将 EC RTCM 的 638783/CB-01 过滤条件误写为 GPIO 最终实际配置。** 两项的目的和最终字段不同。GPIO 范围修正避免了非目标表误匹配，没有独立证明它就是此前 ACPI 末端停顿的唯一原因。
