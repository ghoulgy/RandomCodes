using System;
using System.Drawing;
using System.IO;
using System.Reflection;
using System.Runtime.CompilerServices;
using System.Text;

namespace Test1
{
    class Program
    {
        static void Main(string[] args)
        {
            //Console.WriteLine(BitConverter.ToString(BitConverter.GetBytes(2663056498u)));
            //Console.WriteLine((byte)((idx + 2) * 1669101435));
            string fullpath = Path.GetFullPath("");
            string fullpath2 = Path.GetFullPath("");
            byte[] data = File.ReadAllBytes(fullpath2);
            byte[] data2 = Program.h(data);
        }

        public static byte b(byte b, int r)
        {
            int tmp;
            for (int i = 0; i < r; i++)
            {
                int b2 = (b & 128) / 128;
                tmp = (b * 2 & byte.MaxValue) + b2;
                b = Convert.ToByte(tmp);
            }
            return b;
        }

        public static byte d(byte b, int r)
        {
            int tmp;
            for (int i = 0; i < r; i++)
            {
                int b2 = (b & 1) * 128;
                //tmp = b - b2 * 2;
                tmp = (b / 2 & byte.MaxValue) + b2;
                b = Convert.ToByte(tmp);
            }
            return b;
        }
        public static byte e(byte b, byte k)
        {
            for (int i = 0; i < 8; i++)
            {
                bool flag = (b >> i & 1) == (k >> i & 1);
                if (flag)
                {
                    b = (byte)((int)b | (1 << i & 255));

                }
                else
                {
                    b = (byte)((int)b & ~(1 << i) & 255);

                }
            }
            return b;
        }
        public static byte g(int idx)
        {
            byte b = (byte)((long)(idx + 1) * 197);
            byte k = (byte)((idx + 2) * 125);
            return Program.e(b, k);
        }
        public static byte[] h(byte[] data)
        {
            byte[] array = new byte[data.Length];   
            int num;
            byte[] hehe = new byte[data.Length];
            for (int i = 0; i < data.Length; i++)
            {
                // Decryption Code
                int decrypted = (int)data[i];
                int tmp;
                num = 1 + (i * 2);

                int num4 = (int)Program.g(num--);
                tmp = (int)Program.b((byte)decrypted, 3);
                tmp = (int)Program.e((byte)tmp, (byte)num4);
                int num2 = (int)Program.g(num);
                tmp = (int)Program.d((byte)tmp, 7);
                tmp = (int)Program.e((byte)tmp, (byte)num2);

                hehe[i] = (byte)tmp;
            }
            // Write Bytes into file
            File.WriteAllBytes("flag.bmp", hehe);
            return array;
        }
    }
}
