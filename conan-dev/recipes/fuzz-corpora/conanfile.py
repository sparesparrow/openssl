#!/usr/bin/env python3
"""
Conan recipe for OpenSSL Fuzz Corpora data
Downloads and packages the fuzz regression testing data from the fuzz-corpora repository.
"""

from conan import ConanFile
from conan.tools.files import download, unzip, copy, save
from conan.tools.scm import Git
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake
from conan.tools.layout import cmake_layout
import os
import shutil
from pathlib import Path


class FuzzCorporaConan(ConanFile):
    name = "openssl-fuzz-corpora"
    version = "1.0.0"
    description = "OpenSSL fuzz regression testing data from fuzz-corpora repository"
    license = "Apache-2.0"
    url = "https://github.com/openssl/openssl"
    homepage = "https://github.com/openssl/fuzz-corpora"
    topics = ("openssl", "fuzz", "corpora", "testing", "regression")
    
    # No settings needed for data-only package
    settings = "os", "arch"
    
    # Package options
    options = {
        "include_metadata": [True, False],
    }
    default_options = {
        "include_metadata": True,
    }
    
    def source(self):
        """Download the fuzz-corpora repository."""
        git = Git(self)
        git.clone("https://github.com/openssl/fuzz-corpora.git", target=".")
        git.checkout("main")
    
    def build(self):
        """No build step needed for data-only package."""
        pass
    
    def package(self):
        """Package the fuzz corpora data."""
        # Copy all corpora data to package
        corpora_src = self.source_folder
        corpora_dest = self.package_folder / "corpora"
        
        # Create corpora directory
        corpora_dest.mkdir(parents=True, exist_ok=True)
        
        # Copy all files and directories from the repository
        for item in corpora_src.iterdir():
            if item.name.startswith('.'):
                continue  # Skip hidden files like .git
            
            if item.is_file():
                copy(self, item.name, corpora_src, corpora_dest)
            elif item.is_dir():
                copy(self, f"{item.name}/*", corpora_src, corpora_dest)
        
        # Create a manifest file with metadata
        if self.options.include_metadata:
            manifest = {
                "name": self.name,
                "version": self.version,
                "description": self.description,
                "source_url": self.homepage,
                "package_type": "fuzz_corpora",
                "contents": []
            }
            
            # List all files in the corpora directory
            for root, dirs, files in os.walk(corpora_dest):
                for file in files:
                    rel_path = os.path.relpath(os.path.join(root, file), corpora_dest)
                    manifest["contents"].append(rel_path)
            
            save(self, os.path.join(corpora_dest, "manifest.json"), 
                 str(manifest).replace("'", '"'))
    
    def package_info(self):
        """Set package information for consumers."""
        # Set the corpora path for consumers
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.includedirs = []
        
        # Set the corpora data path
        self.cpp_info.resdirs = ["corpora"]
        
        # Add environment variable for easy access
        self.cpp_info.set_property("pkg_config_name", "openssl-fuzz-corpora")
        
        # Add custom property for corpora path
        self.cpp_info.set_property("corpora_path", os.path.join(self.package_folder, "corpora"))
        
        # Set environment variables for consumers
        self.cpp_info.env_info.OPENSSL_FUZZ_CORPORA_PATH = os.path.join(self.package_folder, "corpora")