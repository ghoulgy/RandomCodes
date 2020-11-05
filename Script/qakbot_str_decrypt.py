import idc
import idautils

# Dropped loader from original
dec_routine = 0x40A317
enc_strings = 0x413B68
bytes_arr = 0x419130

# 2nd loader carved payload
# dec_routine = 0x40A3DA
# enc_strings = 0x413B68
# bytes_arr = 0x419130

# 3rd Final
# dec_routine = 0x411EFF
# enc_strings = 0x429A50
# bytes_arr = 0x430188

def decrypt_string(idx):
	if idx >= 0x373A:
		return
	res = ""
	while True:
		c = idc.get_wide_byte(enc_strings+idx) ^ idc.get_wide_byte(bytes_arr + (idx&0x3F))
		if c == 0: break
		res+=chr(c)
		idx += 1
	return res

xrefs = idautils.CodeRefsTo(dec_routine, 0)

for x in xrefs:
	ea = idc.prev_head(x)
	t = idc.get_operand_type(ea, 1)
	if t == idc.o_imm:
		idx = idc.get_operand_value(ea, 1)
		# print(idx)
		dec = decrypt_string(idx)
		# print(hex(x))
		print(dec)
		idc.set_cmt(ea, dec, 1)
	if idc.print_insn_mnem(ea) == 'push':
		if idc.get_operand_type(ea, 0) == idc.o_imm:
			reg_val = idc.get_operand_value(ea, 0)
			dec = decrypt_string(reg_val)
			print(dec)
			idc.set_cmt(ea, dec, 1)

# Loader1
# 307
# 308
# kernel32.dll
# error res='%s' err=%d len=%u
# Self test OK.
# Self test FAILED!!!
# %s %04x.%u %04x.%u res: %s seh_test: %u consts_test: %d vmdetected: %d createprocess: %d
# GenuineIntel
# Fiddler.exe;samp1e.exe;sample.exe;runsample.exe;lordpe.exe;regshot.exe;Autoruns.exe;dsniff.exe;VBoxTray.exe;HashMyFiles.exe;ProcessHacker.exe;Procmon.exe;Procmon64.exe;netmon.exe;vmtoolsd.exe;vm3dservice.exe;VGAuthService.exe;pr0c3xp.exe;ProcessHacker.exe;CFF Explorer.exe;dumpcap.exe;Wireshark.exe;idaq.exe;idaq64.exe;TPAutoConnect.exe;ResourceHacker.exe;vmacthlp.exe;OLLYDBG.EXE;windbg.exe;bds-vision-agent-nai.exe;bds-vision-apis.exe;bds-vision-agent-app.exe;MultiAnalysis_v1.0.294.exe;x32dbg.exe;VBoxTray.exe;VBoxService.exe;Tcpview.exe
# Fiddler.exe;samp1e.exe;sample.exe;runsample.exe;lordpe.exe;regshot.exe;Autoruns.exe;dsniff.exe;VBoxTray.exe;HashMyFiles.exe;ProcessHacker.exe;Procmon.exe;Procmon64.exe;netmon.exe;vmtoolsd.exe;vm3dservice.exe;VGAuthService.exe;pr0c3xp.exe;ProcessHacker.exe;CFF Explorer.exe;dumpcap.exe;Wireshark.exe;idaq.exe;idaq64.exe;TPAutoConnect.exe;ResourceHacker.exe;vmacthlp.exe;OLLYDBG.EXE;windbg.exe;bds-vision-agent-nai.exe;bds-vision-apis.exe;bds-vision-agent-app.exe;MultiAnalysis_v1.0.294.exe;x32dbg.exe;VBoxTray.exe;VBoxService.exe;Tcpview.exe
# NtUnmapViewOfSection
# NtCreateSection
# NtMapViewOfSection
# NtWriteVirtualMemory
# NtProtectVirtualMemory
# NtClose
# aabcdeefghiijklmnoopqrstuuvwxyyz
# aabcdeefghiijklmnoopqrstuuvwxyyz
# abcdefghijklmnopqrstuvwxyz
# 1234567890
# GetProcAddress
# kernel32.dll
# GetModuleHandleA
# aswhooka.dll
# aswhookx.dll
# snxhk_border_mywnd
# kernel32.dll
# %02u.%02u.%02u-%02u/%02u/%04u
# qbot_run_mutex='%s' username='%S' 
# qbot_conf_path='%S' username='%S' 
# 1.nvprivateoffice.info
# /t3
# %s%s/dupinst.php?n=%s&bg=%s&r=%u
# https://
# wmic process call create 'expand "%S" "%S"'

# ObtainUserAgentString
# Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0
# application/x-shockwave-flash
# image/gif
# image/jpeg
# image/pjpeg
# */*

