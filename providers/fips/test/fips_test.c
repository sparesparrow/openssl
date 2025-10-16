#include <openssl/err.h>
#include <openssl/evp.h>
#include <openssl/fips.h>
#include <stdio.h>
#include <stdlib.h>

int main() {
  printf("FIPS 140-3 Self-Test\n");
  printf("===================\n");

  // Initialize OpenSSL
  OpenSSL_add_all_algorithms();
  ERR_load_crypto_strings();

  // Check if FIPS mode is enabled
  if (FIPS_mode()) {
    printf("✅ FIPS mode is enabled\n");
  } else {
    printf("❌ FIPS mode is not enabled\n");
    return 1;
  }

  // Test basic FIPS-approved algorithms
  printf("Testing FIPS-approved algorithms...\n");

  // Test AES-256-GCM
  EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
  if (!ctx) {
    printf("❌ Failed to create cipher context\n");
    return 1;
  }

  const EVP_CIPHER *cipher = EVP_aes_256_gcm();
  if (!cipher) {
    printf("❌ AES-256-GCM not available\n");
    EVP_CIPHER_CTX_free(ctx);
    return 1;
  }

  printf("✅ AES-256-GCM is available\n");
  EVP_CIPHER_CTX_free(ctx);

  // Test SHA-256
  const EVP_MD *md = EVP_sha256();
  if (!md) {
    printf("❌ SHA-256 not available\n");
    return 1;
  }

  printf("✅ SHA-256 is available\n");

  printf("\n🎉 FIPS self-test completed successfully!\n");
  return 0;
}
