# Slight modification from https://hshrzd.wordpress.com/2019/09/30/flare-on-6-tasks-10-12/
#include <iostream>
#include <Windows.h>
#include <iostream>
#include <cstdlib>
#include <cstdio>
#include <ctime>

void decipher(DWORD *v, BYTE *k) {
    unsigned int num_rounds = 32;
    unsigned int i;
    DWORD v0 = v[0];
    DWORD v1 = v[1];
    DWORD delta = -0x61c88647;
    DWORD sum = delta * num_rounds;

    for (i = 0; i < num_rounds; i++) {
        v1 -= (((v0 << 4) ^ (v0 >> 5)) + v0) ^ (sum + k[(sum >> 11) & 3]);
        sum -= delta;
        v0 -= (((v1 << 4) ^ (v1 >> 5)) + v1) ^ (sum + k[sum & 3]);
    }

    v[0] = v0; v[1] = v1;
}

bool dump_to_file(char* of, BYTE* buf, size_t fsize) {
    FILE* f2 = fopen(of, "wb");
    if (!f2) {
        std::cout << "Error" << std::endl;
        return false;
    }
    fwrite(buf, 1, fsize, f2);
    fclose(f2);
    std::cout << "Saved output to: " << of << std::endl;
    return true;
}

bool test_key(BYTE* buf, BYTE* key) {
    const size_t chunk_size = 8;
    BYTE chunk[chunk_size] = { 0 };
    memcpy(chunk, buf, chunk_size);
    
    decipher((DWORD*)((ULONG_PTR)chunk), key);
    
    unsigned char check_gif[4] = {
        0x47, 0x49, 0x46, 0x38
    };

    if (memcmp(chunk, check_gif, sizeof(check_gif)) == 0) {
        return true;
    }
    return false;
}

bool brute_key(BYTE *buf, BYTE *key) {

    key[0] = 0x31;
    for (uint8_t  i = 0; i < 0xff; i++) {
        for (uint8_t j = 0; j < 0xff; j++) {
            for (uint8_t k = 0; k < 0xff; k++) {
                key[1] = j;
                key[2] = k;
                key[3] = 0xb1;
                printf("%x,%x,%x,%x\n", key[0], key[1], key[2], key[3]);

                if (test_key(buf, key)) {
                    printf("Found: %x,%x,%x,%x\n", key[0], key[1], key[2], key[3]);
                    return true;
                }
            }
        }
    }

    return false;
}

int main(int argc, char *argv[])
{
    if (argc < 2) 
    {
        std::cout << ("Input file?") << std::endl;
        return 1;
    }
    std::cout << "sad" << std::endl;

    char *filename = argv[1];
    FILE *f = fopen(filename, "rb");
    if (!f) {
        std::cout << "Cant read the file" << std::endl;
        return 1;
    }

    fseek(f, 0, SEEK_END);
    size_t fsize = ftell(f);
    fseek(f, 0, SEEK_SET);
    BYTE *buf = (BYTE*)calloc(fsize, 1);
    if (!buf) {
        return 1;
    }
    fread(buf, 1, fsize, f);
    fclose(f);
    f = NULL;

    const size_t key_len = 4;
    BYTE key[key_len] = { 0 };
    
    brute_key(buf, key);
    BYTE *chunk = buf;
    for (size_t i = 0; i < (fsize / 8); i++) {
        decipher((DWORD*)((ULONG_PTR)chunk), (BYTE*)key);
        chunk += 8;
    }
    char of[] = "lala.gif";
    dump_to_file(of, buf, fsize);
    return 0;
}
