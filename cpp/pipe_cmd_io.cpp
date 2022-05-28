// Refer to https://docs.microsoft.com/en-us/windows/win32/procthread/creating-a-child-process-with-redirected-input-and-output

#include <windows.h> 
#include <tchar.h>
#include <stdio.h> 
#include <strsafe.h>
#include <string>
#include <iostream>

#define BUFSIZE 4096 

HANDLE g_hChildStd_IN_Rd = NULL;
HANDLE g_hChildStd_IN_Wr = NULL;
HANDLE g_hChildStd_OUT_Rd = NULL;
HANDLE g_hChildStd_OUT_Wr = NULL;

HANDLE g_hInputFile = NULL;

HANDLE CreateChildProcess(void);
void WriteToPipe(void);
void ReadFromPipe(void);
void ErrorExit(PTSTR);

int main(int argc, TCHAR* argv[]) {
    SECURITY_ATTRIBUTES saAttr;

    saAttr.nLength = sizeof(SECURITY_ATTRIBUTES);
    saAttr.bInheritHandle = TRUE;
    saAttr.lpSecurityDescriptor = NULL;

    if (!CreatePipe(&g_hChildStd_OUT_Rd, &g_hChildStd_OUT_Wr, &saAttr, 0))
        ErrorExit((PTSTR)TEXT("StdoutRd CreatePipe"));

    if (!SetHandleInformation(g_hChildStd_OUT_Rd, HANDLE_FLAG_INHERIT, 0))
        ErrorExit((PTSTR)TEXT("Stdout SetHandleInformation"));

    if (!CreatePipe(&g_hChildStd_IN_Rd, &g_hChildStd_IN_Wr, &saAttr, 0))
        ErrorExit((PTSTR)TEXT("Stdin CreatePipe"));

    if (!SetHandleInformation(g_hChildStd_IN_Wr, HANDLE_FLAG_INHERIT, 0))
        ErrorExit((PTSTR)TEXT("Stdin SetHandleInformation"));

    HANDLE hChild = CreateChildProcess();

    WriteToPipe();
    ReadFromPipe();

    CloseHandle(hChild);

    return 0;
}

HANDLE CreateChildProcess() {
    TCHAR szCmdline[] = TEXT("cmd.exe");
    PROCESS_INFORMATION piProcInfo;
    STARTUPINFO siStartInfo;
    BOOL bSuccess = FALSE;

    ZeroMemory(&piProcInfo, sizeof(PROCESS_INFORMATION));
    ZeroMemory(&siStartInfo, sizeof(STARTUPINFO));
    siStartInfo.cb = sizeof(STARTUPINFO);
    siStartInfo.hStdError = g_hChildStd_OUT_Wr;
    siStartInfo.hStdOutput = g_hChildStd_OUT_Wr;
    siStartInfo.hStdInput = g_hChildStd_IN_Rd;
    siStartInfo.dwFlags |= STARTF_USESTDHANDLES;

    bSuccess = CreateProcess(NULL,
        szCmdline,
        NULL,
        NULL,
        TRUE,
        0x8000000,
        NULL,
        NULL,
        &siStartInfo,
        &piProcInfo);

    if (!bSuccess)
        ErrorExit((PTSTR)TEXT("CreateProcess"));
    else
    {
        CloseHandle(piProcInfo.hThread);
        CloseHandle(g_hChildStd_OUT_Wr);
        CloseHandle(g_hChildStd_IN_Rd);
    }
    return piProcInfo.hProcess;
}

void WriteToPipe(void) {
    DWORD dwRead, dwWritten;
    LPVOID chBuf[BUFSIZE];
    BOOL bSuccess = FALSE;

    const char cmd_str_arr[] = "whoami /priv\r\n";
    bSuccess = WriteFile(g_hChildStd_IN_Wr, cmd_str_arr, strlen(cmd_str_arr), &dwWritten, NULL);

    if (!CloseHandle(g_hChildStd_IN_Wr))
        ErrorExit((PTSTR)TEXT("StdInWr CloseHandle"));
}

void str_cleanup(std::string& str) {
    str.erase(std::remove_if(str.begin(), str.end(),
        [](unsigned char c) {
            return !(c >= 0 && c < 128);
        }),
        str.end());
}

void ReadFromPipe(void) {
    DWORD dwRead, dwWritten;
    CHAR chBuf[BUFSIZE];
    BOOL bSuccess = FALSE;
    HANDLE hParentStdOut = GetStdHandle(STD_OUTPUT_HANDLE);

    while(ReadFile(g_hChildStd_OUT_Rd, chBuf, BUFSIZE, &dwRead, NULL) && dwRead) {
        if (dwRead < 4096) {
            Sleep(1);
            chBuf[dwRead + 1] = '\0';
            std::string cmd_output(chBuf);
            str_cleanup(cmd_output);
            std::cout << cmd_output; // Print out the memory output.
        }
    }
}

void ErrorExit(PTSTR lpszFunction) {
    LPVOID lpMsgBuf;
    LPVOID lpDisplayBuf;
    DWORD dw = GetLastError();

    FormatMessage(
        FORMAT_MESSAGE_ALLOCATE_BUFFER |
        FORMAT_MESSAGE_FROM_SYSTEM |
        FORMAT_MESSAGE_IGNORE_INSERTS,
        NULL,
        dw,
        MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT),
        (LPTSTR)&lpMsgBuf,
        0, NULL);

    lpDisplayBuf = (LPVOID)LocalAlloc(LMEM_ZEROINIT,
        (lstrlen((LPCTSTR)lpMsgBuf) + lstrlen((LPCTSTR)lpszFunction) + 40) * sizeof(TCHAR));
    StringCchPrintf((LPTSTR)lpDisplayBuf,
        LocalSize(lpDisplayBuf) / sizeof(TCHAR),
        TEXT("%s failed with error %d: %s"),
        lpszFunction, dw, lpMsgBuf);
    MessageBox(NULL, (LPCTSTR)lpDisplayBuf, TEXT("Error"), MB_OK);

    LocalFree(lpMsgBuf);
    LocalFree(lpDisplayBuf);
    ExitProcess(1);
}