// Test

// How to decrypt: Get shared key by using the private master key and public ecdh session key from user
// The session correct session key can be use as the AES decryption key with the saved IV to decrypt file correctly

// Please Save AES IV, public master key, session ecdh public key, encrypted bytes

// Before compile please:
// VC++ Directory -> Include Directory -> Add crpyto++ folder
// Linker -> Input -> Additional Dpeendencies -> Add fullpath of "cryptlib.lib"
// C/C++ -> Code Generation -> Runtime Library -> Change to "Multi-Threaded (MT)"

// References for crypto thingy:
// https://unit42.paloaltonetworks.com/ransom-cartel-ransomware/
// https://securelist.com/a-new-generation-of-ransomware/64608/

#include <iostream>
#include <fstream>
#include "cryptlib.h"
#include "xed25519.h"
#include "osrng.h"
#include "files.h"
#include "hex.h"
#include "rijndael.h"

#include <string>
using std::string;

#include "filters.h"
using CryptoPP::StringSink;
using CryptoPP::StringSource;
using CryptoPP::StreamTransformationFilter;

#include "aes.h"
using CryptoPP::AES;

#include "modes.h"
using CryptoPP::ECB_Mode;

int main()
{
    using namespace CryptoPP;
    HexEncoder encoder(new FileSink(std::cout));

    AutoSeededRandomPool prng;
    x25519 ecdhUsr(prng);

    // Example Random Generated master key pair
    //AutoSeededRandomPool rndA;
    //x25519 ecdhA(rndA);
    //SecByteBlock master_pk_key_sb(ecdhA.PrivateKeyLength());
    //SecByteBlock master_pb_key_sb(ecdhA.PublicKeyLength());
    //ecdhA.GenerateKeyPair(rndA, master_pk_key_sb, master_pb_key_sb);
    //std::cout << "Priv (A): ";
    //StringSource(master_pk_key_sb, master_pk_key_sb.size(), true, new Redirector(encoder));
    //std::cout << std::endl;

    // Load master public key
    std::ifstream pb_fin("master_pb.bin", std::ios::binary);
    std::vector<unsigned char> master_pb_loaded(std::istreambuf_iterator<char>(pb_fin), {});
    pb_fin.close();
    SecByteBlock master_pb_key_sb(reinterpret_cast<const unsigned char*>(master_pb_loaded.data()), 0x20);
    std::cout << "Master public key: ";
    StringSource(master_pb_key_sb, master_pb_key_sb.size(), true, new Redirector(encoder));
    std::cout << std::endl;

    // Load master private key (This must be hidden from public)
    std::ifstream pk_fin("master_pk.bin", std::ios::binary);
    std::vector<unsigned char> master_pk_loaded(std::istreambuf_iterator<char>(pk_fin), {});
    pk_fin.close();
    SecByteBlock master_pk_key_sb(reinterpret_cast<const unsigned char*>(master_pk_loaded.data()), 0x20);
    std::cout << "Master private key: ";
    StringSource(master_pk_key_sb, master_pk_key_sb.size(), true, new Redirector(encoder));
    std::cout << std::endl;

    // Create a ecdh object based on the master key pair, actually using ecdhUsr is fine. 
    x25519 ecdhMaster(master_pb_key_sb, master_pk_key_sb);

    // Load PKCS#8
    //FileSource fs("private.key.bin", true);
    //x25519 ecdh;
    //ecdh.Load(fs);
    //SecByteBlock privA(ecdh.PrivateKeyLength());
    //SecByteBlock pubA(ecdh.PublicKeyLength());
    //ecdh.GenerateKeyPair(rndA, privA, pubA);
    ////SecByteBlock sharedA(ecdh.AgreedValueLength());
    //std::cout << "Priv (A): ";
    //StringSource(privA, privA.size(), true, new Redirector(encoder));
    //std::cout << std::endl;
    //std::cout << "Pub (A): ";
    //StringSource(pubA, pubA.size(), true, new Redirector(encoder));
    //std::cout << std::endl;

    //bool valid = ecdh.Validate(prng, 3);
    //if (valid == false)
    //    throw std::runtime_error("Invalid private key");

    //std::cout << "Keys are valid" << std::endl;

    // Generate key pair from user
    SecByteBlock pkUsr(ecdhUsr.PrivateKeyLength());
    SecByteBlock pbUsr(ecdhUsr.PublicKeyLength());
    ecdhUsr.GenerateKeyPair(prng, pkUsr, pbUsr);
    std::cout << "Priv User: ";
    StringSource(pkUsr, pkUsr.size(), true, new Redirector(encoder));
    std::cout << std::endl;

    std::cout << "Pub User: ";
    StringSource(pbUsr, pbUsr.size(), true, new Redirector(encoder));
    std::cout << std::endl;

    SecByteBlock sharedKeyMaster(ecdhMaster.AgreedValueLength());
    SecByteBlock sharedKeyUsr(ecdhUsr.AgreedValueLength());

    // SharedKeyMaster == sharedKeyUsr is a must to ensure same session key is used next steps
    if (!ecdhMaster.Agree(sharedKeyMaster, master_pk_key_sb, pbUsr))
        throw std::runtime_error("Failed to reach shared secret (1)");

    if (!ecdhUsr.Agree(sharedKeyUsr, pkUsr, master_pb_key_sb))
        throw std::runtime_error("Failed to reach shared secret (2)");

    size_t len = std::min(ecdhMaster.AgreedValueLength(), ecdhUsr.AgreedValueLength());
    if (!len || !VerifyBufsEqual(sharedKeyMaster.BytePtr(), sharedKeyUsr.BytePtr(), len))
        throw std::runtime_error("Failed to reach shared secret (3)");

    std::cout << "Shared secret (A): ";
    StringSource(sharedKeyMaster, sharedKeyMaster.size(), true, new Redirector(encoder));
    std::cout << std::endl;

    std::cout << "Shared secret (B): ";
    StringSource(sharedKeyUsr, sharedKeyUsr.size(), true, new Redirector(encoder));
    std::cout << std::endl;

    // AES CBC Encrypt/Decrypt
    SecByteBlock iv(AES::BLOCKSIZE);
    prng.GenerateBlock(iv, iv.size()); // IV needs to be save later if we want decrypt the file later
    std::string plain = "CBC Mode Test";
    std::string cipher, recovered;

    try
    {
        CBC_Mode< AES >::Encryption e;
        e.SetKeyWithIV(sharedKeyUsr, sharedKeyUsr.size(), iv);

        StringSource s(plain, true,
            new StreamTransformationFilter(e,
                new StringSink(cipher)
            )
        );
    }
    catch (const Exception& e)
    {
        std::cerr << e.what() << std::endl;
        exit(1);
    }

    std::cout << "key: ";
    encoder.Put(sharedKeyUsr, sharedKeyUsr.size());
    encoder.MessageEnd();
    std::cout << std::endl;

    std::cout << "iv: ";
    encoder.Put(iv, iv.size());
    encoder.MessageEnd();
    std::cout << std::endl;

    std::cout << "cipher text: ";
    encoder.Put((const byte*)&cipher[0], cipher.size());
    encoder.MessageEnd();
    std::cout << std::endl;

    // AES Decryption
    try
    {
        CBC_Mode< AES >::Decryption d;
        d.SetKeyWithIV(sharedKeyUsr, sharedKeyUsr.size(), iv);

        StringSource s(cipher, true,
            new StreamTransformationFilter(d,
                new StringSink(recovered)
            ) // StreamTransformationFilter
        ); // StringSource

        std::cout << "recovered text: " << recovered << std::endl;
    }
    catch (const Exception& e)
    {
        std::cerr << e.what() << std::endl;
        exit(1);
    }

    return 0;
}

