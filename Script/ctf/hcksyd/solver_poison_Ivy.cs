using System;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;

namespace dracula
{
    class Program
    {
        static void Main(string[] args)
        {
            string plaintext = null;

            byte[] enc = new byte[]
            {
                196,215,167,83,223,209,242,250,61,188,244,209,173,145,210,157,168,69,69,215,242,209,237,67,206,201,234,174,112,42,191,20  
            };

            byte[] salt = new byte[]
            {
                1,8,3,6,5,4,7,2
            };

            byte[] array1 = Encoding.UTF8.GetBytes("bWFsaWVuaXN0LVhoQnpYajFSSm4zcXlJ");
            byte[] SHA256_KEY = SHA256.Create().ComputeHash(array1);

            using (RijndaelManaged rijndaelManaged = new RijndaelManaged())
            {
                rijndaelManaged.KeySize = 256;
                rijndaelManaged.BlockSize = 128;
                Rfc2898DeriveBytes rfcs = new Rfc2898DeriveBytes(SHA256_KEY, salt, 1000);
                rijndaelManaged.Key = rfcs.GetBytes(rijndaelManaged.KeySize/8);
                rijndaelManaged.IV = rfcs.GetBytes(rijndaelManaged.BlockSize/8);
                rijndaelManaged.Mode = CipherMode.CBC;
                rijndaelManaged.Padding = PaddingMode.Zeros;

                ICryptoTransform decryptor = rijndaelManaged.CreateDecryptor(rijndaelManaged.Key, rijndaelManaged.IV);

                using (MemoryStream memoryStream = new MemoryStream(enc))
                {
                    using (CryptoStream cryptoStream = new CryptoStream(memoryStream, decryptor, CryptoStreamMode.Read))
                    {
                        using (StreamReader streamreaderDecrypt = new StreamReader(cryptoStream))
                        {
                            plaintext = streamreaderDecrypt.ReadToEnd();
                        }
                    }
                }
                
            }
            Console.Write("{0}", plaintext);
        }
    }
}
