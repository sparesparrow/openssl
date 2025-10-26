"""
vcpkg Integration Utilities

Provides integration between vcpkg and OpenSSL build systems.
"""

import os
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List
from .detector import VcpkgDetector
from .manager import VcpkgManager


class VcpkgIntegration:
    """Integrates vcpkg with OpenSSL build systems."""
    
    def __init__(self, vcpkg_root: Optional[str] = None):
        self.detector = VcpkgDetector()
        self.vcpkg_root = vcpkg_root or self.detector.detect_vcpkg_root()
        self.manager = VcpkgManager(self.vcpkg_root) if self.vcpkg_root else None
        
    def setup_cmake_integration(self, cmake_file_path: str) -> bool:
        """Setup CMake integration with vcpkg."""
        if not self.vcpkg_root:
            return False
        
        cmake_content = f"""# vcpkg integration for OpenSSL
set(VCPKG_ROOT "{self.vcpkg_root}")
set(VCPKG_DEFAULT_TRIPLET "${{VCPKG_DEFAULT_TRIPLET}}")
set(CMAKE_TOOLCHAIN_FILE "${{VCPKG_ROOT}}/scripts/buildsystems/vcpkg.cmake")

# Find OpenSSL via vcpkg
find_package(OpenSSL REQUIRED)

# Set OpenSSL variables
if(OpenSSL_FOUND)
    set(OPENSSL_FOUND TRUE)
    set(OPENSSL_INCLUDE_DIR ${{OpenSSL_INCLUDE_DIR}})
    set(OPENSSL_LIBRARIES ${{OpenSSL_LIBRARIES}})
    set(OPENSSL_VERSION ${{OpenSSL_VERSION}})
    set(OPENSSL_VERSION_TEXT "${{OpenSSL_VERSION_TEXT}}")
    
    # Create imported targets
    if(NOT TARGET OpenSSL::SSL)
        add_library(OpenSSL::SSL INTERFACE IMPORTED)
        set_target_properties(OpenSSL::SSL PROPERTIES
            INTERFACE_INCLUDE_DIRECTORIES "${{OpenSSL_INCLUDE_DIR}}"
            INTERFACE_LINK_LIBRARIES "${{OpenSSL_LIBRARIES}}"
        )
    endif()
    
    if(NOT TARGET OpenSSL::Crypto)
        add_library(OpenSSL::Crypto INTERFACE IMPORTED)
        set_target_properties(OpenSSL::Crypto PROPERTIES
            INTERFACE_INCLUDE_DIRECTORIES "${{OpenSSL_INCLUDE_DIR}}"
            INTERFACE_LINK_LIBRARIES "${{OpenSSL_LIBRARIES}}"
        )
    endif()
    
    message(STATUS "OpenSSL found via vcpkg: ${{OpenSSL_VERSION}}")
    message(STATUS "OpenSSL include dir: ${{OPENSSL_INCLUDE_DIR}}")
    message(STATUS "OpenSSL libraries: ${{OPENSSL_LIBRARIES}}")
else()
    message(FATAL_ERROR "OpenSSL not found via vcpkg")
endif()
"""
        
        try:
            with open(cmake_file_path, 'w') as f:
                f.write(cmake_content)
            return True
        except Exception:
            return False
    
    def setup_environment(self, output_file: str = None) -> Dict[str, str]:
        """Setup environment variables for vcpkg integration."""
        env_vars = self.detector.get_environment_variables()
        
        if output_file:
            # Generate shell script
            script_content = "#!/bin/bash\n# vcpkg environment setup\n\n"
            for key, value in env_vars.items():
                script_content += f"export {key}=\"{value}\"\n"
            
            try:
                with open(output_file, 'w') as f:
                    f.write(script_content)
                os.chmod(output_file, 0o755)
            except Exception:
                pass
        
        return env_vars
    
    def generate_conan_integration(self, output_file: str) -> bool:
        """Generate Conan integration script for vcpkg."""
        if not self.vcpkg_root:
            return False
        
        integration_content = f'''"""
Conan integration with vcpkg for OpenSSL builds.
"""

import os
from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMakeDeps

class VcpkgOpenSSLIntegration:
    """Integration between Conan and vcpkg for OpenSSL."""
    
    def __init__(self, conanfile: ConanFile):
        self.conanfile = conanfile
        self.vcpkg_root = "{self.vcpkg_root}"
        
    def setup_cmake_toolchain(self):
        """Setup CMake toolchain with vcpkg integration."""
        toolchain = CMakeToolchain(self.conanfile)
        
        # Set vcpkg toolchain file
        toolchain.variables["CMAKE_TOOLCHAIN_FILE"] = os.path.join(
            self.vcpkg_root, "scripts", "buildsystems", "vcpkg.cmake"
        )
        
        # Set vcpkg triplet
        triplet = self._get_vcpkg_triplet()
        toolchain.variables["VCPKG_DEFAULT_TRIPLET"] = triplet
        toolchain.variables["VCPKG_DEFAULT_HOST_TRIPLET"] = triplet
        
        return toolchain
    
    def _get_vcpkg_triplet(self):
        """Get vcpkg triplet from Conan settings."""
        os_map = {{
            "Windows": "windows",
            "Linux": "linux",
            "Macos": "osx"
        }}
        
        arch_map = {{
            "x86_64": "x64",
            "x86": "x86",
            "armv8": "arm64",
            "armv7": "arm"
        }}
        
        os_name = os_map.get(str(self.conanfile.settings.os), "linux")
        arch_name = arch_map.get(str(self.conanfile.settings.arch), "x64")
        
        return f"{{os_name}}-{{arch_name}}"
'''
        
        try:
            with open(output_file, 'w') as f:
                f.write(integration_content)
            return True
        except Exception:
            return False
    
    def create_project_template(self, project_dir: str, project_name: str = "openssl-project") -> bool:
        """Create a complete project template with vcpkg integration."""
        try:
            project_path = Path(project_dir)
            project_path.mkdir(parents=True, exist_ok=True)
            
            # Create CMakeLists.txt
            cmake_content = f"""cmake_minimum_required(VERSION 3.20)
project({project_name})

# Include vcpkg integration
include(vcpkg-openssl.cmake)

# Add executable
add_executable(${{PROJECT_NAME}} main.cpp)

# Link with OpenSSL
target_link_libraries(${{PROJECT_NAME}} 
    PRIVATE 
    OpenSSL::SSL 
    OpenSSL::Crypto
)

# Set C++ standard
target_compile_features(${{PROJECT_NAME}} PRIVATE cxx_std_17)
"""
            
            with open(project_path / "CMakeLists.txt", 'w') as f:
                f.write(cmake_content)
            
            # Create vcpkg integration file
            self.setup_cmake_integration(str(project_path / "vcpkg-openssl.cmake"))
            
            # Create main.cpp
            main_cpp = '''#include <iostream>
#include <openssl/ssl.h>
#include <openssl/evp.h>

int main() {
    std::cout << "OpenSSL vcpkg Integration Test" << std::endl;
    std::cout << "OpenSSL version: " << OpenSSL_version(OPENSSL_VERSION) << std::endl;
    
    // Initialize OpenSSL
    SSL_library_init();
    OpenSSL_add_all_algorithms();
    
    std::cout << "✅ OpenSSL vcpkg integration working!" << std::endl;
    return 0;
}
'''
            
            with open(project_path / "main.cpp", 'w') as f:
                f.write(main_cpp)
            
            # Create vcpkg.json manifest
            manifest = {
                "name": project_name,
                "version": "1.0.0",
                "description": f"{project_name} with OpenSSL vcpkg integration",
                "dependencies": [
                    {
                        "name": "openssl",
                        "features": ["tools"]
                    },
                    {
                        "name": "zlib"
                    }
                ]
            }
            
            with open(project_path / "vcpkg.json", 'w') as f:
                json.dump(manifest, f, indent=2)
            
            # Create environment setup script
            self.setup_environment(str(project_path / "setup-vcpkg-env.sh"))
            
            return True
            
        except Exception:
            return False
    
    def validate_integration(self) -> Dict[str, Any]:
        """Validate vcpkg integration setup."""
        validation = {
            "vcpkg_available": False,
            "openssl_installed": False,
            "cmake_toolchain": False,
            "environment_setup": False,
            "errors": []
        }
        
        # Check vcpkg availability
        if self.detector.is_vcpkg_available():
            validation["vcpkg_available"] = True
        else:
            validation["errors"].append("vcpkg not available")
        
        # Check OpenSSL installation
        if self.manager and self.manager.is_package_installed("openssl"):
            validation["openssl_installed"] = True
        else:
            validation["errors"].append("OpenSSL not installed via vcpkg")
        
        # Check CMake toolchain file
        if self.vcpkg_root:
            toolchain_file = os.path.join(self.vcpkg_root, "scripts", "buildsystems", "vcpkg.cmake")
            if os.path.exists(toolchain_file):
                validation["cmake_toolchain"] = True
            else:
                validation["errors"].append("CMake toolchain file not found")
        else:
            validation["errors"].append("vcpkg root not found")
        
        # Check environment setup
        env_vars = self.detector.get_environment_variables()
        if env_vars:
            validation["environment_setup"] = True
        else:
            validation["errors"].append("Environment variables not set")
        
        return validation