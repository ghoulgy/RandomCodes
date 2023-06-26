using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading.Tasks;

namespace myiis7project
{
    public class Program
    {
        [DllImport("kernel32.dll", SetLastError = true, CharSet = CharSet.Auto)]
        public static extern bool CreateProcess(
            string lpApplicationName,
            string lpCommandLine,
            IntPtr lpProcessAttributes,
            IntPtr lpThreadAttributes,
            bool bInheritHandles,
            uint dwCreationFlags,
            IntPtr lpEnvironment,
            string lpCurrentDirectory,
            ref STARTUPINFO lpStartupInfo,
            out PROCESS_INFORMATION lpProcessInformation
        );

        public struct STARTUPINFO
        {
            public uint cb;
            public string lpReserved;
            public string lpDesktop;
            public string lpTitle;
            public uint dwX;
            public uint dwY;
            public uint dwXSize;
            public uint dwYSize;
            public uint dwXCountChars;
            public uint dwYCountChars;
            public uint dwFillAttribute;
            public uint dwFlags;
            public short wShowWindow;
            public short cbReserved2;
            public IntPtr lpReserved2;
            public IntPtr hStdInput;
            public IntPtr hStdOutput;
            public IntPtr hStdError;
        }

        public struct PROCESS_INFORMATION
        {
            public IntPtr hProcess;
            public IntPtr hThread;
            public int dwProcessId;
            public int dwThreadId;
        }
        public class StartupInfo
        {
            // Token: 0x06000015 RID: 21 RVA: 0x000025B8 File Offset: 0x000007B8
            public StartupInfo()
            {
                this.cb = Marshal.SizeOf<Program.StartupInfo>(this);
            }

            // Token: 0x0400002A RID: 42
            public int cb;

            // Token: 0x0400002B RID: 43
            public IntPtr lpReserved = IntPtr.Zero;

            // Token: 0x0400002C RID: 44
            public IntPtr lpDesktop = IntPtr.Zero;

            // Token: 0x0400002D RID: 45
            public IntPtr lpTitle = IntPtr.Zero;

            // Token: 0x0400002E RID: 46
            public int dwX;

            // Token: 0x0400002F RID: 47
            public int dwY;

            // Token: 0x04000030 RID: 48
            public int dwXSize;

            // Token: 0x04000031 RID: 49
            public int dwYSize;

            // Token: 0x04000032 RID: 50
            public int dwXCountChars;

            // Token: 0x04000033 RID: 51
            public int dwYCountChars;

            // Token: 0x04000034 RID: 52
            public int dwFillAttribute;

            // Token: 0x04000035 RID: 53
            public int dwFlags;

            // Token: 0x04000036 RID: 54
            public short wShowWindow;

            // Token: 0x04000037 RID: 55
            public short cbReserved2;

            // Token: 0x04000038 RID: 56
            public IntPtr lpReserved2 = IntPtr.Zero;

            // Token: 0x04000039 RID: 57
            public IntPtr hStdInput = IntPtr.Zero;

            // Token: 0x0400003A RID: 58
            public IntPtr hStdOutput = IntPtr.Zero;

            // Token: 0x0400003B RID: 59
            public IntPtr hStdError = IntPtr.Zero;
        }

        public struct ProcessInformation
        {
            // Token: 0x04000007 RID: 7
            public IntPtr hProcess;

            // Token: 0x04000008 RID: 8
            public IntPtr hThread;

            // Token: 0x04000009 RID: 9
            public int dwProcessId;

            // Token: 0x0400000A RID: 10
            public int dwThreadId;
        }
        public enum CreateProcessFlags : uint
        {
            // Token: 0x0400000C RID: 12
            DEBUG_PROCESS = 1U,
            // Token: 0x0400000D RID: 13
            DEBUG_ONLY_THIS_PROCESS = 2U,
            // Token: 0x0400000E RID: 14
            CREATE_SUSPENDED = 4U,
            // Token: 0x0400000F RID: 15
            DETACHED_PROCESS = 8U,
            // Token: 0x04000010 RID: 16
            CREATE_NEW_CONSOLE = 16U,
            // Token: 0x04000011 RID: 17
            NORMAL_PRIORITY_CLASS = 32U,
            // Token: 0x04000012 RID: 18
            IDLE_PRIORITY_CLASS = 64U,
            // Token: 0x04000013 RID: 19
            HIGH_PRIORITY_CLASS = 128U,
            // Token: 0x04000014 RID: 20
            REALTIME_PRIORITY_CLASS = 256U,
            // Token: 0x04000015 RID: 21
            CREATE_NEW_PROCESS_GROUP = 512U,
            // Token: 0x04000016 RID: 22
            CREATE_UNICODE_ENVIRONMENT = 1024U,
            // Token: 0x04000017 RID: 23
            CREATE_SEPARATE_WOW_VDM = 2048U,
            // Token: 0x04000018 RID: 24
            CREATE_SHARED_WOW_VDM = 4096U,
            // Token: 0x04000019 RID: 25
            CREATE_FORCEDOS = 8192U,
            // Token: 0x0400001A RID: 26
            BELOW_NORMAL_PRIORITY_CLASS = 16384U,
            // Token: 0x0400001B RID: 27
            ABOVE_NORMAL_PRIORITY_CLASS = 32768U,
            // Token: 0x0400001C RID: 28
            INHERIT_PARENT_AFFINITY = 65536U,
            // Token: 0x0400001D RID: 29
            INHERIT_CALLER_PRIORITY = 131072U,
            // Token: 0x0400001E RID: 30
            CREATE_PROTECTED_PROCESS = 262144U,
            // Token: 0x0400001F RID: 31
            EXTENDED_STARTUPINFO_PRESENT = 524288U,
            // Token: 0x04000020 RID: 32
            PROCESS_MODE_BACKGROUND_BEGIN = 1048576U,
            // Token: 0x04000021 RID: 33
            PROCESS_MODE_BACKGROUND_END = 2097152U,
            // Token: 0x04000022 RID: 34
            CREATE_BREAKAWAY_FROM_JOB = 16777216U,
            // Token: 0x04000023 RID: 35
            CREATE_PRESERVE_CODE_AUTHZ_LEVEL = 33554432U,
            // Token: 0x04000024 RID: 36
            CREATE_DEFAULT_ERROR_MODE = 67108864U,
            // Token: 0x04000025 RID: 37
            CREATE_NO_WINDOW = 134217728U,
            // Token: 0x04000026 RID: 38
            PROFILE_USER = 268435456U,
            // Token: 0x04000027 RID: 39
            PROFILE_KERNEL = 536870912U,
            // Token: 0x04000028 RID: 40
            PROFILE_SERVER = 1073741824U,
            // Token: 0x04000029 RID: 41
            CREATE_IGNORE_SYSTEM_DEFAULT = 2147483648U
        }

    }
}
