#include "pch.h"
#include <windows.h>
#include "DllRegisterServer.h"

extern int __cdecl DllRegisterServer(int start)
{
    MessageBox(0, L"Hello World!", L"Greetings", 0);
    return start + 1;
}