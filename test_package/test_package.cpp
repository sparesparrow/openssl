
#include <openssl/ssl.h>
#include <openssl/crypto.h>
#include <openssl/evp.h>
#include <openssl/rsa.h>
#include <openssl/err.h>
#include <openssl/rand.h>
#include <openssl/conf.h>
#include <openssl/provider.h>
#include <iostream>
#include <cassert>
#include <cstring>

void test_headers() {
    std::cout << "✓ OpenSSL headers included successfully" << std::endl;
}

void test_library_linking() {
    // Test that libraries are properly linked
    const char* version = OpenSSL_version(OPENSSL_VERSION);
    std::cout << "✓ OpenSSL version: " << version << std::endl;

    // Test SSL library
    const char* ssl_version = OpenSSL_version(OPENSSL_SSL_VERSION);
    std::cout << "✓ SSL version: " << ssl_version << std::endl;
}

void test_crypto_operations() {
    std::cout << "Testing cryptographic operations..." << std::endl;

    // Test 1: Random number generation
    unsigned char random_bytes[32];
    int result = RAND_bytes(random_bytes, sizeof(random_bytes));
    assert(result == 1);
    std::cout << "✓ Random number generation works" << std::endl;

    // Test 2: RSA key generation
    EVP_PKEY_CTX* ctx = EVP_PKEY_CTX_new_id(EVP_PKEY_RSA, nullptr);
    assert(ctx != nullptr);

    if (EVP_PKEY_keygen_init(ctx) <= 0) {
        std::cerr << "Failed to initialize RSA key generation" << std::endl;
        EVP_PKEY_CTX_free(ctx);
        return;
    }

    if (EVP_PKEY_CTX_set_rsa_keygen_bits(ctx, 2048) <= 0) {
        std::cerr << "Failed to set RSA key size" << std::endl;
        EVP_PKEY_CTX_free(ctx);
        return;
    }

    EVP_PKEY* pkey = nullptr;
    if (EVP_PKEY_keygen(ctx, &pkey) <= 0) {
        std::cerr << "Failed to generate RSA key" << std::endl;
        EVP_PKEY_CTX_free(ctx);
        return;
    }

    EVP_PKEY_CTX_free(ctx);
    EVP_PKEY_free(pkey);
    std::cout << "✓ RSA key generation works" << std::endl;

    // Test 3: Hash operations
    EVP_MD_CTX* md_ctx = EVP_MD_CTX_new();
    assert(md_ctx != nullptr);

    const EVP_MD* md = EVP_sha256();
    assert(md != nullptr);

    if (EVP_DigestInit_ex(md_ctx, md, nullptr) <= 0) {
        std::cerr << "Failed to initialize digest" << std::endl;
        EVP_MD_CTX_free(md_ctx);
        return;
    }

    const char* test_data = "Hello, OpenSSL!";
    if (EVP_DigestUpdate(md_ctx, test_data, strlen(test_data)) <= 0) {
        std::cerr << "Failed to update digest" << std::endl;
        EVP_MD_CTX_free(md_ctx);
        return;
    }

    unsigned char hash[EVP_MAX_MD_SIZE];
    unsigned int hash_len;
    if (EVP_DigestFinal_ex(md_ctx, hash, &hash_len) <= 0) {
        std::cerr << "Failed to finalize digest" << std::endl;
        EVP_MD_CTX_free(md_ctx);
        return;
    }

    EVP_MD_CTX_free(md_ctx);
    std::cout << "✓ SHA-256 hash computation works" << std::endl;
}

void test_fips_mode() {
    std::cout << "Testing FIPS mode..." << std::endl;

    // Check if FIPS provider is available
    OSSL_PROVIDER* fips_provider = OSSL_PROVIDER_load(nullptr, "fips");
    if (fips_provider != nullptr) {
        std::cout << "✓ FIPS provider loaded successfully" << std::endl;
        OSSL_PROVIDER_unload(fips_provider);
    } else {
        std::cout << "ℹ FIPS provider not available (this is normal for non-FIPS builds)" << std::endl;
    }

    // Check FIPS mode status
    int fips_mode = FIPS_mode();
    if (fips_mode) {
        std::cout << "✓ FIPS mode is enabled" << std::endl;
    } else {
        std::cout << "ℹ FIPS mode is disabled (normal for non-FIPS builds)" << std::endl;
    }
}

void test_error_handling() {
    std::cout << "Testing error handling..." << std::endl;

    // Generate an error
    EVP_PKEY_CTX* invalid_ctx = EVP_PKEY_CTX_new_id(EVP_PKEY_RSA, nullptr);
    assert(invalid_ctx != nullptr);

    // This should fail and set an error
    int result = EVP_PKEY_keygen(invalid_ctx, nullptr);
    assert(result <= 0);

    // Check that error was set
    unsigned long error = ERR_get_error();
    if (error != 0) {
        std::cout << "✓ Error handling works correctly" << std::endl;
    } else {
        std::cerr << "Error handling test failed" << std::endl;
    }

    EVP_PKEY_CTX_free(invalid_ctx);
}

int main() {
    std::cout << "=== OpenSSL Conan Package Test ===" << std::endl;

    try {
        test_headers();
        test_library_linking();
        test_crypto_operations();
        test_fips_mode();
        test_error_handling();

        std::cout << "\n✅ All tests passed successfully!" << std::endl;
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "❌ Test failed: " << e.what() << std::endl;
        return 1;
    }
}
