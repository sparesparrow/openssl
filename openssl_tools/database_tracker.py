"""
OpenSSL Database Tracker

Tracks OpenSSL package builds and metadata in a database.
"""

import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional


class DatabaseTracker:
    """Tracks OpenSSL package information in a database."""

    def __init__(self, conanfile):
        """Initialize database tracker with conanfile instance."""
        self.conanfile = conanfile
        self.package_folder = Path(conanfile.package_folder)

        # Use environment variable for database path, fallback to local file
        db_path = Path(os.getenv('OPENSSL_BUILD_DB', './openssl_builds.db'))
        self.db_path = db_path
        self.use_sqlite = db_path.suffix == '.db'

    def track_package(self):
        """Track the current package build in the database."""
        package_info = self._collect_package_info()

        try:
            if self.use_sqlite:
                self._track_in_sqlite(package_info)
            else:
                self._track_in_json(package_info)

            self.conanfile.output.info(f"✅ Package tracked successfully: {package_info['package_id']}")
            self.conanfile.output.info(f"📦 Package ready for upload: {package_info['name']}/{package_info['version']}")
            self.conanfile.output.info(f"🏷️  Package ID: {package_info['package_id']}")

        except Exception as e:
            self.conanfile.output.error(f"❌ Failed to track package: {e}")

    def log_upload_completion(self, remote_name: str = None):
        """Log package upload completion."""
        package_info = self._collect_package_info()

        upload_msg = f"📤 Package upload completed: {package_info['package_id']}"
        if remote_name:
            upload_msg += f" to remote '{remote_name}'"

        self.conanfile.output.info(upload_msg)
        self.conanfile.output.info(f"🌐 Remote: {remote_name or 'default'}")
        self.conanfile.output.info(f"📋 Version: {package_info['version']}")
        self.conanfile.output.info(f"🏗️  Build Type: {package_info['build_type']}")
        self.conanfile.output.info(f"🖥️  Platform: {package_info['os']}-{package_info['arch']}")

        if package_info['fips_compliance']['enabled']:
            self.conanfile.output.info("🔐 FIPS Mode: Enabled")
        else:
            self.conanfile.output.info("🔓 FIPS Mode: Standard")

        self.conanfile.output.info("✅ Package is now available for consumption")

    def _collect_package_info(self) -> dict:
        """Collect comprehensive package information."""
        return {
            "package_id": f"{self.conanfile.name}/{self.conanfile.version}@{self.conanfile.user}/{self.conanfile.channel}",
            "name": self.conanfile.name,
            "version": self.conanfile.version,
            "user": getattr(self.conanfile, 'user', 'unknown'),
            "channel": getattr(self.conanfile, 'channel', 'unknown'),
            "build_timestamp": datetime.utcnow().isoformat() + "Z",
            "build_type": str(self.conanfile.settings.build_type),
            "os": str(self.conanfile.settings.os),
            "arch": str(self.conanfile.settings.arch),
            "compiler": str(self.conanfile.settings.compiler),
            "compiler_version": str(getattr(self.conanfile.settings.compiler, 'version', 'unknown')),
            "options": {
                "shared": self.conanfile.options.shared,
                "fips": self.conanfile.options.fips,
                "no_threads": self.conanfile.options.no_threads,
                "no_asm": self.conanfile.options.no_asm,
                "fPIC": self.conanfile.options.fPIC
            },
            "dependencies": self._get_dependencies_info(),
            "fips_compliance": self._get_fips_info(),
            "build_metadata": {
                "source_folder": str(getattr(self.conanfile, 'source_folder', 'unknown')),
                "build_folder": str(getattr(self.conanfile, 'build_folder', 'unknown')),
                "package_folder": str(self.package_folder)
            }
        }

    def _get_dependencies_info(self) -> list:
        """Get information about package dependencies."""
        dependencies = []

        # Add zlib dependency info
        if hasattr(self.conanfile, 'dependencies'):
            for dep in self.conanfile.dependencies:
                if 'zlib' in str(dep):
                    dependencies.append({
                        "name": "zlib",
                        "version": "1.3.1",
                        "required": True
                    })
                    break

        # Add python_requires info
        if hasattr(self.conanfile, 'python_requires'):
            for req_name, req_ref in self.conanfile.python_requires.items():
                dependencies.append({
                    "name": req_name,
                    "version": str(req_ref.ref.version),
                    "type": "python_requires",
                    "required": True
                })

        return dependencies

    def _get_fips_info(self) -> dict:
        """Get FIPS compliance information."""
        fips_info = {
            "enabled": self.conanfile.options.fips,
            "certificate": None,
            "validation_status": "not_applicable"
        }

        if self.conanfile.options.fips:
            fips_info.update({
                "certificate": "FIPS 140-3 Certificate #4985",
                "validation_status": "pending_validation",
                "module_path": str(self.package_folder / "lib" / "ossl-modules")
            })

        return fips_info

    def _track_in_sqlite(self, package_info: dict):
        """Track package in SQLite database."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(str(self.db_path))
        try:
            self._create_sqlite_tables(conn)
            self._insert_package_sqlite(conn, package_info)
        finally:
            conn.close()

    def _track_in_json(self, package_info: dict):
        """Track package in JSON file."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Load existing data
        existing_data = []
        if self.db_path.exists():
            try:
                with open(self.db_path, 'r') as f:
                    existing_data = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                existing_data = []

        # Add new package info
        existing_data.append(package_info)

        # Save updated data
        with open(self.db_path, 'w') as f:
            json.dump(existing_data, f, indent=2)

    def _create_sqlite_tables(self, conn: sqlite3.Connection):
        """Create SQLite tables if they don't exist."""
        conn.execute('''
            CREATE TABLE IF NOT EXISTS packages (
                package_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                version TEXT NOT NULL,
                user TEXT,
                channel TEXT,
                build_timestamp TEXT,
                build_type TEXT,
                os TEXT,
                arch TEXT,
                compiler TEXT,
                compiler_version TEXT,
                options TEXT,  -- JSON string
                dependencies TEXT,  -- JSON string
                fips_compliance TEXT,  -- JSON string
                build_metadata TEXT  -- JSON string
            )
        ''')

        conn.execute('''
            CREATE TABLE IF NOT EXISTS build_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                package_id TEXT,
                metric_name TEXT,
                metric_value TEXT,
                timestamp TEXT,
                FOREIGN KEY (package_id) REFERENCES packages (package_id)
            )
        ''')

        conn.commit()

    def _insert_package_sqlite(self, conn: sqlite3.Connection, package_info: dict):
        """Insert package information into SQLite database."""
        conn.execute('''
            INSERT OR REPLACE INTO packages
            (package_id, name, version, user, channel, build_timestamp,
             build_type, os, arch, compiler, compiler_version,
             options, dependencies, fips_compliance, build_metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            package_info['package_id'],
            package_info['name'],
            package_info['version'],
            package_info['user'],
            package_info['channel'],
            package_info['build_timestamp'],
            package_info['build_type'],
            package_info['os'],
            package_info['arch'],
            package_info['compiler'],
            package_info['compiler_version'],
            json.dumps(package_info['options']),
            json.dumps(package_info['dependencies']),
            json.dumps(package_info['fips_compliance']),
            json.dumps(package_info['build_metadata'])
        ))

        conn.commit()

    def get_package_history(self, package_name: str = None, limit: int = 10) -> list:
        """Get package build history."""
        if not self.db_path.exists():
            return []

        try:
            if self.use_sqlite:
                return self._get_history_sqlite(package_name, limit)
            else:
                return self._get_history_json(package_name, limit)
        except Exception:
            return []

    def _get_history_sqlite(self, package_name: str = None, limit: int = 10) -> list:
        """Get package history from SQLite."""
        conn = sqlite3.connect(str(self.db_path))
        try:
            query = '''
                SELECT package_id, version, build_timestamp, build_type, os, arch
                FROM packages
            '''
            params = []

            if package_name:
                query += ' WHERE name = ?'
                params.append(package_name)

            query += ' ORDER BY build_timestamp DESC LIMIT ?'
            params.append(limit)

            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def _get_history_json(self, package_name: str = None, limit: int = 10) -> list:
        """Get package history from JSON file."""
        try:
            with open(self.db_path, 'r') as f:
                data = json.load(f)

            # Filter and sort
            filtered = data
            if package_name:
                filtered = [p for p in data if p.get('name') == package_name]

            # Sort by timestamp descending and limit
            filtered.sort(key=lambda x: x.get('build_timestamp', ''), reverse=True)
            return filtered[:limit]
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def get_build_stats(self) -> dict:
        """Get build statistics."""
        history = self.get_package_history(limit=1000)

        stats = {
            "total_builds": len(history),
            "unique_packages": len(set(p.get('package_id', '').split('/')[0] for p in history)),
            "platforms": {},
            "build_types": {},
            "compilers": {}
        }

        for build in history:
            # Count platforms
            platform = f"{build.get('os', 'unknown')}-{build.get('arch', 'unknown')}"
            stats["platforms"][platform] = stats["platforms"].get(platform, 0) + 1

            # Count build types
            build_type = build.get('build_type', 'unknown')
            stats["build_types"][build_type] = stats["build_types"].get(build_type, 0) + 1

            # Count compilers
            compiler = build.get('compiler', 'unknown')
            stats["compilers"][compiler] = stats["compilers"].get(compiler, 0) + 1

        return stats