# Conan profile for CI macOS ARM64 (Apple Silicon) builds

[settings]
os=Macos
arch=armv8
compiler=apple-clang
compiler.version=${APPLE_CLANG_VERSION}
compiler.libcxx=libc++
build_type=Release

[options]
# OpenSSL specific options for macOS ARM64 CI
openssl/*:shared=True
openssl/*:fips=True
openssl/*:enable_quic=True
openssl/*:enable_lms=True
openssl/*:enable_demos=True
openssl/*:enable_h3demo=True
openssl/*:enable_unit_test=True

[buildenv]
# macOS ARM64 environment
CC=${CC}
CXX=${CXX}
CFLAGS=${CFLAGS:- -O2 -g}
CXXFLAGS=${CXXFLAGS:- -O2 -g}

# OpenSSL CI specific
OSSL_RUN_CI_TESTS=1
HARNESS_JOBS=${HARNESS_JOBS:-4}
MACOSX_DEPLOYMENT_TARGET=${MACOSX_DEPLOYMENT_TARGET:-13.0}
SDKROOT=${SDKROOT}
DEVELOPER_DIR=${DEVELOPER_DIR}

[conf]
tools.system.package_manager:mode=install
tools.env:CONAN_CPU_COUNT=${CONAN_CPU_COUNT}
tools.build:jobs=${CONAN_CPU_COUNT}
