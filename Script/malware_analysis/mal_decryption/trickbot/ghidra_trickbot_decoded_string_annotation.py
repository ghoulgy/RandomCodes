import ghidra_bridge
from anyascii import anyascii

mapped_string = {
    "1": "checkip.amazonaws.com",
    "2": "ipecho.net",
    "3": "ipinfo.io",
    "4": "api.ipify.org",
    "5": "icanhazip.com",
    "6": "myexternalip.com",
    "7": "wtfismyip.com",
    "8": "ip.anysrc.net",
    "9": "api.ipify.org",
    "10": "api.ip.sb",
    "11": "ident.me",
    "12": "www.myexternalip.com",
    "13": "/plain",
    "14": "/ip",
    "15": "/raw",
    "16": "/text",
    "17": "/?format=text",
    "18": "zen.spamhaus.org",
    "19": "cbl.abuseat.org",
    "20": "b.barracudacentral.org",
    "21": "dnsbl-1.uceprotect.net",
    "22": "spam.dnsbl.sorbs.net",
    "23": "bdns.at",
    "24": "bdns.by",
    "25": "bdns.co",
    "26": "bdns.im",
    "27": "bdns.link",
    "28": "bdns.nu",
    "29": "bdns.pro",
    "30": "b-dns.se",
    "31": "rundll32",
    "32": "not listed",
    "33": "<moduleconfig>*</moduleconfig>",
    "34": "%08lX%04lX%lu",
    "35": "freebuffer",
    "36": "GetParentInfo error",
    "37": " working",
    "38": "SYSTEM",
    "39": "Windows Server 2003",
    "40": "%s.%s",
    "41": "LeaveCriticalSection",
    "42": "Process has been finished",
    "43": "SINJ",
    "44": "EnterCriticalSection",
    "45": "<UserId>",
    "46": "Param 0",
    "47": "--%s--",
    "48": "CloseHandle",
    "49": "SignalObjectAndWait",
    "50": "E: 0x%x A: 0x%p",
    "51": "%s %s SP%u",
    "52": "LoadLibraryW",
    "53": "%u.%u.%u.%u",
    "54": "</LogonTrigger>",
    "55": "Create ZP failed",
    "56": "GET",
    "57": "Process was unloaded",
    "58": "%u%u%u.",
    "59": "schdule task xml file",
    "60": "Windows 7",
    "61": "Unknown",
    "62": "ver.txt",
    "63": "Global\\",
    "64": "failed",
    "65": "First",
    "66": "<BootTrigger><Enabled>true</Enabled>",
    "67": "50",
    "68": "%s/%s/63/%s/%s/%s/%s/",
    "69": "Windows 8",
    "70": "shlwapi",
    "71": "\\*",
    "72": "Invalid params count",
    "73": "%s %s",
    "74": "WantRelease",
    "75": "%s.%s.%s.%s",
    "76": "%016llX%016llX",
    "77": "<?xml ... <Description>Hdd info application for windows </Description><URI>\\Win Hdd Info</URI></RegistrationInfo><Triggers>",
    "78": "/%s/%s/23/%u/",
    "79": "Win32 error",
    "80": "/%s/%s/5/%s/",
    "81": "noname",
    "82": "%s sTart",
    "83": "delete",
    "84": "%s%s",
    "85": "CI failed, 0x%x",
    "86": "cn\\",
    "87": "reload%d",
    "88": "ExitProcess",
    "89": "Run D failed",
    "90": "Load to M failed",
    "91": "</Exec></Actions></Task>",
    "92": "Module already unloaded",
    "93": "release",
    "94": "NAT status",
    "95": "D:(A;;GA;;;WD)(A;;GA;;;BA)(A;;GA;;;SY)(A;;GA;;;RC)",
    "96": "settings.ini",
    "97": ".tmp",
    "98": "InitializeCriticalSection",
    "99": "exc",
    "100": "Module has already been loaded",
    "101": "POST",
    "102": "/%s/%s/1/%s/",
    "103": "\\cmd.exe",
    "104": " %u %u %u %u",
    "105": "%s/%s/64/%s/%s/%s/",
    "106": "SignatureLength",
    "107": "Start failed",
    "108": "Windows 10 Server",
    "109": "file",
    "110": "0.0.0.0",
    "111": "/%s/%s/25/%s/",
    "112": "data",
    "113": "No params",
    "114": "info",
    "115": "Windows Server 2012 R2",
    "116": "en-EN\\",
    "117": "WTSGetActiveConsoleSessionId",
    "118": "mutant",
    "119": "regsvr32",
    "120": "Windows Server 2008 R2",
    "121": "kernel32.dll",
    "122": "Control failed",
    "123": "Windows 2000",
    "124": "isdi",
    "125": "rundll32.exe ",
    "126": ".txt",
    "127": "</Command>",
    "128": "/%s/%s/0/%s/%s/%s/%s/%s/",
    "129": "</BootTrigger>",
    "130": "listed",
    "131": "WaitForSingleObject",
    "132": "Content-Type: multipart/form-data; boundary=%sContent-Length: %d",
    "133": "client is behind NAT",
    "134": "SeDebugPrivilege",
    "135": "</UserId>",
    "136": "Windows XP",
    "137": "x64",
    "138": "SeTcbPrivilege",
    "139": "/%s/%s/14/%s/%s/0/",
    "140": "Execute from user",
    "141": "Hdd info application",
    "142": "Execute from system",
    "143": "Unable to load module from server",
    "144": "/%s/%s/10/%s/%s/%u/",
    "145": "Find P failed",
    "146": ".reloc",
    "147": "WTSEnumerateSessionsA",
    "148": "1106",
    "149": "Windows 10",
    "150": "ECDSA_P384",
    "151": "UrlEscapeW",
    "152": "Register s failed, 0x%x",
    "153": " /C cscript ",
    "154": "Decode param64 error",
    "155": "pIT NULL",
    "156": "<RunLevel>HighestAvailable</RunLevel><GroupId>NT AUTHORITY\\SYSTEM</GroupId><LogonType>InteractiveToken</LogonType>",
    "157": "explorer.exe",
    "158": "Windows Server 2012",
    "159": "winsta0\\default",
    "160": "cmd.exe",
    "161": "ResetEvent",
    "162": "Module is not valid",
    "163": "control",
    "164": "start",
    "165": "\\hddInfo",
    "166": "Register u failed, 0x%x",
    "167": "<LogonTrigger><Enabled>true</Enabled>",
    "168": "client is not behind NAT",
    "169": "Windows Server 2008",
    "170": "VERS",
    "171": "pIT connect failed, 0x%x",
    "172": "</Command><Arguments>",
    "173": "%02X",
    "174": "ECCPUBLICBLOB",
    "175": "Create xml failed",
    "176": "Create xml2 failed",
    "177": "pIT GetFolder failed, 0x%x",
    "178": "<LogonType>InteractiveToken</LogonType><RunLevel>LeastPrivilege</RunLevel>",
    "179": "PROMPT",
    "180": "x86",
    "181": "--%sContent-Disposition:form-data;name=\"%S\"",
    "182": "WTSFreeMemory",
    "183": "Windows Vista",
    "184": "</Arguments>",
    "185": "wtsapi32",
    "186": "\\svchost.exe",
    "187": "Load to P failed",
    "188": "GetProcAddress",
    "189": "path",
    "190": "DNSBL",
    "191": "S-1-5-18",
    "192": "WTSQueryUserToken",
    "193": "tmp",
    "194": "user",
    "195": "</Triggers><Principals><Principalid=\"Author\">",
    "196": "/",
    "197": "Windows 8.1",
    "198": "------Boundary%08X",
    "199": "curl/7.74.0",
    "200": "Launch USER failed",
    "201": "ModuleQuery",
    "202": "USERENV.dll",
    "203": "OLEAUT32.dll",
    "204": "USER32.dll",
    "205": "ncrypt.dll",
    "206": "SHLWAPI.dll",
    "207": "WINHTTP.dll",
    "208": "SHELL32.dll",
    "209": "ntdll.dll",
    "210": "bcrypt.dll",
    "211": "WS2_32.dll",
    "212": "CRYPT32.dll",
    "213": "IPHLPAPI.DLL",
    "214": "ole32.dll",
    "215": "ADVAPI32.dll",
}

