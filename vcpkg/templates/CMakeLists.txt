cmake_minimum_required(VERSION 3.20)
project(OpenSSLProject)

# Set vcpkg toolchain file
set(CMAKE_TOOLCHAIN_FILE "${CMAKE_CURRENT_SOURCE_DIR}/vcpkg/scripts/buildsystems/vcpkg.cmake")

# Find OpenSSL
find_package(OpenSSL REQUIRED)

# Add executable
add_executable(${PROJECT_NAME} main.cpp)

# Link with OpenSSL
target_link_libraries(${PROJECT_NAME} 
    PRIVATE 
    OpenSSL::SSL 
    OpenSSL::Crypto
)

# Set C++ standard
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)

# Include directories
target_include_directories(${PROJECT_NAME} PRIVATE ${OPENSSL_INCLUDE_DIR})

# Compile definitions
target_compile_definitions(${PROJECT_NAME} PRIVATE 
    OPENSSL_VERSION_TEXT="${OPENSSL_VERSION_TEXT}"
)

# Print OpenSSL information
message(STATUS "OpenSSL version: ${OPENSSL_VERSION}")
message(STATUS "OpenSSL include dir: ${OPENSSL_INCLUDE_DIR}")
message(STATUS "OpenSSL libraries: ${OPENSSL_LIBRARIES}")