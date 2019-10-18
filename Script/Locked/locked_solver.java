package javaapplication1;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Arrays;
import org.apache.commons.lang3.StringUtils;
import java.util.regex.Matcher; 
import java.util.regex.Pattern; 

public class JavaApplication1 {

    private static byte[][] split(byte[] bArr, int i) {
        int length = bArr.length % i;
        int i2 = 0;
        int length2 = (bArr.length / i) + (length > 0 ? 1 : 0);
        byte[][] bArr2 = new byte[length2][];
        while (true) {
            if (i2 >= (length > 0 ? length2 - 1 : length2)) {
                break;
            }
            int i3 = i2 * i;
            bArr2[i2] = Arrays.copyOfRange(bArr, i3, i3 + i);
            i2++;
        }
        if (length > 0) {
            int i4 = length2 - 1;
            int i5 = i * i4;
            bArr2[i4] = Arrays.copyOfRange(bArr, i5, length + i5);
        }
        return bArr2;
    }
    
    /**
     * @param args the command line arguments
     */
    public static void main(String[] args) throws IOException {
        // Calculate Key Solver ------------------------------------------------
        byte[] byteArray = Files.readAllBytes(Paths.get("encrypted.raw"));
        byte[] byteArray2 = Files.readAllBytes(Paths.get("stream.raw"));
        byte[][] split = split(byteArray, 256);

//        int[] first_known = {246, 253, 40, 82, 204, 182}; // opt 1
//        byte[] guess_key = "ass=\"b".getBytes(); // opt 1
//        Pattern pattern = Pattern.compile(".*cl$", Pattern.CASE_INSENSITIVE); // opt 1
//        int next_6_bytes = 0; // opt 1
        
        int[] first_known = {199, 56, 179, 196, 102, 29}; // opt 2
        byte[] guess_key = "ss=\"b\"".getBytes();   // opt 2
        Pattern pattern = Pattern.compile(".*cla$", Pattern.CASE_INSENSITIVE); // opt 2 
        int next_6_bytes = 102; // opt 2
        
        int x = 0;  // For first_known key loop 
        
        ArrayList<Integer> arl = new ArrayList<Integer>();
        for(int i=0; i<split.length; i++) {
//            System.out.print(i + ": ");
            String printable_str = new String();
            for(int j= next_6_bytes; j<first_known.length + next_6_bytes; j++) {
                if(next_6_bytes > 250) {
                    break;
                }
                char o = (char)(split[i][j] & 255 ^ first_known[x % first_known.length] & 255);

                String p = Character.toString(o);
                x++;
                if(StringUtils.isAsciiPrintable(p)) {
                    printable_str += p;
                }
                if(j == first_known.length + next_6_bytes - 1) {
                    Matcher m = pattern.matcher(printable_str);
                    if(m.find() == true) {
//                        System.out.println(i + ": " + m.group(0));
                        for(int k = 0; k < 6; k++) {
                            if(j+k+1 >= split[i].length){
//                                break;
                            } else {
                                first_known[k] = (split[i][j+k+1] ^ guess_key[k]) & 255;
                                arl.add(first_known[k]);
                            }                        
                        }
                        next_6_bytes += 6;
//                        System.out.println(next_6_bytes);
                        i = 0;
                    } 
                }
            }
//            System.out.println();
        }
        if(next_6_bytes + first_known.length > 255) {
            System.out.println("Ok Done!!");
        } else {
            System.out.println("Stuck at: " + next_6_bytes); 
            /* To_Do: chg guess_key/first_known & line 92 next_6_bytes = 102 & chg line 88 regex: .*cla
                Basically chg "opt 1" to "opt 2" */
        }
        System.out.println(arl.toString());
        // Calculate Key Solver ------------------------------------------------

        // Final Decryption 
//        int[] key2 = {246, 253, 40, 82, 204, 182, 118, 114, 81, 208, 74, 45, 50, 83, 86, 90, 159, 84, 216, 183, 87, 43, 184, 6, 125, 184, 75, 156, 166, 34, 221, 7, 165, 76, 32, 33, 129, 135, 75, 238, 179, 52, 222, 240, 68, 221, 122, 177, 43, 175, 204, 69, 166, 21, 206, 132, 95, 205, 151, 10, 241, 182, 111, 232, 108, 43, 102, 152, 144, 81, 59, 10, 219, 165, 132, 102, 192, 176, 251, 167, 201, 26, 101, 168, 12, 25, 175, 83, 175, 5, 119, 190, 141, 168, 42, 93, 109, 225, 178, 252, 118, 196, 199, 56, 179, 196, 102, 29, 203, 96, 179, 236, 148, 33, 9, 196, 203, 0, 13, 50, 159, 148, 238, 102, 182, 62, 118, 222, 90, 59, 12, 216, 90, 5, 205, 69, 99, 188, 40, 151, 87, 166, 178, 203, 25, 35, 4, 112, 229, 171, 237, 134, 88, 235, 72, 63, 74, 109, 100, 80, 129, 0, 116, 74, 219, 223, 52, 101, 218, 1, 107, 55, 51, 102, 211, 178, 200, 142, 108, 60, 98, 197, 42, 193, 225, 152, 197, 47, 17, 249, 252, 0, 216, 194, 22, 189, 55, 253, 242, 7, 181, 3, 153, 75, 164, 49, 6, 184, 15, 194, 251, 247, 138, 140, 40, 102, 171, 180, 72, 83, 91, 117, 162, 143, 213, 155, 242, 250, 61, 98, 253, 81, 119, 129, 22, 156, 242, 104, 157, 21, 216, 153, 195, 117, 9, 84, 49, 164, 222, 35, 55, 156, 125, 58, 28, 104};
//        int k = 0;
//        for(int i=0; i<split.length; i++) {
//        //            System.out.print(i + ": ");
//            for(int j= 0; j < split[i].length; j++) {
//                char o = (char)(split[i][j] & 255 ^ key2[k%key2.length] & 255);
//                String p = Character.toString(o);
//        //                System.out.print((split[i][j] & 255) + ", ");
//                k++;
//                if(StringUtils.isAsciiPrintable(p)){ // From common_langs library 
//                    System.out.print(o);
//                }
//            }
//        //            System.out.println();
//        }

//        Debug(from head)
//        int[] key2 = {199, 56, 179, 196, 102, 29}; // head
//        int k = 0;    // Loop for key2
//        for(int i=0; i<split.length; i++) {
//            System.out.print(i + ": ");
//            for(int j= 102; j < 108; j++) {
//                char o = (char)(split[i][j] & 255 ^ key2[k % key2.length] & 255);
//                String p = Character.toString(o);
////                System.out.print((split[i][j] & 255) + ", ");
//                k++;
//                if(StringUtils.isAsciiPrintable(p)){
//                    System.out.print(o);
//                }
//            }
//            System.out.println();
//        }
        
//        Debug(from last) 
//        for(int i=0; i<split.length-1; i++) {
//            System.out.print(i + ": ");
//            for(int j= split[i].length - 5; j < split[i].length; j++) {
//                char o = (char)(split[i][j] & 255 ^ key2[k%5] & 255);
//                String p = Character.toString(o);
//                k++;
//                if(StringUtils.isAsciiPrintable(p)){
//                    System.out.print(o);
//                }
//            }
//            System.out.println();
//        }      
    }
    
}
