// In short: Export -> Encode -> toString -> WriteFile
#pragma comment(lib, "crypt32.lib")

#include <stdio.h>
#include <stdlib.h>
#include <tchar.h>
#include <windows.h>
#include <Wincrypt.h>

void MyHandleError(LPTSTR psz)
{
    _ftprintf(stderr, TEXT("An error occurred in the program. \n"));
    _ftprintf(stderr, TEXT("%s\n"), psz);
    _ftprintf(stderr, TEXT("Error number %x.\n"), GetLastError());
    _ftprintf(stderr, TEXT("Program terminating. \n"));
    exit(1);
}

int main()
{
    // Choose private or public key
    BOOL is_prv = false;

    // Crypto handler
    HCRYPTPROV hCryptProv;
    HCRYPTKEY hkey;

    // Crypto container name
    LPCTSTR pszContainerName = TEXT("dasdasd");

    // Acquire crypto context
    if (CryptAcquireContext(&hCryptProv, pszContainerName, NULL, PROV_RSA_FULL, 0)) {
        _tprintf(TEXT("Yeah: %s\n"), pszContainerName);
    }
    else
    {
        if (GetLastError() == NTE_BAD_KEYSET) {
            if (CryptAcquireContext(&hCryptProv, pszContainerName, NULL, PROV_RSA_FULL, CRYPT_NEWKEYSET)) {
                printf("Key container created\n");
            }
            else {
                MyHandleError((LPTSTR)(L"Error: Create new key container failed\n"));
            }
        }
        else {
            MyHandleError((LPTSTR)(L"Error: CryptAcquireContext failed\n"));
        }
    }
    
    // Fetch user key if there is any
    if(CryptGetUserKey(hCryptProv, AT_SIGNATURE, &hkey)) {
        printf("Signature key available\n");
    }
    else {
        if (GetLastError() == NTE_NO_KEY) {
            printf("Create signature key pair\n");
            // Generate user key if no key was found
            if (CryptGenKey(hCryptProv, AT_SIGNATURE, 0x8000001, &hkey)) 
            {
                printf("Gen key pair success\n");
            }
        }
        else {
            MyHandleError((LPTSTR)L"Error other than NTE_NO_KEY\n");
        }
    }
    
    if (is_prv) {
        LPBYTE prvData = NULL;
        DWORD prvwDataLen = 0;

        // Export private key
        if (CryptExportKey(hkey, NULL, PRIVATEKEYBLOB, 0, NULL, &prvwDataLen)) {            // Get buffer size of the private key
            if (prvData = (LPBYTE)malloc(prvwDataLen)) {                                    // Alloc space for the private key data buffer
                if (CryptExportKey(hkey, NULL, PRIVATEKEYBLOB, 0, prvData, &prvwDataLen)) { // Export it into the allocated memory
                    printf("[+] Export private key sucess\n");
                }
                else {
                    return FALSE;
                }
            }
            else {
                return FALSE;
            }
        }
        else {
            return FALSE;
        }
        
        LPBYTE prvDER = NULL;
        // Convert to DER private key format (Binary format)
        if (CryptEncodeObjectEx(X509_ASN_ENCODING | PKCS_7_ASN_ENCODING, PKCS_RSA_PRIVATE_KEY, prvData, 0, NULL, NULL, &prvwDataLen)) {           // Get size of encode private key
            if (prvDER = (LPBYTE)LocalAlloc(0, prvwDataLen)) {                                                                                    // Memory allocation for encode private key
                if (CryptEncodeObjectEx(X509_ASN_ENCODING | PKCS_7_ASN_ENCODING, PKCS_RSA_PRIVATE_KEY, prvData, 0, NULL, prvDER, &prvwDataLen)) { // Store encoded private key into buffer
                    printf("[+] Key encoded with X509_ASN_ENCODING | PKCS_7_ASN_ENCODING.\n");
                }
                else {
                    return FALSE;
                }
            }
            else {
                return FALSE;
            }
        }
        else {
            return FALSE;
        }

        DWORD prvPemSize = 0;
        LPSTR prvPEM = NULL;
        // Convert binary format to base64 format
        if (CryptBinaryToStringA(prvDER, prvwDataLen, CRYPT_STRING_BASE64, NULL, &prvPemSize)) {            // Get size of encoded private key
            if (prvPEM = (LPSTR)LocalAlloc(0, prvPemSize)) {                                                // Memory allocation for base64 private key
                if (CryptBinaryToStringA(prvDER, prvwDataLen, CRYPT_STRING_BASE64, prvPEM, &prvPemSize)) {  // Store converted private key format into buffer
                    printf("[+] Print encoded private key\n");
                    printf("%s", prvPEM);
                }
            }
        }

        DWORD dwPrvBytesWritten = 0;
        HANDLE hPrvKeyFile = CreateFile((LPTSTR)L"prv2.key", GENERIC_WRITE, 0, NULL, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
        if (WriteFile(hPrvKeyFile, prvPEM, prvPemSize, &dwPrvBytesWritten, NULL)) {
            printf("[+] WriteFile sucess\n");
        }
        else {
            printf("[-] WriteFile failed\n");
        }

        /*
        unsigned char* prvBytes = new unsigned char[prvwDataLen];
        DWORD dwPrvBytesWritten = 0;
        HANDLE hPrvKeyFile;
        memcpy(prvBytes, prvData, prvwDataLen);
        hPrvKeyFile = CreateFile((LPTSTR)L"prv2.key", GENERIC_WRITE, 0, NULL, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
        WriteFile(hPrvKeyFile, prvBytes, prvwDataLen, &dwPrvBytesWritten, NULL);
        CloseHandle(hPrvKeyFile);
        */
    }
    else {
        LPBYTE pubData = NULL;
        DWORD pdwDataLen = 0;

        DWORD pubKeySize = 0;
        PCERT_PUBLIC_KEY_INFO pubKeyInfo;
        if (CryptExportPublicKeyInfo(hCryptProv, AT_SIGNATURE, X509_ASN_ENCODING | PKCS_7_ASN_ENCODING, NULL, &pubKeySize)) {
            if (pubKeyInfo = (PCERT_PUBLIC_KEY_INFO)LocalAlloc(0, pubKeySize)) {
                if (CryptExportPublicKeyInfo(hCryptProv, AT_SIGNATURE, X509_ASN_ENCODING | PKCS_7_ASN_ENCODING, pubKeyInfo, &pubKeySize)) {
                    printf("[+] Export public key sucess\n");
                }
                else {
                    return false;
                }
            }
            else {
                return false;
            }
        }
        else 
        {
            return false;
        }

        LPBYTE pubKeyDER = NULL;
        if (CryptEncodeObjectEx(X509_ASN_ENCODING | PKCS_7_ASN_ENCODING, X509_PUBLIC_KEY_INFO, pubKeyInfo, 0, NULL, NULL, &pubKeySize)) {
            if (pubKeyDER = (LPBYTE)LocalAlloc(0, pubKeySize)) {
                if (CryptEncodeObjectEx(X509_ASN_ENCODING | PKCS_7_ASN_ENCODING, X509_PUBLIC_KEY_INFO, pubKeyInfo, 0, NULL, pubKeyDER, &pubKeySize)) {
                    printf("[+] Encode public key sucess\n");
                }
                else {
                    return false;
                }
            }
            else {
                return false;
            }
        }
        else {
            return false;
        }

        LPSTR pubKeyPEM = NULL;
        DWORD pubKeyPemSize = 0;
        if (CryptBinaryToStringA(pubKeyDER, pubKeySize, CRYPT_STRING_BASE64, NULL, &pubKeyPemSize)) {
            if (pubKeyPEM = (LPSTR)LocalAlloc(0, pubKeyPemSize)) {
                if (CryptBinaryToStringA(pubKeyDER, pubKeySize, CRYPT_STRING_BASE64, pubKeyPEM, &pubKeyPemSize)) {
                    printf("[+] Print encoded public key\n");
                    printf("%s", pubKeyPEM);
                }
            }
        }

        DWORD dwPubKeyBytesWritten = 0;
        HANDLE hPubKeyFile = CreateFile((LPTSTR)L"pub2.key", GENERIC_WRITE, 0, NULL, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
        if (WriteFile(hPubKeyFile, pubKeyPEM, pubKeyPemSize, &dwPubKeyBytesWritten, NULL)) {
            printf("[+] WriteFile sucess\n");
        }
        else {
            printf("[-] WriteFile failed\n");
        }
        CloseHandle(hPubKeyFile);
    }
    
    // Destroy Context
    // CryptAcquireContext(&hCryptProv, pszContainerName, NULL, PROV_RSA_FULL, CRYPT_DELETEKEYSET);

    if (hkey)
    {
        if (!(CryptDestroyKey(hkey))) {
            printf("Destroy key handler failed\n");
        }
        else
        {
            printf("Destroy key handler success\n");
        }

        hkey = NULL;
    }

    if (hCryptProv)
    {
        if (!(CryptReleaseContext(hCryptProv, 0)))
        {
            MyHandleError((LPTSTR)(L"Error: crypt release context handler failed\n"));
        }
        else
        {
            printf("Destroy context handler success\n");
        }
    }

    return 0;
}