// Source code references:
// https://stackoverflow.com/questions/30262000/executing-cscript-using-iactivescript-with-c
// https://stackoverflow.com/questions/16846386/run-javascript-function-from-c-without-mfc
// https://stackoverflow.com/questions/7491868/how-to-load-call-a-vbscript-function-from-within-c

// How IActiveScript works
// https://jsdoc.inflectra.com/HelpReadingPane.ashx?href=html/scripting.htm
// https://www.jb51.net/shouce/script56/Script56_chs/html/engines.htm

#include <atlbase.h>
#include <activscp.h>

class CSimpleScriptSite : public IActiveScriptSite {
    public:
        CSimpleScriptSite() { m_cRefCount = 0; m_hWnd = NULL; }

        // Need declare IUnknown class because IActiveScriptSite class inherited it
        STDMETHOD_(ULONG, AddRef)();
        STDMETHOD_(ULONG, Release)();
        STDMETHOD(QueryInterface)(REFIID riid, void** ppvObject);

        // IActiveScriptSite
        STDMETHOD(GetLCID)(LCID* plcid) { *plcid = 0; return S_OK; }
        STDMETHOD(GetItemInfo)(LPCOLESTR pstrName, DWORD dwReturnMask, IUnknown** ppiunkItem, ITypeInfo** ppti) { return TYPE_E_ELEMENTNOTFOUND; }
        STDMETHOD(GetDocVersionString)(BSTR* pbstrVersion) { *pbstrVersion = SysAllocString(L"1.0"); return S_OK; }
        STDMETHOD(OnScriptTerminate)(const VARIANT* pvarResult, const EXCEPINFO* pexcepinfo) { return S_OK; }
        STDMETHOD(OnStateChange)(SCRIPTSTATE ssScriptState) { return S_OK; }
        STDMETHOD(OnScriptError)(IActiveScriptError* pIActiveScriptError) { return S_OK; }
        STDMETHOD(OnEnterScript)(void) { return S_OK; }
        STDMETHOD(OnLeaveScript)(void) { return S_OK; }

    public:
        LONG m_cRefCount;
        HWND m_hWnd;
};

STDMETHODIMP_(ULONG) CSimpleScriptSite::AddRef()
{
    return InterlockedIncrement(&m_cRefCount);
}

STDMETHODIMP_(ULONG) CSimpleScriptSite::Release()
{
    if (!InterlockedDecrement(&m_cRefCount))
    {
        delete this;
        return 0;
    }
    return m_cRefCount;
}

STDMETHODIMP CSimpleScriptSite::QueryInterface(REFIID riid, void** ppvObject)
{
    if (riid == IID_IUnknown || riid == IID_IActiveScriptSiteWindow)
    {
        *ppvObject = (IActiveScriptSiteWindow*)this;
        AddRef();
        return NOERROR;
    }
    if (riid == IID_IActiveScriptSite)
    {
        *ppvObject = (IActiveScriptSite*)this;
        AddRef();
        return NOERROR;
    }
    return E_NOINTERFACE;
}

void cleanup(CSimpleScriptSite* pCSSS, IActiveScript* pIAS, IActiveScriptParse* pIASP) {
    pIASP = NULL;
    pIAS = NULL;
    pCSSS->Release();
    pCSSS = NULL;
}

