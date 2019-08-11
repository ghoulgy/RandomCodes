using System;
using System.Linq;
using System.Text;

namespace BHUSA2019_FlareOn_Special
{
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("Stage 1 Password: RAINBOW");
            char[] pass2 = { '\u0003', '"', '"', '"', '%', '\u0014', '\u000e', '.', '?', '=', ':', '9' };
            byte[] pass2_byte = new byte[pass2.Length];

            for (int i = 0; i < pass2.Length; i++)
            {
                pass2_byte[i] = Convert.ToByte(pass2[i]);
                //Console.Write("{0} ", Convert.ToByte(pass2[i]));
            }
            // Stage 2
            string stage2_pwd_xored = isValidWeaponCode("\u0003\"\"\"%\u0014\u000e.?=:9"); //Bagel_Cannon
            Console.WriteLine("Stage 2 Password: {0}", stage2_pwd_xored);

            // Stage 3
            string b64Enc = Convert.ToBase64String(Encoding.UTF8.GetBytes("Bagel_Cannon"));
            byte[] cat = Encoding.UTF8.GetBytes(b64Enc);
            byte[] ICC = InvertCosmicConstants(cat);
            byte[] results = { 95, 193, 50, 12, 127, 228, 98, 6, 215, 46, 200, 106, 251, 121, 186, 119, 109, 73, 35, 14, 20 };
            AssignFelineDesignation(results);
        }
        //Stage 2 Pwd Code
        public static string isValidWeaponCode(string s)
        {
            string stage2_Pwd = "";
            char[] array = s.ToCharArray();
            int length = s.Length;
            for (int i = 0; i < length; i++)
            {
                char[] array2 = array;
                int num = i;
                array2[num] ^= (char)(65 + i * 2);
            }
            for (int i = 0; i < length; i++)
            {
                stage2_Pwd += Encoding.ASCII.GetString(new[] { (byte)array[i] });
            }
            return stage2_Pwd;
            //return array.SequenceEqual(new char[]
            //{
            //    '\u0003',
            //    '"',
            //    '"',
            //    '"',
            //    '%',
            //    '\u0014',
            //    '\u000e',
            //    '.',
            //    '?',
            //    '=',
            //    ':',
            //    '9'
            //});
        }
        // Stage 3 Pwd Code
        public const byte MaxValue = 255;
        private static void AssignFelineDesignation(byte[] data)
        {
            string b64Enc = Convert.ToBase64String(Encoding.UTF8.GetBytes("Bagel_Cannon"));
            string stage3_Pwd = "";
            byte[] cat = Encoding.UTF8.GetBytes(b64Enc);
            byte[] s = InvertCosmicConstants(cat);
            int i = 0;
            int j = 0;

            foreach (byte ab in data)
            {
                i = i + 1 & 255;
                j = j + s[i] & 255;
                CatFact(s, i, j);
                stage3_Pwd += Encoding.ASCII.GetString(new[] { (byte)(ab ^ s[s[i] + s[j] & 255]) });
            }
            Console.WriteLine("Stage 3 Password: {0}", stage3_Pwd);
        }
        private static byte[] InvertCosmicConstants(byte[] cat)
        {
            byte[] array = (from i in Enumerable.Range(0, 256)
                            select (byte)i).ToArray();
            int j = 0;
            int num = 0;
            while (j < 256)
            {
                num = num + cat[j % cat.Length] + array[j] & 255;
                CatFact(array, j, num);
                j++;
            }
            return array;
        }
        private static void CatFact(byte[] s, int i, int j)
        {
            byte b = s[i];
            s[i] = s[j];
            s[j] = b;
        }
    }
}
