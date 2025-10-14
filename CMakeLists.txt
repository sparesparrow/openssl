cmake_minimum_required(VERSION 3.22)
project(OpenSSL-FIPS-DDD VERSION 3.3.0 LANGUAGES C ASM)

# Set C standard for OpenSSL compatibility
set(CMAKE_C_STANDARD 99)
set(CMAKE_C_STANDARD_REQUIRED ON)

# OpenSSL-specific options
option(OPENSSL_FIPS "Enable FIPS 140-3 compliance" ON)
option(ENABLE_FIPS_MODULE "Build FIPS provider module" ON)
option(ENABLE_SHARED "Build shared libraries" ON)
option(ENABLE_STATIC "Build static libraries" ON)
option(DISABLE_NON_FIPS_ALGORITHMS "Disable non-FIPS approved algorithms" OFF)
option(BUILD_TESTING "Build test suite" ON)
option(ENABLE_EXAMPLES "Build example programs" OFF)
option(ENABLE_DOCS "Build documentation" OFF)

# DDD Layered Architecture Setup
set(CRYPTO_DOMAIN_DIR "${CMAKE_CURRENT_SOURCE_DIR}/crypto")
set(SSL_APPLICATION_DIR "${CMAKE_CURRENT_SOURCE_DIR}/ssl")
set(PROVIDERS_INFRASTRUCTURE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/providers")
set(APPS_PRESENTATION_DIR "${CMAKE_CURRENT_SOURCE_DIR}/apps")
set(TEST_LAYER_DIR "${CMAKE_CURRENT_SOURCE_DIR}/test")

# Conan toolchain support
if(EXISTS "${CMAKE_BINARY_DIR}/conan_toolchain.cmake")
    include("${CMAKE_BINARY_DIR}/conan_toolchain.cmake")
endif()

# FIPS-specific compiler flags
if(OPENSSL_FIPS)
    add_compile_definitions(OPENSSL_FIPS)
    if(DISABLE_NON_FIPS_ALGORITHMS)
        add_compile_definitions(OPENSSL_NO_DEPRECATED)
    endif()
endif()

# Global include directories (DDD Domain Layer interfaces)
include_directories(
    ${CMAKE_CURRENT_SOURCE_DIR}/include
    ${CMAKE_CURRENT_BINARY_DIR}/include
)

# ============================================================================
# DOMAIN LAYER: Core Crypto Primitives
# ============================================================================

# Collect crypto domain sources (FIPS-approved algorithms)
file(GLOB_RECURSE CRYPTO_SOURCES
    "${CRYPTO_DOMAIN_DIR}/*.c"
    "${CRYPTO_DOMAIN_DIR}/*.S"
)

# Create crypto domain library
add_library(openssl-crypto ${CRYPTO_SOURCES})
target_include_directories(openssl-crypto PRIVATE
    ${CRYPTO_DOMAIN_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/include/crypto
)

if(ENABLE_SHARED)
    set_target_properties(openssl-crypto PROPERTIES
        VERSION ${PROJECT_VERSION}
        SOVERSION ${PROJECT_VERSION_MAJOR}
    )
endif()

# ============================================================================
# APPLICATION LAYER: SSL/TLS Protocol Orchestration
# ============================================================================

# Collect SSL/TLS application sources
file(GLOB_RECURSE SSL_SOURCES "${SSL_APPLICATION_DIR}/*.c")

# Create SSL application library
add_library(openssl-ssl ${SSL_SOURCES})
target_include_directories(openssl-ssl PRIVATE
    ${SSL_APPLICATION_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/include/openssl
)
target_link_libraries(openssl-ssl PUBLIC openssl-crypto)

# ============================================================================
# INFRASTRUCTURE LAYER: Providers and External Services
# ============================================================================

# FIPS Provider (Infrastructure Layer)
if(ENABLE_FIPS_MODULE)
    file(GLOB_RECURSE FIPS_SOURCES "${PROVIDERS_INFRASTRUCTURE_DIR}/fips/*.c")

    add_library(fips-module ${FIPS_SOURCES})
    target_include_directories(fips-module PRIVATE
        ${PROVIDERS_INFRASTRUCTURE_DIR}/fips
        ${CMAKE_CURRENT_SOURCE_DIR}/include/openssl
    )
    target_link_libraries(fips-module PUBLIC openssl-crypto)

    # FIPS self-tests
    file(GLOB_RECURSE FIPS_TEST_SOURCES "${PROVIDERS_INFRASTRUCTURE_DIR}/fips/test/*.c")
    add_executable(fips_test ${FIPS_TEST_SOURCES})
    target_link_libraries(fips_test fips-module openssl-crypto)
endif()

# ============================================================================
# PRESENTATION LAYER: CLI/API Interfaces
# ============================================================================

# OpenSSL CLI application
file(GLOB_RECURSE APPS_SOURCES "${APPS_PRESENTATION_DIR}/*.c")

add_executable(openssl ${APPS_SOURCES})
target_include_directories(openssl PRIVATE
    ${APPS_PRESENTATION_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/include/openssl
)
target_link_libraries(openssl openssl-ssl openssl-crypto)

# ============================================================================
# TESTING LAYER: FIPS Validation and Unit Tests
# ============================================================================

if(BUILD_TESTING)
    enable_testing()

    # FIPS self-tests (part of FIPS module validation)
    if(ENABLE_FIPS_MODULE)
        add_test(NAME fips-self-test
            COMMAND fips_test
            WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
        )
    endif()

    # Crypto algorithm tests
    file(GLOB_RECURSE CRYPTO_TEST_SOURCES "${TEST_LAYER_DIR}/*.c")
    foreach(TEST_SOURCE ${CRYPTO_TEST_SOURCES})
        get_filename_component(TEST_NAME ${TEST_SOURCE} NAME_WE)
        add_executable(${TEST_NAME} ${TEST_SOURCE})
        target_link_libraries(${TEST_NAME} openssl-crypto)
        add_test(NAME ${TEST_NAME}
            COMMAND ${TEST_NAME}
            WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
        )
    endforeach()
endif()

# ============================================================================
# INSTALLATION AND PACKAGING
# ============================================================================

# Install libraries
if(ENABLE_SHARED)
    install(TARGETS openssl-crypto openssl-ssl
        LIBRARY DESTINATION lib
        ARCHIVE DESTINATION lib
        RUNTIME DESTINATION bin
    )
endif()

if(ENABLE_STATIC)
    install(TARGETS openssl-crypto openssl-ssl
        LIBRARY DESTINATION lib
        ARCHIVE DESTINATION lib
    )
endif()

# Install FIPS module
if(ENABLE_FIPS_MODULE)
    install(TARGETS fips-module
        LIBRARY DESTINATION lib/ossl-modules
        ARCHIVE DESTINATION lib
    )
endif()

# Install CLI application
install(TARGETS openssl
    RUNTIME DESTINATION bin
)

# Install headers (layered structure)
install(DIRECTORY include/ DESTINATION include)

# ============================================================================
# DOCUMENTATION
# ============================================================================

if(ENABLE_DOCS)
    find_package(Doxygen)
    if(DOXYGEN_FOUND)
        set(DOXYGEN_PROJECT_NAME "OpenSSL FIPS DDD")
        set(DOXYGEN_PROJECT_BRIEF "FIPS 140-3 compliant OpenSSL with DDD layered architecture")
        set(DOXYGEN_INPUT_DIR "${CMAKE_CURRENT_SOURCE_DIR}/include ${CMAKE_CURRENT_SOURCE_DIR}/crypto ${CMAKE_CURRENT_SOURCE_DIR}/ssl")
        set(DOXYGEN_OUTPUT_DIR "${CMAKE_CURRENT_BINARY_DIR}/docs")
        set(DOXYGEN_RECURSIVE YES)
        set(DOXYGEN_EXTRACT_ALL YES)

        doxygen_add_docs(openssl-docs
            ${CMAKE_CURRENT_SOURCE_DIR}/include
            ${CMAKE_CURRENT_SOURCE_DIR}/crypto
            ${CMAKE_CURRENT_SOURCE_DIR}/ssl
            COMMENT "Generate OpenSSL API documentation"
        )
    endif()
endif()

# ============================================================================
# EXAMPLES
# ============================================================================

if(ENABLE_EXAMPLES)
    add_subdirectory(demos)
endif()

# ============================================================================
# CMAKE PACKAGE CONFIGURATION
# ============================================================================

include(CMakePackageConfigHelpers)

# Generate version file
write_basic_package_version_file(
    "${CMAKE_CURRENT_BINARY_DIR}/OpenSSLConfigVersion.cmake"
    VERSION ${PROJECT_VERSION}
    COMPATIBILITY SameMajorVersion
)

# Generate config file
configure_package_config_file(
    "${CMAKE_CURRENT_SOURCE_DIR}/cmake/OpenSSLConfig.cmake.in"
    "${CMAKE_CURRENT_BINARY_DIR}/OpenSSLConfig.cmake"
    INSTALL_DESTINATION lib/cmake/OpenSSL
    PATH_VARS
        INCLUDE_INSTALL_DIR
)

# Install config files
install(FILES
    "${CMAKE_CURRENT_BINARY_DIR}/OpenSSLConfig.cmake"
    "${CMAKE_CURRENT_BINARY_DIR}/OpenSSLConfigVersion.cmake"
    DESTINATION lib/cmake/OpenSSL
)

# ============================================================================
# SUMMARY
# ============================================================================

message(STATUS "OpenSSL FIPS DDD Configuration:")
message(STATUS "  FIPS Mode: ${OPENSSL_FIPS}")
message(STATUS "  FIPS Module: ${ENABLE_FIPS_MODULE}")
message(STATUS "  Shared Libraries: ${ENABLE_SHARED}")
message(STATUS "  Static Libraries: ${ENABLE_STATIC}")
message(STATUS "  Non-FIPS Algorithms: ${DISABLE_NON_FIPS_ALGORITHMS}")
message(STATUS "  Testing: ${BUILD_TESTING}")
message(STATUS "  Examples: ${ENABLE_EXAMPLES}")
message(STATUS "  Documentation: ${ENABLE_DOCS}")