Sub Test1()
   Dim x As Long
   Dim i As Long
   Dim numrows As Long
   i = 2
   Worksheets("Sheet1").Activate
   numrows = Range("C1:C54837").Rows.Count
   Debug.Print (numrows)
   'Range("A" & 3).Value = 2
   
   For x = 1 To numrows
      If IsEmpty(Range("C" & x).Value) Then
        Range("A" & x + 1).Value = "Sentence: " & i
        i = i + 1
      End If
      ActiveCell.Offset(1, 0).Select
   Next
End Sub
