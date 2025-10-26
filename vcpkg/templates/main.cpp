#include <iostream>
#include <openssl/ssl.h>
#include <openssl/evp.h>
#include <openssl/err.h>

int main() {
    std::cout << "OpenSSL vcpkg Integration Test" << std::endl;
    std::cout << "==============================" << std::endl;
    
    // Initialize OpenSSL
    SSL_library_init();
    OpenSSL_add_all_algorithms();
    SSL_load_error_strings();
    
    // Print OpenSSL version
    std::cout << "OpenSSL version: " << OpenSSL_version(OPENSSL_VERSION) << std::endl;
    std::cout << "OpenSSL version text: " << OPENSSL_VERSION_TEXT << std::endl;
    
    // Test basic functionality
    EVP_MD_CTX* mdctx = EVP_MD_CTX_new();
    if (mdctx == nullptr) {
        std::cerr << "Failed to create EVP_MD_CTX" << std::endl;
        return 1;
    }
    
    const EVP_MD* md = EVP_sha256();
    if (EVP_DigestInit_ex(mdctx, md, nullptr) != 1) {
        std::cerr << "Failed to initialize digest" << std::endl;
        EVP_MD_CTX_free(mdctx);
        return 1;
    }
    
    // Test data
    const char* test_data = "Hello, OpenSSL with vcpkg!";
    if (EVP_DigestUpdate(mdctx, test_data, strlen(test_data)) != 1) {
        std::cerr << "Failed to update digest" << std::endl;
        EVP_MD_CTX_free(mdctx);
        return 1;
    }
    
    unsigned char hash[EVP_MAX_MD_SIZE];
    unsigned int hash_len;
    if (EVP_DigestFinal_ex(mdctx, hash, &hash_len) != 1) {
        std::cerr << "Failed to finalize digest" << std::endl;
        EVP_MD_CTX_free(mdctx);
        return 1;
    }
    
    std::cout << "SHA256 hash of '" << test_data << "': ";
    for (unsigned int i = 0; i < hash_len; i++) {
        printf("%02x", hash[i]);
    }
    std::cout << std::endl;
    
    // Cleanup
    EVP_MD_CTX_free(mdctx);
    EVP_cleanup();
    ERR_free_strings();
    
    std::cout << "✅ OpenSSL vcpkg integration test completed successfully!" << std::endl;
    return 0;
}