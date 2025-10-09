#!/usr/bin/env python3
"""
Build Metrics Collector
Collects comprehensive build metrics for analysis and optimization
"""

import os
import json
import time
import psutil
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class BuildMetrics:
    """Data class for build metrics"""
    timestamp: str
    build_id: str
    source_repo: str
    source_sha: str
    platform: str
    profile: str
    build_scope: str
    
    # Performance metrics
    total_build_time: float
    configure_time: float
    compile_time: float
    link_time: float
    test_time: float
    package_time: float
    
    # Resource utilization
    peak_memory_mb: float
    avg_cpu_percent: float
    peak_cpu_percent: float
    disk_io_read_mb: float
    disk_io_write_mb: float
    
    # Cache metrics
    cache_hit_rate: float
    cache_miss_count: int
    cache_size_mb: float
    
    # Build results
    build_status: str
    test_passed: int
    test_failed: int
    test_skipped: int
    
    # Artifacts
    artifact_count: int
    artifact_size_mb: float
    
    # Quality metrics
    warnings_count: int
    errors_count: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


class MetricsCollector:
    """Collects comprehensive build metrics during build process"""
    
    def __init__(self, build_id: str, source_repo: str, source_sha: str, 
                 platform: str, profile: str, build_scope: str):
        self.build_id = build_id
        self.source_repo = source_repo
        self.source_sha = source_sha
        self.platform = platform
        self.profile = profile
        self.build_scope = build_scope
        
        self.start_time = time.time()
        self.phase_times = {}
        self.resource_samples = []
        self.monitoring_active = False
        self.monitoring_thread = None
        
        # Initialize metrics
        self.metrics = BuildMetrics(
            timestamp=datetime.utcnow().isoformat(),
            build_id=build_id,
            source_repo=source_repo,
            source_sha=source_sha,
            platform=platform,
            profile=profile,
            build_scope=build_scope,
            total_build_time=0.0,
            configure_time=0.0,
            compile_time=0.0,
            link_time=0.0,
            test_time=0.0,
            package_time=0.0,
            peak_memory_mb=0.0,
            avg_cpu_percent=0.0,
            peak_cpu_percent=0.0,
            disk_io_read_mb=0.0,
            disk_io_write_mb=0.0,
            cache_hit_rate=0.0,
            cache_miss_count=0,
            cache_size_mb=0.0,
            build_status="unknown",
            test_passed=0,
            test_failed=0,
            test_skipped=0,
            artifact_count=0,
            artifact_size_mb=0.0,
            warnings_count=0,
            errors_count=0
        )
    
    def start_monitoring(self):
        """Start resource monitoring in background thread"""
        logger.info("🔍 Starting resource monitoring")
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitor_resources)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
    
    def stop_monitoring(self):
        """Stop resource monitoring"""
        logger.info("⏹️ Stopping resource monitoring")
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
    
    def _monitor_resources(self):
        """Monitor system resources during build"""
        process = psutil.Process()
        
        while self.monitoring_active:
            try:
                # Get current resource usage
                memory_info = process.memory_info()
                cpu_percent = process.cpu_percent()
                
                # Get disk I/O (if available)
                try:
                    io_counters = process.io_counters()
                    disk_read = io_counters.read_bytes / (1024 * 1024)  # MB
                    disk_write = io_counters.write_bytes / (1024 * 1024)  # MB
                except (AttributeError, psutil.AccessDenied):
                    disk_read = disk_write = 0
                
                sample = {
                    'timestamp': time.time(),
                    'memory_mb': memory_info.rss / (1024 * 1024),
                    'cpu_percent': cpu_percent,
                    'disk_read_mb': disk_read,
                    'disk_write_mb': disk_write
                }
                
                self.resource_samples.append(sample)
                
                # Update peak values
                self.metrics.peak_memory_mb = max(self.metrics.peak_memory_mb, sample['memory_mb'])
                self.metrics.peak_cpu_percent = max(self.metrics.peak_cpu_percent, sample['cpu_percent'])
                
                time.sleep(1)  # Sample every second
                
            except Exception as e:
                logger.warning(f"Error monitoring resources: {e}")
                time.sleep(5)  # Wait longer on error
    
    def start_phase(self, phase_name: str):
        """Start timing a build phase"""
        logger.info(f"📊 Starting phase: {phase_name}")
        self.phase_times[phase_name] = {'start': time.time()}
    
    def end_phase(self, phase_name: str):
        """End timing a build phase"""
        if phase_name in self.phase_times:
            end_time = time.time()
            start_time = self.phase_times[phase_name]['start']
            duration = end_time - start_time
            self.phase_times[phase_name]['duration'] = duration
            
            logger.info(f"✅ Phase {phase_name} completed in {duration:.2f}s")
            
            # Update metrics based on phase
            if phase_name == 'configure':
                self.metrics.configure_time = duration
            elif phase_name == 'compile':
                self.metrics.compile_time = duration
            elif phase_name == 'link':
                self.metrics.link_time = duration
            elif phase_name == 'test':
                self.metrics.test_time = duration
            elif phase_name == 'package':
                self.metrics.package_time = duration
    
    def record_cache_metrics(self, hit_rate: float, miss_count: int, cache_size_mb: float):
        """Record cache-related metrics"""
        logger.info(f"💾 Cache metrics - Hit rate: {hit_rate:.1%}, Misses: {miss_count}, Size: {cache_size_mb:.1f}MB")
        self.metrics.cache_hit_rate = hit_rate
        self.metrics.cache_miss_count = miss_count
        self.metrics.cache_size_mb = cache_size_mb
    
    def record_test_results(self, passed: int, failed: int, skipped: int):
        """Record test results"""
        logger.info(f"🧪 Test results - Passed: {passed}, Failed: {failed}, Skipped: {skipped}")
        self.metrics.test_passed = passed
        self.metrics.test_failed = failed
        self.metrics.test_skipped = skipped
    
    def record_build_status(self, status: str):
        """Record final build status"""
        logger.info(f"📋 Build status: {status}")
        self.metrics.build_status = status
    
    def record_artifacts(self, artifact_paths: List[str]):
        """Record information about build artifacts"""
        total_size = 0
        valid_artifacts = 0
        
        for path in artifact_paths:
            if Path(path).exists():
                size = Path(path).stat().st_size
                total_size += size
                valid_artifacts += 1
        
        self.metrics.artifact_count = valid_artifacts
        self.metrics.artifact_size_mb = total_size / (1024 * 1024)
        
        logger.info(f"📦 Artifacts - Count: {valid_artifacts}, Size: {self.metrics.artifact_size_mb:.1f}MB")
    
    def record_quality_metrics(self, warnings: int, errors: int):
        """Record code quality metrics"""
        logger.info(f"⚠️ Quality metrics - Warnings: {warnings}, Errors: {errors}")
        self.metrics.warnings_count = warnings
        self.metrics.errors_count = errors
    
    def finalize_metrics(self) -> BuildMetrics:
        """Finalize and return complete metrics"""
        logger.info("📊 Finalizing build metrics")
        
        # Calculate total build time
        self.metrics.total_build_time = time.time() - self.start_time
        
        # Calculate average CPU usage
        if self.resource_samples:
            cpu_values = [sample['cpu_percent'] for sample in self.resource_samples]
            self.metrics.avg_cpu_percent = sum(cpu_values) / len(cpu_values)
            
            # Get final disk I/O values
            if self.resource_samples:
                final_sample = self.resource_samples[-1]
                self.metrics.disk_io_read_mb = final_sample['disk_read_mb']
                self.metrics.disk_io_write_mb = final_sample['disk_write_mb']
        
        # Stop monitoring
        self.stop_monitoring()
        
        logger.info(f"✅ Metrics finalized - Total time: {self.metrics.total_build_time:.2f}s")
        return self.metrics
    
    def save_metrics(self, output_path: str):
        """Save metrics to file"""
        metrics_dict = self.metrics.to_dict()
        
        # Add detailed resource samples if requested
        metrics_dict['resource_samples'] = self.resource_samples
        metrics_dict['phase_times'] = self.phase_times
        
        with open(output_path, 'w') as f:
            json.dump(metrics_dict, f, indent=2)
        
        logger.info(f"💾 Metrics saved to: {output_path}")
    
    def generate_summary_report(self) -> str:
        """Generate human-readable summary report"""
        report = f"""
📊 Build Metrics Summary
========================

Build Information:
- Build ID: {self.metrics.build_id}
- Source: {self.metrics.source_repo}@{self.metrics.source_sha[:8]}
- Platform: {self.metrics.platform}
- Profile: {self.metrics.profile}
- Scope: {self.metrics.build_scope}
- Status: {self.metrics.build_status}

Performance:
- Total Time: {self.metrics.total_build_time:.2f}s
- Configure: {self.metrics.configure_time:.2f}s
- Compile: {self.metrics.compile_time:.2f}s
- Link: {self.metrics.link_time:.2f}s
- Test: {self.metrics.test_time:.2f}s
- Package: {self.metrics.package_time:.2f}s

Resources:
- Peak Memory: {self.metrics.peak_memory_mb:.1f}MB
- Avg CPU: {self.metrics.avg_cpu_percent:.1f}%
- Peak CPU: {self.metrics.peak_cpu_percent:.1f}%
- Disk Read: {self.metrics.disk_io_read_mb:.1f}MB
- Disk Write: {self.metrics.disk_io_write_mb:.1f}MB

Cache:
- Hit Rate: {self.metrics.cache_hit_rate:.1%}
- Misses: {self.metrics.cache_miss_count}
- Size: {self.metrics.cache_size_mb:.1f}MB

Tests:
- Passed: {self.metrics.test_passed}
- Failed: {self.metrics.test_failed}
- Skipped: {self.metrics.test_skipped}

Artifacts:
- Count: {self.metrics.artifact_count}
- Size: {self.metrics.artifact_size_mb:.1f}MB

Quality:
- Warnings: {self.metrics.warnings_count}
- Errors: {self.metrics.errors_count}
"""
        return report


