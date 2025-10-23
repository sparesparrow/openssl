
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
