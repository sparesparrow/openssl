#!/usr/bin/env python3
"""
Conan Performance Benchmark Script
Measures build performance and generates reports
"""

import time
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any
import argparse
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ConanPerformanceBenchmark:
    """Conan Performance Benchmarking Tool"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.results = {}
        
    def run_benchmark(self, profile: str = "linux-gcc11") -> Dict[str, Any]:
        """Run performance benchmark for a specific profile"""
        logger.info(f"🚀 Running benchmark for profile: {profile}")
        
        benchmark_results = {
            "profile": profile,
            "timestamp": time.time(),
            "metrics": {}
        }
        
        # Clean previous builds
        self._clean_build()
        
        # Measure install time
        install_time = self._measure_install_time(profile)
        benchmark_results["metrics"]["install_time"] = install_time
        
        # Measure build time
        build_time = self._measure_build_time(profile)
        benchmark_results["metrics"]["build_time"] = build_time
        
        # Measure test time
        test_time = self._measure_test_time(profile)
        benchmark_results["metrics"]["test_time"] = test_time
        
        # Measure package size
        package_size = self._measure_package_size()
        benchmark_results["metrics"]["package_size"] = package_size
        
        # Calculate total time
        total_time = install_time + build_time + test_time
        benchmark_results["metrics"]["total_time"] = total_time
        
        logger.info(f"✅ Benchmark complete for {profile}")
        logger.info(f"📊 Total time: {total_time:.2f}s")
        
        return benchmark_results
    
    def _clean_build(self):
        """Clean previous build artifacts"""
        logger.info("🧹 Cleaning previous build...")
        try:
            subprocess.run(["conan", "remove", "*", "--force"], 
                         check=True, capture_output=True)
            subprocess.run(["rm", "-rf", "build/", "package/"], 
                         check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            logger.warning(f"Clean failed: {e}")
    
    def _measure_install_time(self, profile: str) -> float:
        """Measure dependency installation time"""
        logger.info("📦 Measuring install time...")
        start_time = time.time()
        
        try:
            subprocess.run([
                "conan", "install", ".", 
                "--profile", profile, 
                "--build", "missing"
            ], check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"Install failed: {e}")
            return 0.0
        
        install_time = time.time() - start_time
        logger.info(f"⏱️ Install time: {install_time:.2f}s")
        return install_time
    
    def _measure_build_time(self, profile: str) -> float:
        """Measure package build time"""
        logger.info("🔨 Measuring build time...")
        start_time = time.time()
        
        try:
            subprocess.run([
                "conan", "build", ".", 
                "--profile", profile
            ], check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"Build failed: {e}")
            return 0.0
        
        build_time = time.time() - start_time
        logger.info(f"⏱️ Build time: {build_time:.2f}s")
        return build_time
    
    def _measure_test_time(self, profile: str) -> float:
        """Measure test execution time"""
        logger.info("🧪 Measuring test time...")
        start_time = time.time()
        
        try:
            subprocess.run([
                "conan", "test", "test_package", 
                "openssl/3.5.0@user/channel", 
                "--profile", profile
            ], check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"Test failed: {e}")
            return 0.0
        
        test_time = time.time() - start_time
        logger.info(f"⏱️ Test time: {test_time:.2f}s")
        return test_time
    
    def _measure_package_size(self) -> int:
        """Measure package size in bytes"""
        logger.info("📏 Measuring package size...")
        
        package_dir = Path("package")
        if not package_dir.exists():
            return 0
        
        total_size = 0
        for file_path in package_dir.rglob("*"):
            if file_path.is_file():
                total_size += file_path.stat().st_size
        
        logger.info(f"📦 Package size: {total_size / (1024*1024):.2f} MB")
        return total_size
    
    def run_all_profiles(self) -> Dict[str, Any]:
        """Run benchmark for all available profiles"""
        profiles = ["linux-gcc11", "linux-clang15", "debug"]
        all_results = {
            "timestamp": time.time(),
            "profiles": {}
        }
        
        for profile in profiles:
            profile_path = self.project_root / "conan-dev" / "profiles" / f"{profile}.profile"
            if profile_path.exists():
                try:
                    result = self.run_benchmark(profile)
                    all_results["profiles"][profile] = result
                except Exception as e:
                    logger.error(f"Benchmark failed for {profile}: {e}")
            else:
                logger.warning(f"Profile not found: {profile}")
        
        return all_results
    
    def save_results(self, results: Dict[str, Any], output_file: str = "performance_results.json"):
        """Save benchmark results to file"""
        output_path = self.project_root / output_file
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        logger.info(f"💾 Results saved to: {output_path}")
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate a human-readable performance report"""
        report = []
        report.append("# Conan Performance Benchmark Report")
        report.append(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        if "profiles" in results:
            report.append("## Profile Comparison")
            report.append("")
            report.append("| Profile | Install (s) | Build (s) | Test (s) | Total (s) | Package Size (MB) |")
            report.append("|---------|-------------|-----------|----------|------------|-------------------|")
            
            for profile_name, profile_data in results["profiles"].items():
                metrics = profile_data.get("metrics", {})
                install_time = metrics.get("install_time", 0)
                build_time = metrics.get("build_time", 0)
                test_time = metrics.get("test_time", 0)
                total_time = metrics.get("total_time", 0)
                package_size = metrics.get("package_size", 0) / (1024 * 1024)
                
                report.append(f"| {profile_name} | {install_time:.2f} | {build_time:.2f} | {test_time:.2f} | {total_time:.2f} | {package_size:.2f} |")
        
        report.append("")
        report.append("## Recommendations")
        report.append("")
        
        # Find fastest profile
        if "profiles" in results:
            fastest_profile = min(results["profiles"].items(), 
                                key=lambda x: x[1].get("metrics", {}).get("total_time", float('inf')))
            report.append(f"- **Fastest Profile**: {fastest_profile[0]} ({fastest_profile[1]['metrics']['total_time']:.2f}s)")
        
        report.append("- **Optimization Tips**:")
        report.append("  - Use `--build=missing` to avoid unnecessary rebuilds")
        report.append("  - Enable parallel builds with `-j$(nproc)`")
        report.append("  - Use binary packages when possible")
        report.append("  - Consider using lockfiles for reproducible builds")
        
        return "\n".join(report)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Conan Performance Benchmark")
    parser.add_argument("--profile", "-p", default="linux-gcc11",
                       help="Profile to benchmark")
    parser.add_argument("--all-profiles", "-a", action="store_true",
                       help="Run benchmark for all profiles")
    parser.add_argument("--output", "-o", default="performance_results.json",
                       help="Output file for results")
    parser.add_argument("--report", "-r", action="store_true",
                       help="Generate human-readable report")
    
    args = parser.parse_args()
    
    project_root = Path.cwd()
    benchmark = ConanPerformanceBenchmark(project_root)
    
    if args.all_profiles:
        results = benchmark.run_all_profiles()
    else:
        results = benchmark.run_benchmark(args.profile)
    
    benchmark.save_results(results, args.output)
    
    if args.report:
        report = benchmark.generate_report(results)
        print(report)
        
        report_file = project_root / "performance_report.md"
        with open(report_file, 'w') as f:
            f.write(report)
        logger.info(f"📊 Report saved to: {report_file}")

if __name__ == "__main__":
    main()