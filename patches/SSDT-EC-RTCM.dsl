DefinitionBlock ("", "SSDT", 2, "CODEX", "ECRTCM", 1)
{
    External (\_SB.PC00.LPCB.EC0, DeviceObj)
    External (\_SB.PC00.LPCB.EC0.XNTM, MethodObj)
    Scope (\_SB.PC00.LPCB.EC0)
    {
        Method (SNTM, 0, NotSerialized)
        {
            // macOS cannot service AWAC's SystemCMOS field reads from this EC query.
            If (_OSI ("Darwin")) { Return (Zero) }
            XNTM ()
        }
    }
}
