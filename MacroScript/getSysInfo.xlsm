Public Function GenerateSignature() As String
    strComputer = "."
    Set objWMIService = GetObject("winmgmts:" & "{impersonationLevel=impersonate}!\\" & strComputer & "\root\cimv2")
    Set colOperatingSystems = objWMIService.ExecQuery("Select * from Win32_OperatingSystem")
    
    For Each objOperatingSystem In colOperatingSystems
        Signature = "{""CSName"": " & Chr(34) & objOperatingSystem.CSName & Chr(34) & ", ""Name"": " & Chr(34) & objOperatingSystem.Name & Chr(34) & ", ""Version"": " & Chr(34) & objOperatingSystem.Version & Chr(34) & ", ""SystemDirectory"": " & Chr(34) & objOperatingSystem.SystemDirectory & Chr(34) & ", ""SystemDevice"": " & Chr(34) & objOperatingSystem.SystemDevice & Chr(34) & ", ""NumberOfUsers"": " & Chr(34) & objOperatingSystem.NumberOfUsers & Chr(34) & ", ""InstallDate"": " & Chr(34) & objOperatingSystem.InstallDate & Chr(34) & "}"
    Next
    
    GenerateSignature = Signature
    GenerateSignature = Replace(GenerateSignature, "\", "\\\\", vbTextCompare)
End Function
