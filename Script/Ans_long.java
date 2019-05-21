import java.io.PrintStream;
import java.util.Scanner;

public class Hello_long {

    public Hello_long() {}

    public static Boolean securing_fsecure(String paramString) {
        boolean bool = false;
        long parsedLong = Long.parseLong(paramString);
        // System.out.println(parsedLong);
        if (42L + -37L * parsedLong == 17206538690L) {
          bool = true;
          String flag = getHexString(paramString);
          System.out.println("Flag: " + flag);
          System.out.println("Yay! I think I got it!? The flag is here somewhere...");
        }
        return Boolean.valueOf(bool);
    }

    public static String getHexString(String paramString) {
        String str = hexToASCII("" + paramString.charAt(10) + paramString.charAt(19) + paramString.charAt(4) + paramString.charAt(12) + paramString.charAt(6) + paramString.charAt(8) + paramString.charAt(1) + paramString.charAt(16) + paramString.charAt(2) + "c" + paramString.charAt(6) + "f" + paramString.charAt(1) + "e" + paramString.charAt(2) + paramString.charAt(4) + paramString.charAt(19) + paramString.charAt(12) + paramString.charAt(4) + paramString.charAt(16) + paramString.charAt(10) + paramString.charAt(15) + paramString.charAt(19) + paramString.charAt(7) + paramString.charAt(4) + paramString.charAt(11));
        return str;
    }

    public static String hexToASCII(String paramString) {
        StringBuilder localStringBuilder = new StringBuilder("");
        for (int i = 0; i < paramString.length(); i += 2) {
          localStringBuilder.append((char)Integer.parseInt(paramString.substring(i, i + 2), 16));
        }
        return localStringBuilder.toString();
    }

    public static void main(String[] paramArrayOfString) throws Exception {
        // Testing PlayGround 
        // 64-bit 2^64 == 18446744073709551616
        // Max = 9223372036854775807, Min = -9223372036854775808 

        long test1 = 42L + -37L * -4487045856232229816L;
        long test2 = 17206538648L * 1495681951922396077L; // 4487045856232229816L

        System.out.println("Test1: " + test1 + "\nTest2: " + test2);

        // String str = getHexString("-4487045856232229816");
        // System.out.println(str);

        if (securing_fsecure("-4487045856232229816").booleanValue() == true) {
          System.out.println("You got it! Good job!!!");
        }
        else
        {
          System.out.println("You're good with numbers for sure. :P");
        }
    }
}
