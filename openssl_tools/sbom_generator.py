"""
OpenSSL SBOM Generator

Generates Software Bill of Materials (SBOM) for OpenSSL packages.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional


class SbomGenerator:
    """Generates SBOM files for OpenSSL packages."""

    def __init__(self, conanfile):
        """Initialize SBOM generator with conanfile instance."""
        self.conanfile = conanfile
        self.package_folder = Path(conanfile.package_folder)

    def generate_and_save(self, format: str = "cyclonedx"):
        """Generate and save SBOM in specified format."""
        if format.lower() == "cyclonedx":
            self._generate_cyclonedx_sbom()
        elif format.lower() == "spdx":
            self._generate_spdx_sbom()
        else:
            raise ValueError(f"Unsupported SBOM format: {format}")

    def _generate_cyclonedx_sbom(self):
        """Generate CycloneDX format SBOM."""
        sbom_data = self._create_cyclonedx_sbom_data()

        sbom_file = self.package_folder / "sbom.json"
        sbom_file.parent.mkdir(parents=True, exist_ok=True)

        with open(sbom_file, 'w') as f:
            json.dump(sbom_data, f, indent=2)

        self.conanfile.output.info(f"Generated CycloneDX SBOM: {sbom_file}")

    def _generate_spdx_sbom(self):
        """Generate SPDX format SBOM."""
        sbom_data = self._create_spdx_sbom_data()

        sbom_file = self.package_folder / "sbom.spdx.json"
        sbom_file.parent.mkdir(parents=True, exist_ok=True)

        with open(sbom_file, 'w') as f:
            json.dump(sbom_data, f, indent=2)

        self.conanfile.output.info(f"Generated SPDX SBOM: {sbom_file}")

    def _create_cyclonedx_sbom_data(self) -> dict:
        """Create CycloneDX SBOM data structure."""
        timestamp = datetime.utcnow().isoformat() + "Z"

        return {
            "$schema": "http://cyclonedx.org/schema/bom-1.5.schema.json",
            "bomFormat": "CycloneDX",
            "specVersion": "1.5",
            "serialNumber": f"urn:uuid:{uuid.uuid4()}",
            "version": 1,
            "metadata": self._create_cyclonedx_metadata(timestamp),
            "components": self._create_cyclonedx_components()
        }

    def _create_spdx_sbom_data(self) -> dict:
        """Create SPDX SBOM data structure."""
        timestamp = datetime.utcnow().isoformat() + "Z"

        return {
            "spdxVersion": "SPDX-2.3",
            "dataLicense": "CC0-1.0",
            "SPDXID": f"SPDXRef-DOCUMENT-{uuid.uuid4()}",
            "name": f"SBOM-{self.conanfile.name}-{self.conanfile.version}",
            "creationInfo": {
                "created": timestamp,
                "creators": ["Tool: OpenSSL Conan Integration"]
            },
            "packages": self._create_spdx_packages()
        }

    def _create_cyclonedx_metadata(self, timestamp: str) -> dict:
        """Create CycloneDX metadata section."""
        return {
            "timestamp": timestamp,
            "tools": [{
                "vendor": "OpenSSL Project",
                "name": "Conan Integration",
                "version": self.conanfile.version
            }],
            "component": {
                "type": "library",
                "name": self.conanfile.name,
                "version": self.conanfile.version,
                "description": self.conanfile.description,
                "licenses": [{"license": {"id": "Apache-2.0"}}],
                "externalReferences": [{
                    "type": "website",
                    "url": self.conanfile.url
                }]
            }
        }

    def _create_cyclonedx_components(self) -> list:
        """Create CycloneDX components list."""
        components = []

        # Add zlib dependency if present
        if hasattr(self.conanfile, 'dependencies') and 'zlib' in str(self.conanfile.dependencies):
            components.append({
                "type": "library",
                "name": "zlib",
                "version": "1.3.1",  # From requirements
                "description": "Compression library",
                "licenses": [{"license": {"id": "Zlib"}}]
            })

        # Add FIPS compliance information
        if self.conanfile.options.fips:
            components.append({
                "type": "data",
                "name": "openssl-fips-certificate",
                "version": "140-3.2",
                "description": "FIPS 140-3 compliance certificate data",
                "licenses": [{"license": {"id": "proprietary"}}]
            })

        return components

    def _create_spdx_packages(self) -> list:
        """Create SPDX packages list."""
        packages = []

        # Main OpenSSL package
        packages.append({
            "SPDXID": f"SPDXRef-Package-{self.conanfile.name}",
            "name": self.conanfile.name,
            "versionInfo": self.conanfile.version,
            "downloadLocation": "NOASSERTION",
            "filesAnalyzed": False,
            "copyrightText": "NOASSERTION",
            "licenseConcluded": "Apache-2.0",
            "licenseDeclared": "Apache-2.0",
            "description": self.conanfile.description
        })

        # Add zlib dependency
        if hasattr(self.conanfile, 'dependencies') and 'zlib' in str(self.conanfile.dependencies):
            packages.append({
                "SPDXID": "SPDXRef-Package-zlib",
                "name": "zlib",
                "versionInfo": "1.3.1",
                "downloadLocation": "NOASSERTION",
                "filesAnalyzed": False,
                "copyrightText": "NOASSERTION",
                "licenseConcluded": "Zlib",
                "licenseDeclared": "Zlib",
                "description": "Compression library"
            })

        return packages

    def get_sbom_summary(self) -> dict:
        """Get summary of generated SBOM."""
        return {
            "package_name": self.conanfile.name,
            "package_version": self.conanfile.version,
            "fips_enabled": self.conanfile.options.fips,
            "shared_linking": self.conanfile.options.shared,
            "sbom_formats": ["cyclonedx", "spdx"],
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "compliance_level": "FIPS 140-3" if self.conanfile.options.fips else "Standard"
        }