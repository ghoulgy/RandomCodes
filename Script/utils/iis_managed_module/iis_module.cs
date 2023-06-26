// Please add strong name signing before install it via gacutil.exe
// Generate key file: sn.exe -k <OUTPUT_FILE>
// https://learn.microsoft.com/en-us/dotnet/standard/assembly/sign-strong-name
using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text;
using System.Web;
using static iis_module.Program;

namespace iis_module
{
    public class Class1: IHttpModule
    {
        public void Init(HttpApplication context)
        {
            context.BeginRequest += OnBeginRequest;
        }

        public void Dispose() { }

        private void OnBeginRequest(object sender, EventArgs e)
        {
            // Custom logic to be executed when a request begins
            HttpApplication httpApplication = (HttpApplication)sender;
            HttpContext context = httpApplication.Context;
            HttpRequest request = httpApplication.Request;

            STARTUPINFO startupInfo = new STARTUPINFO();
            PROCESS_INFORMATION processInfo = new PROCESS_INFORMATION();
            Program.CreateProcess("C:\\Windows\\System32\\cmd.exe", "/c mkdir C:\\ProgramData\\lol", IntPtr.Zero, IntPtr.Zero, false, 
                0, IntPtr.Zero, null, ref startupInfo, out processInfo);
        }
    }
}
