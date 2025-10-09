#include <stdio.h>
#include <openssl/ssl.h>
#include <openssl/err.h>
#include <openssl/evp.h>
#include <openssl/rand.h>

int main() {
    printf("OpenSSL Test Package\n");
    printf("===================\n");
    
    // Test OpenSSL version
    printf("OpenSSL Version: %s\n", OpenSSL_version(OPENSSL_VERSION));
    
    // Test SSL library initialization
    SSL_library_init();
    SSL_load_error_strings();
    OpenSSL_add_all_algorithms();
    
    printf("SSL library initialized successfully\n");
    
    // Test random number generation
    unsigned char random_bytes[16];
    if (RAND_bytes(random_bytes, sizeof(random_bytes)) == 1) {
        printf("Random number generation: OK\n");
    } else {
        printf("Random number generation: FAILED\n");
        return 1;
    }
    
    // Test basic crypto operations
    EVP_MD_CTX *mdctx = EVP_MD_CTX_new();
    if (mdctx != NULL) {
        printf("Crypto context creation: OK\n");
        EVP_MD_CTX_free(mdctx);
    } else {
        printf("Crypto context creation: FAILED\n");
        return 1;
    }
    
    // Cleanup
    EVP_cleanup();
    ERR_free_strings();
    
    printf("\nAll tests passed! OpenSSL package is working correctly.\n");
    return 0;
}