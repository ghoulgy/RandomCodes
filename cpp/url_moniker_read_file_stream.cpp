#include <windows.h>
#include <urlmon.h>
#include <iostream>
#include <string>

#pragma comment(lib, "urlmon.lib")

int main() {
    HRESULT hr = CoInitialize(NULL);
    if (FAILED(hr)) {
        std::cout << "Failed to initialize COM." << std::endl;
        return 1;
    }

    IMoniker* moniker = nullptr;
    IBindCtx* bindCtx = nullptr;
    IStream* stream = nullptr;

    LPCWSTR url = TEXT("http://127.0.0.1/haha.sct");

    hr = CreateURLMonikerEx(NULL, url, &moniker, URL_MK_UNIFORM);
    if (FAILED(hr)) {
        std::cout << "Failed to create URL moniker." << std::endl;
        CoUninitialize();
        return 1;
    }

    hr = CreateBindCtx(0, &bindCtx);
    if (FAILED(hr)) {
        std::cout << "Failed to create bind context." << std::endl;
        moniker->Release();
        CoUninitialize();
        return 1;
    }

    hr = moniker->BindToStorage(bindCtx, nullptr, IID_IStream, reinterpret_cast<void**>(&stream));
    if (FAILED(hr)) {
        std::cout << "Failed to bind URL moniker to storage." << std::endl;
        bindCtx->Release();
        moniker->Release();
        CoUninitialize();
        return 1;
    }

    const int bufferSize = 1024;
    char buffer[bufferSize];
    ULONG bytesRead = 0;

    std::cout << "URL Content:" << std::endl;

    while (SUCCEEDED(stream->Read(buffer, bufferSize, &bytesRead)) && bytesRead > 0) {
        std::cout.write(buffer, bytesRead);
    }

    stream->Release();
    bindCtx->Release();
    moniker->Release();

    CoUninitialize();

    return 0;
}