[settings]
os=Windows
arch=x86_64
compiler=msvc
compiler.version=193
compiler.runtime=dynamic
build_type=Release

[options]
openssl/*:shared=True
openssl/*:fips=False
openssl/*:no_asm=False
openssl/*:no_threads=False

[conf]
tools.system.package_manager:mode=install