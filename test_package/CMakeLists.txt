cmake_minimum_required(VERSION 3.15)
project(test_openssl)

set(CMAKE_CXX_STANDARD 11)

# Find OpenSSL
find_package(OpenSSL REQUIRED)

# Create test executable
add_executable(test_openssl test_openssl.c)

# Link with OpenSSL
target_link_libraries(test_openssl 
    OpenSSL::SSL 
    OpenSSL::Crypto
)

# Set C standard
set_property(TARGET test_openssl PROPERTY C_STANDARD 99)