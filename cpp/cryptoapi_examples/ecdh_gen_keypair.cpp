// Generate keypair using ecdh xed25519 which will use in "ecdh_aes.cpp" later

// Before compile please:
// VC++ Directory -> Include Directory -> Add crpyto++ folder
// Linker -> Input -> Additional Dpeendencies -> Add fullpath of "cryptlib.lib"
// C/C++ -> Code Generation -> Runtime Library -> Change to "Multi-Threaded (MT)"

#include "cryptlib.h"
#include "xed25519.h"
#include "filters.h"
#include "osrng.h"
#include "files.h"
#include "hex.h"
#include "rijndael.h"

int main(int argc, char* argv[])
{
    using namespace CryptoPP;
    HexEncoder encoder(new FileSink(std::cout));

    AutoSeededRandomPool rnd, prng;
    x25519 ecdh(rnd);
    FileSink fs("private.key.bin"); // This can be ignore
    ecdh.Save(fs);

    SecByteBlock master_priv(ecdh.PrivateKeyLength());
    SecByteBlock master_pub(ecdh.PublicKeyLength());
    ecdh.GenerateKeyPair(rnd, master_priv, master_pub);
    std::cout << "Master Priv: ";
    StringSource(master_priv, master_priv.size(), true, new Redirector(encoder));
    std::cout << std::endl;

    std::cout << "Master Pub: ";
    StringSource(master_pub, master_pub.size(), true, new Redirector(encoder));
    std::cout << std::endl;

    // Save generated key pair
    std::ofstream pk_fout;
    pk_fout.open("master_pk.bin", std::ios::binary | std::ios::out);
    pk_fout.write((char*)&*(master_priv), master_priv.size());
    pk_fout.close();

    std::ofstream pb_fout;
    pb_fout.open("master_pb.bin", std::ios::binary | std::ios::out);
    pb_fout.write((char*)&*(master_pub), master_pub.size());
    pb_fout.close();

    std::ifstream pk_fin("master_pk.bin", std::ios::binary);
    std::vector<unsigned char> master_pk_loaded(std::istreambuf_iterator<char>(pk_fin), {});
    pk_fin.close();

    std::ifstream pb_fin("master_pb.bin", std::ios::binary);
    std::vector<unsigned char> master_pb_loaded(std::istreambuf_iterator<char>(pb_fin), {});
    pb_fin.close();

    for (int i = 0; i < 0x20; i++) {
        printf("%X", master_pk_loaded[i]);
    }
    printf("\n");
    for (int i = 0; i < 0x20; i++) {
        printf("%X", master_pb_loaded[i]);
    }

    // Note: unsigned char alias with byte
    SecByteBlock master_pk_key_sb(reinterpret_cast<const unsigned char*>(master_pk_loaded.data()), 0x20);
    std::cout << "Priv (A): ";
    StringSource(master_pk_key_sb, master_pk_key_sb.size(), true, new Redirector(encoder));
    std::cout << std::endl;
    
    return 0;
}