# Loader2
# cmd.exe /c ping -n 10 localhost && rmdir /S /Q "%s"
# SOFTWARE\Microsoft\Windows\CurrentVersion\Run
# c:\hiberfil.sysss
# c:\\
# .dat
# SOFTWARE\Microsoft\Microsoft Antimalware\Exclusions\Paths
# SOFTWARE\Microsoft\Windows Defender\Exclusions\Paths
# "%s\system32\schtasks.exe" /DELETE /F /TN %s
# powershell.exe
# \System32\WindowsPowerShell\v1.0\powershell.exe
# %s \"$%s = \\\"%s\\\\; & $%s\"
# %s "$%s = \"%s\"; & $%s"
# %s\system32\
# SOFTWARE\Microsoft\Windows\CurrentVersion\Run
# NTUSER.DAT
# .lnk
# shell32.dll
#  /c ping.exe -n 6 127.0.0.1 &  type "%s\System32\calc.exe" > "%s"
# cmd.exe
# .dat
# .exe
# .cfg
# at.exe %u:%u "%s" /I
# "%s\system32\schtasks.exe" /Create /RU "NT AUTHORITY\SYSTEM" /tn %s /tr "\"%s\" /I %s" /SC ONCE /Z /ST %02u:%02u /ET %02u:%02u
# .cfg
# cscript.exe
# Set objWMIService = GetObject("winmgmts:" & "{impersonationLevel=impersonate}!\\.\%coot\cimv2")
# Set colFiles = objWMIService.ExecQuery("Select * From CIM_DataFile Where Name = '%s'")
# For Each objFile in colFiles
# objFile.Copy("%s")
# Next
# WScript.Sleep %u
# Set objWMIService = GetObject("winmgmts:" & "{impersonationLevel=impersonate}!\\.\%coot\cimv2")
# Set objProcess = GetObject("winmgmts:root\cimv2:Win32_Process")
# errReturn = objProcess.Create("%s", null, nul, nul)
# WSCript.Sleep 2000
# Set fso = CreateObject("Scripting.FileSystemObject")
# fso.DeleteFile("%s")
# SOFTWARE\Microsoft\Windows NT\CurrentVersion\ProfileList
# ProfileImagePath
# Microsoft

# Final Payload
# /t3
# 311
# WEEKLY /D TUE,WED,THU /ST 12:00:00
# HOURLY /mo 5
# i2
#  host=[
# administrator,argo,operator,administrador,user,prof,owner,usuario,admin,HP_Administrator,HP_Owner,Compaq_Owner,Compaq_Administrator
# 123,password,Password,letmein,1234,12345,123456,1234567,12345678,123456789,1234567890,qwerty,love,iloveyou,princess,pussy,master,monkey,abc123,99999999,9999999,999999,99999,9999,999,99,9,88888888,8888888,888888,88888,8888,888,88,8,77777777,7777777,777777,77777,7777,777,77,7,66666666,6666666,666666,66666,6666,666,66,6,55555555,5555555,555555,55555,5555,555,55,5,44444444,4444444,444444,44444,4444,444,44,4,33333333,3333333,333333,33333,3333,333,33,3,22222222,2222222,222222,22222,2222,222,22,2,11111111,1111111,111111,11111,1111,111,11,1,00000000,0000000,00000,0000,000,00,0987654321,987654321,87654321,7654321,654321,54321,4321,321,21,12,super,secret,server,computer,owner,backup,database,lotus,oracle,business,manager,temporary,ihavenopass,nothing,nopassword,nopass,Internet,internet,example,sample,love123,boss123,work123,home123,mypc123,temp123,test123,qwe123,pw123,root123,pass123,pass12,pass1,admin123,admin12,admin1,password123,password12,password1,default,foobar,foofoo,temptemp,temp,testtest,test,rootroot,root,fuck,zzzzz,zzzz,zzz,xxxxx,xxxx,xxx,qqqqq,qqqq,qqq,aaaaa,aaaa,aaa,sql,file,web,foo,job,home,work,intranet,controller,killer,games,private,market,coffee,cookie,forever,freedom,student,account,academia,files,windows,monitor,unknown,anything,letitbe,domain,access,money,campus,explorer,exchange,customer,cluster,nobody,codeword,codename,changeme,desktop,security,secure,public,system,shadow,office,supervisor,superuser,share,adminadmin,mypassword,mypass,pass,Login,login,passwd,zxcvbn,zxcvb,zxccxz,zxcxz,qazwsxedc,qazwsx,q1w2e3,qweasdzxc,asdfgh,asdzxc,asddsa,asdsa,qweasd,qweewq,qwewq,nimda,administrator,Admin,admin,a1b2c3,1q2w3e,1234qwer,1234abcd,123asd,123qwe,123abc,123321,12321,123123,James,John,Robert,Michael,William,David,Richard,Charles,Joseph,Thomas,Christopher,Daniel,Paul,Mark,Donald,George,Kenneth,Steven,Edward,Brian,Ronald,Anthony,Kevin,Mary,Patricia,Linda,Barbara,Elizabeth,Jennifer,Maria,Susan,Margaret,Dorothy,Lisa,Nancy,Karen,Betty,Helen,Sandra,Donna,Carol,james,john,robert,michael,william,david,richard,charles,joseph,thomas,christopher,daniel,paul,mark,donald,george,kenneth,steven,edward,brian,ronald,anthony,kevin,mary,patricia,linda,barbara,elizabeth,jennifer,maria,susan,margaret,dorothy,lisa,nancy,karen,betty,helen,sandra,donna,carol,baseball,dragon,football,mustang,superman,696969,batman,trustno1
# jHxastDcds)oMc=jvh7wdUhxcsdt2
# NtUnmapViewOfSection
# NtCreateSection
# NtMapViewOfSection
# NtWriteVirtualMemory
# NtProtectVirtualMemory
# NtClose
# QueryFullProcessImageNameW
# GetProcAddress
# kernel32.dll
# GetModuleHandleA
# ObtainUserAgentString
# Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0
# application/x-shockwave-flash
# image/gif
# image/jpeg
# image/pjpeg
# */*
# Content-Type: application/x-www-form-urlencoded
# t=%s time=[%02d:%02d:%02d-%02d/%02d/%d]
# abcdefghijklmnopqrstuvwxyz
# 1234567890
# kernel32.dll
# https://cdn.speedof.me/sample4096k.bin?r=0.%u
# 23.49.13.33:7000
# 23.49.13.33:7000