class MetricsAnalyzer:
    """Analyzes build metrics and provides insights"""
    
    @staticmethod
    def analyze_performance(metrics: BuildMetrics) -> Dict[str, Any]:
        """Analyze performance metrics and provide insights"""
        analysis = {
            "performance_score": 0,
            "bottlenecks": [],
            "recommendations": [],
            "comparisons": {}
        }
        
        # Analyze build time distribution
        total_time = metrics.total_build_time
        if total_time > 0:
            compile_ratio = metrics.compile_time / total_time
            test_ratio = metrics.test_time / total_time
            
            if compile_ratio > 0.7:
                analysis["bottlenecks"].append("Compilation time is high")
                analysis["recommendations"].append("Consider enabling more parallelization")
            
            if test_ratio > 0.3:
                analysis["bottlenecks"].append("Test time is high")
                analysis["recommendations"].append("Consider optimizing test suite")
        
        # Analyze resource usage
        if metrics.peak_memory_mb > 8000:  # 8GB
            analysis["bottlenecks"].append("High memory usage")
            analysis["recommendations"].append("Consider reducing parallel jobs")
        
        if metrics.cache_hit_rate < 0.7:
            analysis["bottlenecks"].append("Low cache hit rate")
            analysis["recommendations"].append("Improve cache warming strategy")
        
        # Calculate performance score (0-100)
        score = 100
        if metrics.total_build_time > 600:  # 10 minutes
            score -= 20
        if metrics.cache_hit_rate < 0.8:
            score -= 15
        if metrics.peak_memory_mb > 4000:  # 4GB
            score -= 10
        
        analysis["performance_score"] = max(0, score)
        
        return analysis
    
    @staticmethod
    def compare_metrics(current: BuildMetrics, baseline: BuildMetrics) -> Dict[str, Any]:
        """Compare current metrics with baseline"""
        comparison = {
            "improvements": [],
            "regressions": [],
            "changes": {}
        }
        
        # Compare build times
        time_change = current.total_build_time - baseline.total_build_time
        time_change_percent = (time_change / baseline.total_build_time) * 100
        
        comparison["changes"]["build_time"] = {
            "absolute": time_change,
            "percent": time_change_percent
        }
        
        if time_change_percent < -5:  # 5% improvement
            comparison["improvements"].append(f"Build time improved by {abs(time_change_percent):.1f}%")
        elif time_change_percent > 5:  # 5% regression
            comparison["regressions"].append(f"Build time regressed by {time_change_percent:.1f}%")
        
        # Compare cache hit rates
        cache_change = current.cache_hit_rate - baseline.cache_hit_rate
        if cache_change > 0.05:  # 5% improvement
            comparison["improvements"].append(f"Cache hit rate improved by {cache_change:.1%}")
        elif cache_change < -0.05:  # 5% regression
            comparison["regressions"].append(f"Cache hit rate regressed by {abs(cache_change):.1%}")
        
        return comparison


