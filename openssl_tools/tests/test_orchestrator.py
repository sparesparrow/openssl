"""
Unit tests for OpenSSLBuildOrchestrator
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os
from pathlib import Path
import sys

# Add the parent directory to sys.path to import the orchestrator
sys.path.insert(0, str(Path(__file__).parent.parent))

from build_orchestrator import OpenSSLBuildOrchestrator


class TestOpenSSLBuildOrchestrator(unittest.TestCase):
    """Test cases for OpenSSLBuildOrchestrator."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_conanfile = Mock()
        self.mock_conanfile.source_folder = "/tmp/source"
        self.mock_conanfile.build_folder = "/tmp/build"
        self.mock_conanfile.package_folder = "/tmp/package"
        self.mock_conanfile.recipe_folder = "/tmp/recipe"
        self.mock_conanfile.output = Mock()

        # Create a temporary directory structure for testing
        self.temp_dir = tempfile.mkdtemp()
        self.orchestrator = OpenSSLBuildOrchestrator(self.mock_conanfile)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_init(self):
        """Test orchestrator initialization."""
        self.assertEqual(self.orchestrator.conanfile, self.mock_conanfile)
        self.assertEqual(self.orchestrator.source_folder, Path("/tmp/source"))
        self.assertEqual(self.orchestrator.build_folder, Path("/tmp/build"))
        self.assertEqual(self.orchestrator.package_folder, Path("/tmp/package"))
        self.assertEqual(self.orchestrator.recipe_folder, Path("/tmp/recipe"))

    def test_determine_source_directory_source_folder(self):
        """Test source directory determination when Configure exists in source_folder."""
        with patch('pathlib.Path.exists') as mock_exists:
            mock_exists.return_value = True
            result = self.orchestrator._determine_source_directory()
            self.assertEqual(result, Path("/tmp/source"))
            mock_exists.assert_called_with(Path("/tmp/source") / "Configure")

    def test_determine_source_directory_recipe_folder(self):
        """Test source directory determination when Configure exists in recipe_folder."""
        with patch('pathlib.Path.exists') as mock_exists:
            # Configure doesn't exist in source_folder
            def side_effect(path):
                return str(path).endswith("recipe/Configure")

            mock_exists.side_effect = side_effect
            result = self.orchestrator._determine_source_directory()
            self.assertEqual(result, Path("/tmp/recipe"))

    def test_determine_source_directory_default(self):
        """Test source directory determination defaults to source_folder."""
        with patch('pathlib.Path.exists') as mock_exists:
            mock_exists.return_value = False
            result = self.orchestrator._determine_source_directory()
            self.assertEqual(result, Path("/tmp/source"))

    @patch('subprocess.run')
    @patch('os.chdir')
    def test_configure_and_build_success(self, mock_chdir, mock_run):
        """Test successful configure and build process."""
        # Mock successful subprocess calls
        mock_run.return_value = Mock(returncode=0, stderr="")

        with patch.object(self.orchestrator, '_should_skip_tests', return_value=False):
            self.orchestrator.configure_and_build()

        # Verify subprocess calls were made
        self.assertGreaterEqual(mock_run.call_count, 2)  # configure + build + test

    @patch('subprocess.run')
    @patch('os.chdir')
    def test_configure_and_build_configure_failure(self, mock_chdir, mock_run):
        """Test configure failure handling."""
        # Mock configure failure
        mock_run.return_value = Mock(returncode=1, stderr="configure error")

        with self.assertRaises(Exception) as context:
            self.orchestrator.configure_and_build()

        self.assertIn("OpenSSL configuration failed", str(context.exception))

    @patch('subprocess.run')
    @patch('os.chdir')
    def test_configure_and_build_build_failure(self, mock_chdir, mock_run):
        """Test build failure handling."""
        # Configure succeeds, build fails
        mock_run.side_effect = [
            Mock(returncode=0, stderr=""),  # configure
            Mock(returncode=1, stderr="build error")  # build
        ]

        with self.assertRaises(Exception) as context:
            self.orchestrator.configure_and_build()

        self.assertIn("OpenSSL build failed", str(context.exception))

    @patch('subprocess.run')
    @patch('os.chdir')
    def test_install_and_package_success(self, mock_chdir, mock_run):
        """Test successful install and package process."""
        mock_run.return_value = Mock(returncode=0, stderr="")

        with patch('pathlib.Path.mkdir'), \
             patch.object(self.orchestrator, '_copy_to_package_folder'):
            self.orchestrator.install_and_package()

        # Verify installation was attempted
        mock_run.assert_called()

    @patch('subprocess.run')
    def test_configure_openssl_success(self, mock_run):
        """Test successful OpenSSL configuration."""
        mock_run.return_value = Mock(returncode=0, stderr="")

        with patch.object(self.orchestrator, '_build_python_configure_command', return_value=['python', 'configure.py']):
            result = self.orchestrator._configure_openssl()
            self.assertTrue(result)

    @patch('subprocess.run')
    def test_configure_openssl_failure(self, mock_run):
        """Test OpenSSL configuration failure."""
        mock_run.return_value = Mock(returncode=1, stderr="configure error")

        with patch.object(self.orchestrator, '_build_python_configure_command', return_value=['python', 'configure.py']):
            result = self.orchestrator._configure_openssl()
            self.assertFalse(result)

    @patch('subprocess.run')
    def test_build_openssl_success(self, mock_run):
        """Test successful OpenSSL build."""
        mock_run.return_value = Mock(returncode=0, stderr="")

        result = self.orchestrator._build_openssl()
        self.assertTrue(result)

    @patch('subprocess.run')
    def test_build_openssl_failure(self, mock_run):
        """Test OpenSSL build failure."""
        mock_run.return_value = Mock(returncode=1, stderr="build error")

        result = self.orchestrator._build_openssl()
        self.assertFalse(result)

    @patch('subprocess.run')
    def test_test_openssl_success(self, mock_run):
        """Test successful OpenSSL testing."""
        mock_run.return_value = Mock(returncode=0, stderr="")

        result = self.orchestrator._test_openssl()
        self.assertTrue(result)

    @patch('subprocess.run')
    def test_test_openssl_failure(self, mock_run):
        """Test OpenSSL test failure."""
        mock_run.return_value = Mock(returncode=1, stderr="test error")

        result = self.orchestrator._test_openssl()
        self.assertFalse(result)

    def test_should_skip_tests(self):
        """Test test skipping logic."""
        # Test with no skip_tests option
        result = self.orchestrator._should_skip_tests()
        self.assertFalse(result)

        # Test with skip_tests=True
        self.mock_conanfile.options.skip_tests = True
        result = self.orchestrator._should_skip_tests()
        self.assertTrue(result)

    def test_get_optimal_job_count(self):
        """Test job count determination."""
        result = self.orchestrator._get_optimal_job_count()
        self.assertIsInstance(result, int)
        self.assertGreater(result, 0)

    def test_build_python_configure_command(self):
        """Test Python configure command building."""
        with patch.object(self.orchestrator, '_get_build_options', return_value=['--prefix=/usr']):
            cmd = self.orchestrator._build_python_configure_command()
            self.assertIsInstance(cmd, list)
            self.assertIn('python', cmd[0])

    def test_get_build_options(self):
        """Test build options generation."""
        # Mock conanfile settings and options
        self.mock_conanfile.settings = Mock()
        self.mock_conanfile.settings.os = 'Linux'
        self.mock_conanfile.settings.arch = 'x86_64'
        self.mock_conanfile.settings.compiler = 'gcc'
        self.mock_conanfile.settings.build_type = 'Release'

        self.mock_conanfile.options = Mock()
        self.mock_conanfile.options.shared = True
        self.mock_conanfile.options.fPIC = True

        options = self.orchestrator._get_build_options()
        self.assertIsInstance(options, list)
        self.assertGreater(len(options), 0)


if __name__ == '__main__':
    unittest.main()