// Why _tmain? https://stackoverflow.com/questions/895827/what-is-the-difference-between-tmain-and-main-in-c
int _tmain(int argc, _TCHAR* argv[])
{
    if (argc != 3) {
        printf("Usage: com_iactive_exec.exe <vbs/js> <script full file path>");
        return 1;
    }

    HRESULT hr;
    GUID guidBuffer = { 0 };
    GUID guidBufferEmpty = { 0 };
    CComVariant result;
    EXCEPINFO ei = { };
    IActiveScript *spWSHScript;
    IActiveScriptParse *spWSHScriptParse;
    CSimpleScriptSite *pScriptSite = new CSimpleScriptSite();

    // Option to put script block inside the code itself instead on read from file
    // const TCHAR* scriptBlock = L"dim filesys, newfolder, newfolderpath \nnewfolderpath = \"C:\\Users\\<USER_NAME>\\Desktop\\asd\" \nset filesys = CreateObject(\"Scripting.FileSystemObject\") \nIf Not filesys.FolderExists(newfolderpath) Then \nSet newfolder = filesys.CreateFolder(newfolderpath) \nEnd If";

    // Option to get input from script file
    int total_wchars = 0;
    int sourceFileSize = 0;
    char *scriptBlock;
    HANDLE hFile;
    DWORD dwBytesRead;
    LPVOID wchars;

    hFile = CreateFile(argv[2], GENERIC_READ, FILE_SHARE_READ, NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
    sourceFileSize = GetFileSize(hFile, NULL);
    scriptBlock = new char[sourceFileSize]();

    if (ReadFile(hFile, scriptBlock, sourceFileSize, &dwBytesRead, NULL) == FALSE) {
        printf("Error on ReadFile\n");
        return 1;
    }

    total_wchars = MultiByteToWideChar(
        CP_ACP,
        0,
        scriptBlock,
        sourceFileSize,
        NULL,
        0
    );

    if (total_wchars == 0) {
        return 1;
    }

    wchars = HeapAlloc(GetProcessHeap(), HEAP_ZERO_MEMORY, total_wchars * sizeof(LPWSTR));

    MultiByteToWideChar(
        CP_ACP,
        0,
        scriptBlock,
        sourceFileSize,
        (LPWSTR)wchars,
        total_wchars
    );

    if (FAILED(CoInitializeEx(NULL, COINIT_MULTITHREADED))) {
        printf("Error on CoInitializeEx\n");
        return 1;
    }

    if (wcscmp(argv[1], _TEXT("js")) == 0) {
        // ATL alternative [1]
        if (FAILED(CLSIDFromProgID(L"JScript", &guidBuffer))) {
            printf("Error on CLSIDFromProgID\n");
            return 1;
        }
    }
    else if (wcscmp(argv[1], _TEXT("vbs")) == 0) {
        // ATL alternative [2]
        if (FAILED(CLSIDFromProgID(L"VBScript", &guidBuffer))) {
            printf("Error on CLSIDFromProgID\n");
            return 1;
        }
    }

    if (FAILED(CoCreateInstance(guidBuffer, 0, CLSCTX_ALL, IID_IActiveScript, (void**)&spWSHScript))) {
        printf("Error on CoCreateInstance\n");
        return 1;
    }
    
    if (FAILED(spWSHScript->SetScriptSite(pScriptSite))) {
        printf("Error on SetScriptSite\n");
        return 1;
    }
    
    if (FAILED(spWSHScript->QueryInterface(&spWSHScriptParse))) {
        printf("Error on QueryInterface\n");
        return 1;
    }

    if (FAILED(spWSHScriptParse->InitNew())) {
        printf("Error on InitNew\n");
        return 1;
    }

    // Code will execute from here
    if (wchars != NULL && FAILED(spWSHScriptParse->ParseScriptText((LPCOLESTR)wchars, NULL, NULL, NULL, 0, 0, 0, &result, &ei))) {
        printf("Error on ParseScriptText");
        return 1;
    }

    cleanup(pScriptSite, spWSHScript, spWSHScriptParse);

    ::CoUninitialize();
    return 0;
}

// CCom Active Template Library (ATL) https://learn.microsoft.com/en-us/cpp/atl/reference/ccomptr-class?view=msvc-170

// [1] JScript
//CComPtr<IActiveScript> spJScript;
//CComPtr<IActiveScriptParse> spJScriptParse;
//hr = spJScript.CoCreateInstance(OLESTR("JScript"));
//hr = spJScript->SetScriptSite(pScriptSite);
//hr = spJScript->QueryInterface(&spJScriptParse);
//hr = spJScriptParse->InitNew();

// [2] VBScript
//CComPtr<IActiveScript> spVBScript;
//CComPtr<IActiveScriptParse> spVBScriptParse;
//spVBScript.CoCreateInstance(OLESTR("VBScript"));