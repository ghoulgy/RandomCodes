Attribute VB_Name = "Module1"
Sub Test1()
   Dim x As Integer
   Dim i As Integer
   i = 2
   Worksheets("Sheet1").Activate
   numrows = Range("A1:A14").Rows.Count
   Debug.Print (numrows)
   Range("A" & 3).Value = 2
   
   For x = 1 To numrows
      If IsEmpty(Range("A" & x).Value) Then
        Range("B" & x + 1).Value = "Sentence: " & i
        i = i + 1
      End If
      ActiveCell.Offset(1, 0).Select
   Next
End Sub