def main():
    """Main entry point for metrics collection"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Build Metrics Collector")
    parser.add_argument("--build-id", required=True, help="Build ID")
    parser.add_argument("--source-repo", required=True, help="Source repository")
    parser.add_argument("--source-sha", required=True, help="Source SHA")
    parser.add_argument("--platform", required=True, help="Build platform")
    parser.add_argument("--profile", required=True, help="Build profile")
    parser.add_argument("--build-scope", required=True, help="Build scope")
    parser.add_argument("--output", required=True, help="Output file for metrics")
    
    args = parser.parse_args()
    
    # Create metrics collector
    collector = MetricsCollector(
        build_id=args.build_id,
        source_repo=args.source_repo,
        source_sha=args.source_sha,
        platform=args.platform,
        profile=args.profile,
        build_scope=args.build_scope
    )
    
    # Start monitoring
    collector.start_monitoring()
    
    try:
        # Simulate build phases (in real usage, this would be called by build system)
        collector.start_phase("configure")
        time.sleep(2)  # Simulate configure time
        collector.end_phase("configure")
        
        collector.start_phase("compile")
        time.sleep(5)  # Simulate compile time
        collector.end_phase("compile")
        
        collector.start_phase("test")
        time.sleep(3)  # Simulate test time
        collector.end_phase("test")
        
        # Record some example metrics
        collector.record_cache_metrics(hit_rate=0.85, miss_count=25, cache_size_mb=1500)
        collector.record_test_results(passed=1250, failed=2, skipped=15)
        collector.record_build_status("success")
        collector.record_artifacts(["libssl.so", "libcrypto.so"])
        collector.record_quality_metrics(warnings=5, errors=0)
        
    finally:
        # Finalize and save metrics
        metrics = collector.finalize_metrics()
        collector.save_metrics(args.output)
        
        # Print summary
        print(collector.generate_summary_report())


if __name__ == "__main__":
    main()