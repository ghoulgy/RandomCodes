using System;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;

namespace DarkCrypto
{
    class Program
    {
        private static readonly string PasswordHash = "ADMIN";
        private static readonly string SaltKey = "SALTYKEY";
        static readonly string desktop_ini = @"C:\<YOUR_PATH_HERE>\<YOUR_FILE_NAME>";  // type desktop.ini > keyVal.txt
        static void Main(string[] args)
        {
            // Finding the correct IV (In this case is GUID[0:16])
            string keyVal = File.ReadAllText(desktop_ini);
            keyVal = keyVal.Substring(0, keyVal.Length - 1);    // Remove the '/n'
            string dec_keyVal = "";
            byte[] enc_keyVals = Encoding.UTF8.GetBytes(keyVal);
            foreach (byte enc_keyVal in enc_keyVals)
            {
                dec_keyVal += Encoding.ASCII.GetString(new[] { (byte)((int)enc_keyVal ^ 293) });
            }
            Console.WriteLine("Decrypted key & value pair: {0}", dec_keyVal);
            string IV_GUID = dec_keyVal.Substring(dec_keyVal.Length - 16);  // 51d0de1c-958f-47
            Console.WriteLine("Correct IV: {0}", IV_GUID);
            byte[] encryptedText = StringToByteArray("9a0046b4bed9938aa45bd07cbbe1903457e62f7098bda4fb42a70f65ba5433a9");   // Convert encrpyted flag into byte array
            string decryptedText = Decrypt(encryptedText, IV_GUID);
            Console.WriteLine("{0}", decryptedText);
        }
        // Decryption Of PlainText
        public static string Decrypt(byte[] encrpytedText, string IV)
        {
            string plaintext = null;
            byte[] bytes2 = new Rfc2898DeriveBytes(Program.PasswordHash, Encoding.ASCII.GetBytes(Program.SaltKey)).GetBytes(32);
            ICryptoTransform transform = new RijndaelManaged
            {
                Mode = CipherMode.CBC,
                Padding = PaddingMode.Zeros
            }.CreateDecryptor(bytes2, Encoding.ASCII.GetBytes(IV));

            using (MemoryStream memoryStream = new MemoryStream(encrpytedText))
            {
                using (CryptoStream cryptoStream = new CryptoStream(memoryStream, transform, CryptoStreamMode.Read))
                {
                    using (StreamReader srDecrypt = new StreamReader(cryptoStream))
                    {
                        plaintext = srDecrypt.ReadToEnd();
                    }
                }
            }
            return plaintext;
        }
        public static byte[] StringToByteArray(string hex)
        {
            return Enumerable.Range(0, hex.Length)
                             .Where(x => x % 2 == 0)
                             .Select(x => Convert.ToByte(hex.Substring(x, 2), 16))
                             .ToArray();
        }
    }
}