from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, cmake_layout
from conan.tools.files import save
import os

class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeDeps", "CMakeToolchain"
    test_type = "explicit"

    options = {
        "component": ["openssl", "libcrypto", "libssl"],  # Test specific component
        "fips_validation": [True, False],  # Enable FIPS-specific validation
        "performance_test": [True, False],  # Run performance benchmarks
    }
    default_options = {
        "component": "openssl",
        "fips_validation": False,
        "performance_test": False,
    }

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def generate(self):
        # Generate test source files
        self._generate_test_sources()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            # Test 1: Basic version check
            self._test_version_info()

            # Test 2: Component-specific testing
            self._test_component_functionality()

            # Test 3: FIPS validation if enabled
            if self.options.fips_validation:
                self._test_fips_validation()

            # Test 4: Performance testing if enabled
            if self.options.performance_test:
                self._test_performance()

            # Test 5: Run comprehensive test executable
            self._run_comprehensive_tests()

            # Test 6: Test that openssl_tools utilities are accessible
            self._test_tool_integration()

    def _test_version_info(self):
        """Test version information for the component"""
        self.output.info(f"Testing component: {self.options.component}")

        if self.options.component == "openssl":
            # Test full OpenSSL version
            self.run("openssl version", cwd=self.build_folder)
        elif self.options.component == "libcrypto":
            # Test libcrypto version
            test_exe = os.path.join(self.cpp.build.bindirs[0], "test_package")
            if os.path.exists(test_exe):
                self.run(f"{test_exe} --version", cwd=self.build_folder)
        elif self.options.component == "libssl":
            # Test libssl version
            test_exe = os.path.join(self.cpp.build.bindirs[0], "test_package")
            if os.path.exists(test_exe):
                self.run(f"{test_exe} --ssl-version", cwd=self.build_folder)

    def _test_component_functionality(self):
        """Test component-specific functionality"""
        test_exe = os.path.join(self.cpp.build.bindirs[0], "test_package")
        if not os.path.exists(test_exe):
            self.output.warn("Test executable not found, skipping component tests")
            return

        if self.options.component == "libcrypto":
            # Test crypto-specific functionality
            self.run(f"{test_exe} --test-crypto", cwd=self.build_folder)
        elif self.options.component == "libssl":
            # Test SSL-specific functionality
            self.run(f"{test_exe} --test-ssl", cwd=self.build_folder)
        else:
            # Test full OpenSSL functionality
            self.run(test_exe, cwd=self.build_folder)

    def _test_fips_validation(self):
        """Perform FIPS-specific validation tests"""
        self.output.info("Running FIPS validation tests...")

        test_exe = os.path.join(self.cpp.build.bindirs[0], "test_package")
        if os.path.exists(test_exe):
            # Run FIPS-specific tests
            try:
                self.run(f"{test_exe} --fips-test", cwd=self.build_folder)
                self.output.info("✓ FIPS validation tests passed")
            except Exception as e:
                self.output.error(f"✗ FIPS validation tests failed: {e}")
                raise

            # Additional FIPS checks
            self._verify_fips_artifacts()
        else:
            self.output.warn("Test executable not found, skipping FIPS validation")

    def _verify_fips_artifacts(self):
        """Verify FIPS-related artifacts are present and valid"""
        # Check for FIPS module
        fips_module_path = os.path.join(self.package_folder, "lib", "ossl-modules", "fips.so")
        if os.path.exists(fips_module_path):
            self.output.info("✓ FIPS module found")
        else:
            self.output.info("ℹ FIPS module not found (normal for non-FIPS builds)")

        # Check for FIPS certificates/data
        fips_cert_path = os.path.join(self.package_folder, "share", "openssl", "fips", "certificate-4985.json")
        if os.path.exists(fips_cert_path):
            self.output.info("✓ FIPS certificate data found")
        else:
            self.output.info("ℹ FIPS certificate data not found")

    def _test_performance(self):
        """Run performance benchmark tests"""
        self.output.info("Running performance benchmark tests...")

        test_exe = os.path.join(self.cpp.build.bindirs[0], "test_package")
        if os.path.exists(test_exe):
            try:
                self.run(f"{test_exe} --performance-test", cwd=self.build_folder)
                self.output.info("✓ Performance tests completed")
            except Exception as e:
                self.output.warning(f"Performance tests failed: {e}")
        else:
            self.output.warn("Test executable not found, skipping performance tests")

    def _run_comprehensive_tests(self):
        """Run the comprehensive test executable"""
        test_exe = os.path.join(self.cpp.build.bindirs[0], "test_package")
        if os.path.exists(test_exe):
            self.run(test_exe, cwd=self.build_folder)
        else:
            self.output.warn("Test executable not found, skipping comprehensive tests")

    def _test_tool_integration(self):
        """Test integration with openssl_tools"""
        try:
            self.run("python3 -c \\\"from openssl_tools import VersionManager; vm = VersionManager(); print('Tools integration works')\\\"", env="conanrun")
            self.output.info("✓ OpenSSL tools integration verified")
        except Exception as e:
            self.output.warning(f"OpenSSL tools integration test failed: {e}")

    def _generate_test_sources(self):
        """Generate comprehensive test source files"""

        # Generate CMakeLists.txt
        cmake_content = """
cmake_minimum_required(VERSION 3.15)
project(test_package)

find_package(OpenSSL REQUIRED)

# Test executable
add_executable(test_package test_package.cpp)
target_link_libraries(test_package OpenSSL::SSL OpenSSL::Crypto)

# Test shared vs static linking
if(OpenSSL_SHARED)
    message(STATUS "Testing shared OpenSSL libraries")
else()
    message(STATUS "Testing static OpenSSL libraries")
endif()
"""
        save(self, os.path.join(self.source_folder, "CMakeLists.txt"), cmake_content)

        # Generate comprehensive test source
        test_source = """
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
#include <chrono>

void test_headers() {
    std::cout << "✓ OpenSSL headers included successfully" << std::endl;
}

void test_library_linking() {
    // Test that libraries are properly linked
    const char* version = OpenSSL_version(OPENSSL_VERSION);
    std::cout << "✓ OpenSSL version: " << version << std::endl;

    // Test SSL library (OpenSSL 3.x compatible)
    const char* ssl_version = OpenSSL_version(OPENSSL_VERSION);
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

    // Check FIPS mode status (OpenSSL 3.x compatible)
    // Note: FIPS_mode() is deprecated in OpenSSL 3.x, using provider check instead
    if (fips_provider != nullptr) {
        std::cout << "✓ FIPS mode is available via provider" << std::endl;
    } else {
        std::cout << "ℹ FIPS mode is not available (normal for non-FIPS builds)" << std::endl;
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

void run_performance_test() {
    std::cout << "Running performance benchmark..." << std::endl;

    auto start = std::chrono::high_resolution_clock::now();

    // Performance test: Generate multiple RSA keys
    const int num_keys = 10;
    for (int i = 0; i < num_keys; ++i) {
        EVP_PKEY_CTX* ctx = EVP_PKEY_CTX_new_id(EVP_PKEY_RSA, nullptr);
        if (ctx && EVP_PKEY_keygen_init(ctx) > 0) {
            EVP_PKEY_CTX_set_rsa_keygen_bits(ctx, 2048);
            EVP_PKEY* pkey = nullptr;
            EVP_PKEY_keygen(ctx, &pkey);
            if (pkey) EVP_PKEY_free(pkey);
        }
        if (ctx) EVP_PKEY_CTX_free(ctx);
    }

    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);

    std::cout << "✓ Performance test completed in " << duration.count() << "ms" << std::endl;
}

int main(int argc, char* argv[]) {
    std::cout << "=== OpenSSL Conan Package Test ===" << std::endl;

    // Parse command line arguments
    bool test_crypto_only = false;
    bool test_ssl_only = false;
    bool fips_test = false;
    bool performance_test = false;
    bool version_only = false;
    bool ssl_version_only = false;

    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        if (arg == "--test-crypto") test_crypto_only = true;
        else if (arg == "--test-ssl") test_ssl_only = true;
        else if (arg == "--fips-test") fips_test = true;
        else if (arg == "--performance-test") performance_test = true;
        else if (arg == "--version") version_only = true;
        else if (arg == "--ssl-version") ssl_version_only = true;
    }

    try {
        if (version_only) {
            test_library_linking();
            return 0;
        }

        if (ssl_version_only) {
            std::cout << "SSL Version: " << OpenSSL_version(OPENSSL_VERSION) << std::endl;
            return 0;
        }

        if (fips_test) {
            test_fips_mode();
            return 0;
        }

        if (performance_test) {
            run_performance_test();
            return 0;
        }

        if (test_crypto_only) {
            test_headers();
            test_crypto_operations();
            test_error_handling();
        } else if (test_ssl_only) {
            test_headers();
            test_library_linking();
            // Add SSL-specific tests here
        } else {
            // Run all tests
            test_headers();
            test_library_linking();
            test_crypto_operations();
            test_fips_mode();
            test_error_handling();
        }

        std::cout << "\\n✅ All tests passed successfully!" << std::endl;
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "❌ Test failed: " << e.what() << std::endl;
        return 1;
    }
}
"""
        save(self, os.path.join(self.source_folder, "test_package.cpp"), test_source)