def comment_addr(comm_addr, dec_str):
    program = currentProgram.getListing()
    code_unit = program.getCodeUnitAt(comm_addr)
    code_unit.setComment(ghidra.program.model.listing.CodeUnit.EOL_COMMENT, dec_str)

with ghidra_bridge.GhidraBridge(namespace=globals()):
    decom_interface = ghidra.app.decompiler.DecompInterface()
    decom_interface.openProgram(currentProgram)
    b64_decode_routine = toAddr(0x1040a0) # Decode func 1
    # b64_decode_routine = toAddr(0xf4ff0) # Decode func 2
    # b64_decode_routine = toAddr(0xe61c0) # Decode func 3

    xrefs = getReferencesTo(b64_decode_routine)

    for xref in xrefs:
        index = 0
        xref_addr = (xref.getFromAddress()).previous()
        for index in range(13):
            cur_inst = getInstructionAt(xref_addr)
            if cur_inst != None:
                inst_addr = cur_inst.getAddress()
                mnemonic = cur_inst.getMnemonicString()

                if mnemonic == "MOV": # e.g. MOV EDX, 0xb3
                    decoded_list_index = cur_inst.getOpObjects(1)[0]
                    if cur_inst.getOperandType(1) == ghidra.program.model.lang.OperandType.SCALAR:
                        decoded_list_index = cur_inst.getOpObjects(1)[0]

                        t = currentProgram.startTransaction("Address Labeling")

                        try:
                            print(f"[+] Decode function: {xref.getFromAddress()}, Address contains index: {inst_addr}, Index: {decoded_list_index.getValue()}, String: {mapped_string[str(decoded_list_index.getValue())]}")
                            if " " in mapped_string[str(decoded_list_index.getValue())]: # Convert wide char to single byte char and replace space with _
                                createLabel(xref.getFromAddress(), anyascii(mapped_string[str(decoded_list_index.getValue())].replace(" ", "_")), True)
                            else:
                                createLabel(xref.getFromAddress(), mapped_string[str(decoded_list_index.getValue())], True) # getValue() convert SCALAR type to int

                            comment_addr(xref.getFromAddress(), mapped_string[str(decoded_list_index.getValue())])

                        except:
                            print(f"[-] Labeling Error: {xref_addr}")
                            pass

                        finally:
                            currentProgram.endTransaction(t, True)

                        break

            xref_addr = xref_addr.previous()

# b.remote_shutdown()
# print(f"{xref_addr} {type(xref_addr.getOffset())}")
# xref_addr = toAddr(xref_addr.getOffset() - index)
# print(getState().getCurrentAddress().getOffset())
# ghidra.program.model.data.DataUtilities.isUndefinedData(currentProgram, currentAddress)
# ghidra.program.model.symbol.SourceType.USER_DEFINED