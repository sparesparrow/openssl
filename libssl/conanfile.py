from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake, cmake_layout
from conan.tools.files import copy
import os


class LibSSLConan(ConanFile):
    name = "libssl"
    description = "OpenSSL SSL/TLS library"
    version = "3.4.1"
    license = "Apache-2.0"

    python_requires = "openssl-tools/1.2.4"

    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_tests": [True, False],
        "deployment_target": ["general", "fips-government", "embedded"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_tests": False,
        "deployment_target": "general",
    }

    def requirements(self):
        self.requires("libcrypto/3.4.1")

    def configure(self):
        if self.settings.os == "Windows":
            self.options.fPIC = False
        elif not self.options.shared:
            self.options.fPIC = True

    def layout(self):
        cmake_layout(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_CRYPTO_ONLY"] = False
        tc.variables["BUILD_SSL"] = True
        tc.variables["BUILD_SHARED"] = self.options.shared
        tc.variables["BUILD_TESTING"] = self.options.enable_tests
        tc.variables["DEPLOYMENT_TARGET"] = str(self.options.deployment_target)
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

        # Copy additional files
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.libs = ["ssl"]
        self.cpp_info.set_property("cmake_file_name", "OpenSSL")
        self.cpp_info.set_property("cmake_target_name", "OpenSSL::SSL")
        self.cpp_info.set_property("pkg_config_name", "libssl")

        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["ws2_32", "crypt32", "advapi32"]
        elif self.settings.os == "Linux":
            self.cpp_info.system_libs = ["dl", "pthread"]

        # Define components
        self.cpp_info.components["ssl"].libs = ["ssl"]
        self.cpp_info.components["ssl"].requires = ["libcrypto::crypto"]
        self.cpp_info.components["ssl"].set_property("cmake_target_name", "OpenSSL::SSL")
        self.cpp_info.components["ssl"].set_property("pkg_config_name", "libssl")