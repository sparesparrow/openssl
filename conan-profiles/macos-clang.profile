[settings]
os=Macos
arch=x86_64
compiler=clang
compiler.version=14
compiler.libcxx=libc++
build_type=Release

[options]
openssl:shared=True
openssl:fips=False
openssl:no_asm=False
openssl:no_threads=False

[conf]
tools.system.package_manager:mode=install