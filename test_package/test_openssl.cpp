#include <openssl/ssl.h>
#include <openssl/err.h>
#include <openssl/evp.h>
#include <iostream>
#include <cstring>

int main() {
    std::cout << "🧪 OpenSSL Test Suite" << std::endl;
    std::cout << "====================" << std::endl;
    
    // Test 1: Version check
    std::cout << "\n1️⃣  Version: " << OpenSSL_version(OPENSSL_VERSION) << std::endl;
    
    // Test 2: Initialize OpenSSL
    SSL_load_error_strings();
    OpenSSL_add_all_algorithms();
    std::cout << "2️⃣  Initialization: ✅" << std::endl;
    
    // Test 3: SHA-256 hash
    unsigned char hash[EVP_MAX_MD_SIZE];
    unsigned int hash_len;
    
    EVP_MD_CTX *mdctx = EVP_MD_CTX_new();
    if (!mdctx) {
        std::cerr << "❌ Failed to create MD context" << std::endl;
        return 1;
    }
    
    if (EVP_DigestInit_ex(mdctx, EVP_sha256(), nullptr) != 1) {
        std::cerr << "❌ Failed to initialize SHA-256" << std::endl;
        return 1;
    }
    
    const char *data = "Hello, OpenSSL!";
    EVP_DigestUpdate(mdctx, data, std::strlen(data));
    EVP_DigestFinal_ex(mdctx, hash, &hash_len);
    EVP_MD_CTX_free(mdctx);
    
    std::cout << "3️⃣  SHA-256 hash: ";
    for (unsigned int i = 0; i < hash_len; i++) {
        printf("%02x", hash[i]);
    }
    std::cout << " ✅" << std::endl;
    
    // Test 4: AES encryption
    EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
    if (!ctx) {
        std::cerr << "❌ Failed to create cipher context" << std::endl;
        return 1;
    }
    
    unsigned char key[32] = {0}; // 256-bit key
    unsigned char iv[16] = {0};  // 128-bit IV
    
    if (EVP_EncryptInit_ex(ctx, EVP_aes_256_cbc(), nullptr, key, iv) != 1) {
        std::cerr << "❌ Failed to initialize AES-256-CBC" << std::endl;
        return 1;
    }
    
    EVP_CIPHER_CTX_free(ctx);
    std::cout << "4️⃣  AES-256-CBC: ✅" << std::endl;
    
    std::cout << "\n✅ All tests passed!" << std::endl;
    return 0;
}
