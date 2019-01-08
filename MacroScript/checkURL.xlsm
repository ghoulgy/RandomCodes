Public Function URLCheck(ByVal urlStr As String) As Boolean
    Set objXmlHttp = CreateObject("Msxml2.ServerXMLHTTP")
    objXmlHttp.Open "HEAD", urlStr, False
    On Error GoTo Bye
    objXmlHttp.Send
    
    If objXmlHttp.Status = 200 Then
        URLCheck = True
    Else
        URLCheck = False
    End If
Bye:
End Function
