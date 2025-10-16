#include <openssl/ssl.h>
#include <openssl/err.h>
#include <iostream>

int main() {
    std::cout << "🌐 TLS Client Test" << std::endl;
    std::cout << "==================" << std::endl;
    
    // Initialize OpenSSL
    SSL_load_error_strings();
    SSL_library_init();
    
    // Create SSL context
    const SSL_METHOD *method = TLS_client_method();
    SSL_CTX *ctx = SSL_CTX_new(method);
    
    if (!ctx) {
        std::cerr << "❌ Failed to create SSL context" << std::endl;
        ERR_print_errors_fp(stderr);
        return 1;
    }
    
    std::cout << "✅ SSL context created" << std::endl;
    
    // Set minimum TLS version
    SSL_CTX_set_min_proto_version(ctx, TLS1_2_VERSION);
    std::cout << "✅ Minimum TLS version set to 1.2" << std::endl;
    
    // Create SSL object
    SSL *ssl = SSL_new(ctx);
    if (!ssl) {
        std::cerr << "❌ Failed to create SSL object" << std::endl;
        return 1;
    }
    
    std::cout << "✅ SSL object created" << std::endl;
    
    // Cleanup
    SSL_free(ssl);
    SSL_CTX_free(ctx);
    
    std::cout << "\n✅ TLS client test passed!" << std::endl;
    return 0;
}
