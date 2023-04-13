#include <ShlObj.h>
#include <iostream>
#include <objidl.h>

int main()
{
    wchar_t filePath[] = L"C:\\Users\\<USER_NAME>\\Desktop\\calc.exe";
    IShellFolder* desktopFolder;
    IContextMenu* contextMenu;
    LPITEMIDLIST pidl = NULL;
    LPITEMIDLIST ppidlLast = NULL;

    if (FAILED(CoInitialize(NULL)))
    {
        printf("Failed to initialize COM\n");
        return 1;
    }

    if (FAILED(SHParseDisplayName((LPCWSTR)filePath, NULL, &pidl, 0x70C58008, NULL))) {
        printf("[-] Failed SHParseDisplayName\n");
        return 1;
    }

    if (FAILED(SHBindToParent(pidl, IID_IShellFolder, (void**)&desktopFolder, (LPCITEMIDLIST*)&ppidlLast))) {
        printf("[-] Failed SHBindToParent\n");
        return 1;
    }

    if (FAILED(desktopFolder->GetUIObjectOf(0, 1, (LPCITEMIDLIST*)&ppidlLast, IID_IContextMenu, NULL, (LPVOID*)&contextMenu)))
    {
        printf("[-] Failed GetUIObjectOf\n");
        return 1;
    }

    desktopFolder->Release();
    HMENU popMenu = CreatePopupMenu();

    if (FAILED(contextMenu->QueryContextMenu(popMenu, 0, 1, 0x7FFF, CMF_DEFAULTONLY)))
    {
        printf("[-] Failed QueryContextMenu\n");
        contextMenu->Release();
        desktopFolder->Release();
        ppidlLast = NULL;
        CoTaskMemFree(ppidlLast);

        return 1;
    }

    CMINVOKECOMMANDINFOEX invokeInfo = { 0 };
    invokeInfo.cbSize = sizeof(invokeInfo); // 0x68
    invokeInfo.fMask = 0x4500;
    invokeInfo.hwnd = 0;
    invokeInfo.lpVerb = (LPCSTR)0x1b; // Open
    invokeInfo.lpParameters = "";
    //invokeInfo.lpDirectory = NULL;
    invokeInfo.nShow = SW_SHOWNORMAL;
    //invokeInfo.dwHotKey = NULL;
    //invokeInfo.hIcon = NULL;
    //invokeInfo.lpTitle = NULL;
    //invokeInfo.lpVerbW = (LPCWSTR)L"open";
    //invokeInfo.lpParametersW = (LPCWSTR)L"";
    //invokeInfo.lpDirectoryW = NULL;
    //invokeInfo.lpTitleW = NULL;

    if (FAILED(contextMenu->InvokeCommand((CMINVOKECOMMANDINFO*)&invokeInfo)))
    {
        printf("[-] Failed InvokeCommand\n");
        return 1;
    }

    contextMenu->Release();
    ppidlLast = NULL;
    CoTaskMemFree(ppidlLast);
    CoUninitialize();

    return 0;
}