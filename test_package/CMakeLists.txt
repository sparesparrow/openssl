cmake_minimum_required(VERSION 3.15)
project(OpenSSLTest CXX)

find_package(OpenSSL REQUIRED)

add_executable(test_openssl test_openssl.cpp)
target_link_libraries(test_openssl OpenSSL::SSL OpenSSL::Crypto)

add_executable(test_tls_client test_tls_client.cpp)
target_link_libraries(test_tls_client OpenSSL::SSL OpenSSL::Crypto)
