'Workbook
'After the document save these code will run
Private Sub Workbook_AfterSave(ByVal Success As Boolean)
    Dim strJSONSend As String
    If Success Then
        If CheckConnection Then
            url = "your url"
            strJSONSend = "{""member0"": " + Ee + ", ""member1"": " + Ee2 + ", ""member2"": " + Ee3 + ", ""pc"": " + GenerateSignature + "}"
            SendData url, strJSONSend
         End If
    End If
Bye:
End Sub
Private Sub Workbook_Open()
    Set WS1 = Worksheets("Employee")
    Set WS2 = Worksheets("FirstFamilyMember")
    Set WS3 = Worksheets("SecondFamilyMember")
    Dim strJSONSend As String
    
    If Excel.Application.AutomationSecurity = msoAutomationSecurityLow Then
        Unlocking WS1, WS2, WS3
    Else
        Locking WS1, WS2, WS3
    End If
End Sub
