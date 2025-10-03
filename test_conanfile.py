#!/usr/bin/env python3
"""
Simple test conanfile for testing the Python orchestrator
"""

from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake
from conan.tools.files import copy
import os

class TestPackageConan(ConanFile):
    name = "testpackage"
    version = "1.0.0"
    description = "Simple test package"
    license = "MIT"
    
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    
    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
    
    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
    
    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()
    
    def build(self):
        # Simple build - just create a test file
        test_file = os.path.join(self.build_folder, "test.txt")
        with open(test_file, 'w') as f:
            f.write("Hello from test package!")
    
    def package(self):
        copy(self, "test.txt", src=self.build_folder, dst=os.path.join(self.package_folder, "bin"))
    
    def package_info(self):
        self.cpp_info.libs = []
        self.cpp_info.bindirs = ["bin"]