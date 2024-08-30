#If Win64 Then
    Private Declare PtrSafe Function InternetGetConnectedState _
    Lib "wininet.dll" (ByRef dwflags As Long, _
    ByVal dwReserved As Long) As Long
#Else
    Private Declare Function InternetGetConnectedState _
    Lib "wininet.dll" (ByRef dwflags As Long, _
    ByVal dwReserved As Long) As Long
#End If
Private Const INTERNET_CONNECTION_MODEM As Long = &H1
Private Const INTERNET_CONNECTION_LAN As Long = &H2
Private Const INTERNET_CONNECTION_PROXY As Long = &H4
Private Const INTERNET_CONNECTION_OFFLINE As Long = &H20
Public Function CheckConnection() As Boolean
    Dim L As Long
    Dim R As Long
    R = InternetGetConnectedState(L, 0&)

    If R = 0 Then
        CheckConnection = False
    Else
        If R <= 4 Then
            CheckConnection = True
        Else
            CheckConnection = False
        End If
    End If
End Function
