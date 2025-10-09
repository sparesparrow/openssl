[settings]
os=Linux
arch=x86_64
compiler=gcc
compiler.version=11
compiler.libcxx=libstdc++11
build_type=Release

[options]
openssl/*:shared=True
openssl/*:fips=False
openssl/*:enable_quic=True

[conf]
tools.system.package_manager:mode=install
tools.system.package_manager:sudo=True
tools.env:CONAN_CPU_COUNT=4

[buildenv]
# Basic build environment
CC=gcc
CXX=g++