// Some random stuffs
/*
unsigned char* prepanded_session_prv_key = (unsigned char*)malloc(36);
    memset(prepanded_session_prv_key, 0, 36);
    //unsigned char* prepand_bytes = (unsigned char*)malloc(36);
    //memcpy(a, privA, sizeof(privA));

    int j = 4;
    for (int i = 0; i < privA.size(); i++) {
        prepanded_session_prv_key[j] = *(privA + i);
        j++;
        //printf("%x", *(prepanded_session_prv_key + i));
    }

    for (int i = 0; i < PREPENDED_ARY_SIZE; i++) {
        printf("%x", *(prepanded_session_prv_key + i));
    }
    //uint8_t a = (uint8_t)privA;
*/

/*
    const byte privUsrKey[] = { 0x76, 0xde, 0x1, 0x91, 0x1a, 0xe9, 0x64, 0xb5, 0xc6, 0x94, 0xbf, 0x1b, 0x74, 0x30, 0xee, 0x4, 0xa5, 0x5a, 0x5c, 0x71, 0xb6, 0x9b, 0x3, 0xcc, 0x78, 0xa2, 0xa1, 0x48, 0xea, 0x63, 0xb, 0xe5 };
    SecByteBlock privUsr(privUsrKey, 0x20);
    std::cout << "User public key: ";
    StringSource(privUsr, privUsr.size(), true, new Redirector(encoder));
    std::cout << std::endl;
*/