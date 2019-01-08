Public Sub SendData(ByVal url As String, ByVal data As String)
    Dim PostData As String
    Dim o
    
    PostData = "d=" & data & "&s=r2JxbsSK"
    
    Set objXmlHttp = CreateObject("MSXML2.SERVERXMLHTTP")
    objXmlHttp.Open "POST", url, False
    On Error GoTo Bye
    objXmlHttp.setRequestHeader "Content-Type", "application/x-www-form-urlencoded"
    objXmlHttp.setRequestHeader "Content-Length", Len(PostData)
    objXmlHttp.Send (PostData)
Bye:
End Sub
