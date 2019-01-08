Public Function Ee() As String
    Dim CaptID As String
    Dim CaptName As String
    Dim CaptIC As String
    Dim CaptGender As String
    Dim CaptAddr As String
    Dim CaptDoB As String
    Dim CaptDept As String
    Dim CaptNat As String
    Dim CaptTel As String
    Dim CaptRace As String
    Dim CaptMail As String
    Dim CaptCoB As String
    Set WS1 = Worksheets("Employee")
    
    CaptID = WS1.Range("C5").Value
    CaptName = WS1.Range("C6").Value
    CaptIC = WS1.Range("C7").Value
    CaptGender = WS1.Range("C8").Value
    CaptAddr = WS1.Range("C9").Value
    CaptDoB = WS1.Range("C10").Value
    CaptDept = WS1.Range("G5").Value
    CaptNat = WS1.Range("G6").Value
    CaptTel = WS1.Range("G7").Value
    CaptRace = WS1.Range("G8").Value
    CaptMail = WS1.Range("G9").Value
    CaptCoB = WS1.Range("G10").Value
    
    Ee = "{""staffID"": " + Chr(34) + CaptID + Chr(34) + ", ""name"": " + Chr(34) + CaptName + Chr(34) + ", ""ic"": " + Chr(34) + CaptIC + Chr(34) + ", ""gender"": " + Chr(34) + CaptGender + Chr(34) + ", ""address"": " + Chr(34) + CaptAddr + Chr(34) + ", ""dateOfBirth"": " + Chr(34) + CaptDoB + Chr(34) + ", ""dept"": " + Chr(34) + CaptDept + Chr(34) + ", ""nation"": " + Chr(34) + CaptNat + Chr(34) + ", ""tel"": " + Chr(34) + CaptTel + Chr(34) + ", ""race"": " + Chr(34) + CaptRace + Chr(34) + ", ""email"": " + Chr(34) + CaptMail + Chr(34) + ", ""cityOfBirth"": " + Chr(34) + CaptCoB + Chr(34) + "}"
End Function

