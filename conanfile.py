#!/usr/bin/env python3
"""
C++ Project Conan Package Recipe
Based on ngapy-dev patterns for C++ development with Conan 2.x integration
"""

from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import copy, save, load
from conan.tools.scm import Git
from conan.tools.system import package_manager
from conan.errors import ConanInvalidConfiguration
import os
import re
import hashlib
import json
import uuid
from pathlib import Path


class CppProjectConan(ConanFile):
    name = "project-name"  # Change this to your project name
    version = "1.0.0"      # Change this to your project version
    
    # Package metadata
    description = "C++ project description"
    homepage = "https://github.com/your-org/project-name"
    url = "https://github.com/your-org/project-name"
    license = "Apache-2.0"
    topics = ("cpp", "project", "template")
    
    # Package configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_tests": [True, False],
        "enable_examples": [True, False],
        "enable_docs": [True, False],
    }
    
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_tests": True,
        "enable_examples": False,
        "enable_docs": False,
    }
    
    # Build requirements
    def build_requirements(self):
        if self.options.enable_tests:
            self.tool_requires("gtest/1.14.0")
        if self.options.enable_docs:
            self.tool_requires("doxygen/1.9.8")
    
    # Runtime requirements
    def requirements(self):
        # Add your project dependencies here
        # self.requires("boost/1.82.0")
        # self.requires("fmt/10.1.1")
        pass
    
    def system_requirements(self):
        # System package requirements for different platforms
        package_manager.Apt(self).install(["build-essential", "cmake", "git"])
        package_manager.Yum(self).install(["gcc", "gcc-c++", "make", "cmake", "git"])
        package_manager.PacMan(self).install(["base-devel", "cmake", "git"])
        package_manager.Zypper(self).install(["gcc", "gcc-c++", "make", "cmake", "git"])
    
    def set_version(self):
        """Set version from git or default - following ngapy patterns"""
        try:
            git = Git(self)
            # Get version from git describe or use default
            version = git.run("describe --tags --always --dirty")
            if version:
                # Clean up version string
                version = version.strip().replace("v", "")
                self.version = version
            else:
                self.version = "1.0.0"
        except:
            self.version = "1.0.0"
    
    def configure(self):
        """Configure package options"""
        # Static builds don't need fPIC
        if not self.options.shared:
            del self.options.fPIC
    
    def validate(self):
        """Validate configuration"""
        # Add your validation logic here
        pass
    
    def export_sources(self):
        """Export source files"""
        copy(self, "*", src=self.recipe_folder, dst=self.export_sources_folder)
    
    def layout(self):
        """Define build layout"""
        cmake_layout(self)
    
    def generate(self):
        """Generate build configuration"""
        deps = CMakeDeps(self)
        deps.generate()
        
        tc = CMakeToolchain(self)
        tc.variables["ENABLE_TESTS"] = self.options.enable_tests
        tc.variables["ENABLE_EXAMPLES"] = self.options.enable_examples
        tc.variables["ENABLE_DOCS"] = self.options.enable_docs
        tc.generate()
    
    def build(self):
        """Build the package"""
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
        
        # Run tests if enabled
        if self.options.enable_tests:
            cmake.test()
    
    def package(self):
        """Package the built artifacts"""
        # Copy headers
        copy(self, "*.h", src=self.source_folder, dst=os.path.join(self.package_folder, "include"))
        copy(self, "*.hpp", src=self.source_folder, dst=os.path.join(self.package_folder, "include"))
        
        # Copy libraries
        copy(self, "*.lib", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.a", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.so*", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.dylib", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.dll", src=self.build_folder, dst=os.path.join(self.package_folder, "bin"), keep_path=False)
        
        # Copy executables
        copy(self, "*.exe", src=self.build_folder, dst=os.path.join(self.package_folder, "bin"), keep_path=False)
        copy(self, "*", src=self.build_folder, dst=os.path.join(self.package_folder, "bin"), keep_path=False, excludes="*.o")
        
        # Copy license
        copy(self, "LICENSE*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        
        # Generate SBOM
        self._generate_sbom()
    
    def _calculate_file_hash(self, filepath, algorithm='sha256'):
        """Calculate cryptographic hash of a file"""
        hash_func = getattr(hashlib, algorithm)()
        try:
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_func.update(chunk)
            return hash_func.hexdigest()
        except Exception as e:
            self.output.warning(f"Failed to calculate hash for {filepath}: {e}")
            return None
    
    def _generate_sbom(self):
        """Generate Software Bill of Materials following ngapy patterns"""
        self.output.info("Generating Software Bill of Materials (SBOM)...")
        
        # Calculate hashes for main files
        file_hashes = {}
        for root, dirs, files in os.walk(self.package_folder):
            for file in files:
                if file.endswith(('.h', '.hpp', '.cpp', '.c', '.lib', '.a', '.so', '.dll', '.exe')):
                    file_path = os.path.join(root, file)
                    sha256 = self._calculate_file_hash(file_path, 'sha256')
                    if sha256:
                        rel_path = os.path.relpath(file_path, self.package_folder)
                        file_hashes[rel_path] = {
                            "sha256": sha256,
                            "algorithm": "SHA-256"
                        }
        
        # Enhanced metadata collection - pattern from ngapy-dev
        build_metadata = {
            "build_timestamp": os.environ.get("SOURCE_DATE_EPOCH", ""),
            "build_platform": f"{self.settings.os}-{self.settings.arch}",
            "compiler": f"{self.settings.compiler}-{self.settings.compiler.version}",
            "build_type": str(self.settings.build_type),
            "conan_version": "2.0",
            "build_options": {k: str(v) for k, v in self.options.items()}
        }
        
        sbom_data = {
            "bomFormat": "CycloneDX",
            "specVersion": "1.5",
            "serialNumber": f"urn:uuid:{uuid.uuid4()}",
            "version": 1,
            "metadata": {
                "timestamp": str(os.environ.get("SOURCE_DATE_EPOCH", "")),
                "component": {
                    "type": "library",
                    "bom-ref": f"{self.name}@{self.version}",
                    "name": self.name,
                    "version": str(self.version),
                    "description": self.description,
                    "licenses": [{"license": {"id": "Apache-2.0"}}],
                    "hashes": [{"alg": "SHA-256", "content": h["sha256"]} 
                              for h in file_hashes.values()],
                    "externalReferences": [
                        {
                            "type": "website",
                            "url": self.homepage
                        },
                        {
                            "type": "vcs",
                            "url": self.url
                        }
                    ],
                    "properties": [
                        {"name": "build_metadata", "value": json.dumps(build_metadata)},
                        {"name": "conan_options", "value": json.dumps({k: str(v) for k, v in self.options.items()})},
                        {"name": "build_platform", "value": f"{self.settings.os}-{self.settings.arch}"},
                        {"name": "package_type", "value": "cpp-library"}
                    ]
                },
                "tools": [
                    {
                        "vendor": "Conan",
                        "name": "conan",
                        "version": "2.0"
                    }
                ]
            },
            "components": [],
            "vulnerabilities": []
        }
        
        # Add dependencies to SBOM
        deps = getattr(self, "deps_cpp_info", None)
        if deps and hasattr(deps, "deps"):
            for dep in deps.deps:
                try:
                    dep_version = str(deps[dep].version) if hasattr(deps[dep], "version") else "unknown"
                    component = {
                        "type": "library",
                        "bom-ref": f"{dep}@{dep_version}",
                        "name": dep,
                        "version": dep_version,
                        "scope": "required",
                        "licenses": []
                    }
                    sbom_data["components"].append(component)
                except Exception as e:
                    self.output.warning(f"Failed to add dependency {dep} to SBOM: {e}")
        
        # Save SBOM
        sbom_path = os.path.join(self.package_folder, "sbom.json")
        save(self, sbom_path, json.dumps(sbom_data, indent=2))
        self.output.success(f"SBOM generated: {sbom_path}")
        
        # Generate package signature if key is available
        self._sign_package(sbom_path)
        
        # Generate vulnerability report placeholder
        self._generate_vulnerability_report()
    
    def _sign_package(self, sbom_path):
        """Sign package for supply chain security (placeholder for actual signing)"""
        signing_enabled = os.getenv("CONAN_SIGN_PACKAGES", "false").lower() == "true"
        
        if not signing_enabled:
            self.output.info("Package signing disabled (set CONAN_SIGN_PACKAGES=true to enable)")
            return
        
        self.output.info("Package signing placeholder - integrate with cosign/gpg in production")
        
        signature_metadata = {
            "signed": True,
            "timestamp": str(os.environ.get("SOURCE_DATE_EPOCH", "")),
            "algorithm": "placeholder",
            "keyid": "placeholder"
        }
        
        sig_path = os.path.join(self.package_folder, "package-signature.json")
        save(self, sig_path, json.dumps(signature_metadata, indent=2))
    
    def _generate_vulnerability_report(self):
        """Generate vulnerability scan report (integration point)"""
        vuln_report = {
            "scanTool": "placeholder",
            "scanDate": str(os.environ.get("SOURCE_DATE_EPOCH", "")),
            "component": f"{self.name}@{self.version}",
            "vulnerabilities": [],
            "note": "Integrate with Trivy/Snyk for actual vulnerability scanning"
        }
        
        vuln_path = os.path.join(self.package_folder, "vulnerability-report.json")
        save(self, vuln_path, json.dumps(vuln_report, indent=2))
        self.output.info(f"Vulnerability report placeholder generated: {vuln_path}")
    
    def package_info(self):
        """Package info following ngapy patterns"""
        # Set package information
        self.cpp_info.libs = ["project-name"]  # Change to your library name
        
        # Set binary paths
        self.cpp_info.bindirs = ["bin"]
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.libdirs = ["lib"]
        
        # Environment variables
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        if self.settings.os == "Linux":
            self.env_info.LD_LIBRARY_PATH.append(os.path.join(self.package_folder, "lib"))
        elif self.settings.os == "Macos":
            self.env_info.DYLD_LIBRARY_PATH.append(os.path.join(self.package_folder, "lib"))
    
    def package_id(self):
        """Optimize package ID for better caching"""
        # Test-only options don't affect package ID
        del self.info.options.enable_tests
        del self.info.options.enable_examples
        del self.info.options.enable_docs