[settings]
os=Linux
arch=x86_64
compiler=gcc
compiler.version=11
compiler.libcxx=libstdc++11
build_type=Release

[options]
openssl:shared=True
openssl:fips=False
openssl:no_asm=False
openssl:no_threads=False

[conf]
tools.system.package_manager:mode=install
tools.system.package_manager:sudo=True