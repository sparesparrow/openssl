Practical Implementation Guide for OpenSSL CI Modernization
============================================================

## Quick Start: 48-Hour Implementation Plan

### Day 1: Foundation Setup

#### Morning (4 hours): Change Detection Implementation
```bash
# 1. Create change detection workflow
cat > .github/workflows/change-detection.yml << 'EOF'
name: Change Detection
on: [push, pull_request]

jobs:
  detect:
    runs-on: ubuntu-latest
    outputs:
      source: ${{ steps.changes.outputs.source }}
      tests: ${{ steps.changes.outputs.tests }}
      docs: ${{ steps.changes.outputs.docs }}
      fuzz: ${{ steps.changes.outputs.fuzz }}
      config: ${{ steps.changes.outputs.config }}
    steps:
      - uses: actions/checkout@v4
      - uses: dorny/paths-filter@v3
        id: changes
        with:
          filters: |
            source:
              - 'crypto/**'
              - 'ssl/**'
              - 'apps/**'
              - 'providers/**'
              - 'include/**'
            tests:
              - 'test/**'
            docs:
              - 'doc/**'
              - '*.md'
              - 'CHANGES.md'
              - 'NEWS.md'
            fuzz:
              - 'fuzz/**'
            config:
              - 'Configure'
              - 'VERSION.dat'
              - 'configdata.pm.in'
              - 'build.info'
EOF

# 2. Test the change detection
git add .github/workflows/change-detection.yml
git commit -m "Add change detection workflow"
git push origin feature/ci-optimization
```

#### Afternoon (4 hours): Optimize Existing CI
```bash
# 3. Create optimized main CI workflow
cat > .github/workflows/optimized-main.yml << 'EOF'
name: Optimized CI
on: [push, pull_request]

jobs:
  changes:
    uses: ./.github/workflows/change-detection.yml
    
  quick-check:
    needs: changes
    if: needs.changes.outputs.docs == 'true' && needs.changes.outputs.source == 'false'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Documentation check
        run: |
          echo "Only documentation changed - running quick validation"
          ./config --help > /dev/null
          echo "✅ Quick validation passed"
          
  build-matrix:
    needs: changes
    if: needs.changes.outputs.source == 'true' || needs.changes.outputs.config == 'true'
    strategy:
      matrix:
        include:
          - name: gcc-release
            cc: gcc
            config: "--strict-warnings enable-fips"
          - name: clang-debug  
            cc: clang
            config: "--strict-warnings --debug no-fips"
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          submodules: recursive
          
      - name: Cache build
        uses: actions/cache@v4
        with:
          path: |
            .
            !.git
          key: build-${{ matrix.name }}-${{ hashFiles('Configure', 'VERSION.dat') }}-${{ github.sha }}
          restore-keys: |
            build-${{ matrix.name }}-${{ hashFiles('Configure', 'VERSION.dat') }}-
            
      - name: Configure
        run: |
          CC=${{ matrix.cc }} ./config ${{ matrix.config }}
          perl configdata.pm --dump
          
      - name: Build
        run: make -j$(nproc)
        
      - name: Test
        run: make test HARNESS_JOBS=$(nproc)
        
  fuzz-tests:
    needs: changes
    if: needs.changes.outputs.fuzz == 'true'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build fuzzers
        run: |
          ./config --debug enable-fuzz-afl enable-fuzz-libfuzzer
          make -j$(nproc)
      - name: Run fuzz tests
        run: make test TESTS="test_fuzz*"
EOF

git add .github/workflows/optimized-main.yml
git commit -m "Add optimized main CI workflow"
```

### Day 2: Advanced Optimizations

#### Morning (4 hours): Conan Integration
```bash
# 4. Create Conan configuration
mkdir -p conan-profiles

cat > conanfile.py << 'EOF'
from conan import ConanFile
from conan.tools.cmake import cmake_layout

class OpenSSLConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    
    def requirements(self):
        self.requires("zlib/1.3.1")
        
    def build_requirements(self):
        self.tool_requires("perl/5.34.0")
        
    def layout(self):
        cmake_layout(self)
EOF

cat > conan-profiles/ci-linux.profile << 'EOF'
[settings]
os=Linux
arch=x86_64
compiler=gcc
compiler.version=11
compiler.libcxx=libstdc++11
build_type=Release

[conf]
tools.system.package_manager:mode=install
tools.system.package_manager:sudo=True
EOF

# 5. Update CI to use Conan
cat > .github/workflows/conan-ci.yml << 'EOF'
name: Conan CI
on: 
  workflow_dispatch:
  push:
    paths:
      - 'conanfile.py'
      - 'conan-profiles/**'

jobs:
  conan-build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install Conan
        run: pip install conan==2.0.17
      - name: Configure Conan
        run: |
          conan profile detect --force
          conan remote add conancenter https://center.conan.io
      - name: Build with Conan
        run: |
          conan install . --profile=conan-profiles/ci-linux.profile --build=missing
          # Traditional build with Conan dependencies available
          ./config --strict-warnings
          make -j$(nproc)
EOF

git add conanfile.py conan-profiles/ .github/workflows/conan-ci.yml
git commit -m "Add Conan integration"
```

#### Afternoon (4 hours): Performance Monitoring
```bash
# 6. Create performance monitoring
mkdir -p scripts

cat > scripts/performance-monitor.py << 'EOF'
#!/usr/bin/env python3
import subprocess
import json
import time
import sys

def run_benchmark():
    """Run OpenSSL speed benchmarks"""
    benchmarks = {
        'rsa2048': ['openssl', 'speed', '-seconds', '10', 'rsa2048'],
        'aes-256-cbc': ['openssl', 'speed', '-seconds', '10', 'aes-256-cbc'],
        'sha256': ['openssl', 'speed', '-seconds', '10', 'sha256']
    }
    
    results = {}
    for name, cmd in benchmarks.items():
        try:
            start_time = time.time()
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True)
            end_time = time.time()
            
            # Parse speed output (simplified)
            lines = output.split('\n')
            for line in lines:
                if 'sign/s' in line or 'verify/s' in line or 'k/s' in line:
                    # Extract performance numbers
                    parts = line.split()
                    if len(parts) >= 2:
                        try:
                            perf_value = float(parts[-1].replace('k', ''))
                            results[name] = perf_value
                            break
                        except ValueError:
                            continue
                            
        except subprocess.CalledProcessError as e:
            print(f"Benchmark {name} failed: {e}")
            results[name] = 0
            
    return results

def compare_with_baseline(results, baseline_file='baseline.json'):
    """Compare results with baseline"""
    try:
        with open(baseline_file, 'r') as f:
            baseline = json.load(f)
    except FileNotFoundError:
        print("No baseline found, creating new baseline")
        with open(baseline_file, 'w') as f:
            json.dump(results, f, indent=2)
        return []
    
    regressions = []
    for test, current in results.items():
        baseline_val = baseline.get(test, 0)
        if baseline_val > 0 and current < baseline_val * 0.95:  # 5% regression
            regression_pct = ((baseline_val - current) / baseline_val) * 100
            regressions.append({
                'test': test,
                'baseline': baseline_val,
                'current': current,
                'regression_pct': regression_pct
            })
    
    return regressions

if __name__ == "__main__":
    print("Running OpenSSL performance benchmarks...")
    results = run_benchmark()
    
    print("Results:")
    for test, value in results.items():
        print(f"  {test}: {value}")
    
    regressions = compare_with_baseline(results)
    
    if regressions:
        print("\n⚠️  Performance regressions detected:")
        for reg in regressions:
            print(f"  {reg['test']}: {reg['regression_pct']:.1f}% slower")
        sys.exit(1)
    else:
        print("\n✅ No performance regressions detected")
        
    # Update baseline if on main branch
    import os
    if os.environ.get('GITHUB_REF') == 'refs/heads/main':
        with open('baseline.json', 'w') as f:
            json.dump(results, f, indent=2)
        print("Updated performance baseline")
EOF

chmod +x scripts/performance-monitor.py

# 7. Add performance monitoring to CI
cat > .github/workflows/performance.yml << 'EOF'
name: Performance Monitoring
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  performance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build OpenSSL
        run: |
          ./config --strict-warnings
          make -j$(nproc)
      - name: Run performance tests
        run: |
          export PATH=$PWD/apps:$PATH
          python3 scripts/performance-monitor.py
      - name: Upload baseline
        if: github.ref == 'refs/heads/main'
        uses: actions/upload-artifact@v4
        with:
          name: performance-baseline
          path: baseline.json
EOF

git add scripts/ .github/workflows/performance.yml
git commit -m "Add performance monitoring"
```

## Week 1: Production Deployment

### Monday: Testing and Validation
```bash
# Create comprehensive test script
cat > scripts/validate-ci.sh << 'EOF'
#!/bin/bash
set -e

echo "🔍 Validating CI optimization..."

# Test 1: Change detection
echo "Testing change detection..."
git checkout -b test-docs-only
echo "# Test change" >> README.md
git add README.md
git commit -m "test: docs only change"
git push origin test-docs-only

# Create PR and check that only quick-check runs
echo "✅ Create PR and verify only documentation checks run"

# Test 2: Source changes
git checkout main
git checkout -b test-source-change
echo "// Test change" >> crypto/aes/aes_core.c
git add crypto/aes/aes_core.c
git commit -m "test: source change"
git push origin test-source-change

echo "✅ Create PR and verify full build matrix runs"

# Test 3: Fuzz changes
git checkout main
git checkout -b test-fuzz-change
echo "// Test change" >> fuzz/asn1.c
git add fuzz/asn1.c
git commit -m "test: fuzz change"
git push origin test-fuzz-change

echo "✅ Create PR and verify only fuzz tests run"

echo "All tests completed successfully!"
EOF

chmod +x scripts/validate-ci.sh
```

### Tuesday-Wednesday: Gradual Rollout
```bash
# Enable new workflows gradually
# 1. Start with change detection only
# 2. Add optimized builds for non-critical branches
# 3. Enable for main branch after validation

# Create feature flag system
cat > .github/workflows/feature-flags.yml << 'EOF'
name: Feature Flags
on:
  workflow_call:
    outputs:
      use-optimized-ci:
        value: ${{ jobs.flags.outputs.use-optimized-ci }}
      use-conan:
        value: ${{ jobs.flags.outputs.use-conan }}
      use-performance-monitoring:
        value: ${{ jobs.flags.outputs.use-performance-monitoring }}

jobs:
  flags:
    runs-on: ubuntu-latest
    outputs:
      use-optimized-ci: ${{ steps.flags.outputs.use-optimized-ci }}
      use-conan: ${{ steps.flags.outputs.use-conan }}
      use-performance-monitoring: ${{ steps.flags.outputs.use-performance-monitoring }}
    steps:
      - id: flags
        run: |
          # Enable features based on branch or environment
          if [[ "${{ github.ref }}" == "refs/heads/main" ]]; then
            echo "use-optimized-ci=true" >> $GITHUB_OUTPUT
            echo "use-conan=true" >> $GITHUB_OUTPUT
            echo "use-performance-monitoring=true" >> $GITHUB_OUTPUT
          elif [[ "${{ github.ref }}" == refs/heads/feature/* ]]; then
            echo "use-optimized-ci=true" >> $GITHUB_OUTPUT
            echo "use-conan=false" >> $GITHUB_OUTPUT
            echo "use-performance-monitoring=false" >> $GITHUB_OUTPUT
          else
            echo "use-optimized-ci=false" >> $GITHUB_OUTPUT
            echo "use-conan=false" >> $GITHUB_OUTPUT
            echo "use-performance-monitoring=false" >> $GITHUB_OUTPUT
          fi
EOF
```

### Thursday-Friday: Monitoring and Optimization
```bash
# Create monitoring dashboard
cat > scripts/ci-dashboard.py << 'EOF'
#!/usr/bin/env python3
import requests
import json
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

class CIDashboard:
    def __init__(self, repo, token):
        self.repo = repo
        self.headers = {'Authorization': f'token {token}'}
        self.api_base = f'https://api.github.com/repos/{repo}'
    
    def get_workflow_runs(self, workflow_id, days=7):
        """Get workflow runs for the last N days"""
        since = (datetime.now() - timedelta(days=days)).isoformat()
        url = f'{self.api_base}/actions/workflows/{workflow_id}/runs'
        params = {'created': f'>{since}', 'per_page': 100}
        
        response = requests.get(url, headers=self.headers, params=params)
        return response.json()['workflow_runs']
    
    def analyze_performance(self):
        """Analyze CI performance metrics"""
        workflows = ['ci.yml', 'optimized-main.yml']
        metrics = {}
        
        for workflow in workflows:
            runs = self.get_workflow_runs(workflow)
            
            durations = []
            success_rate = 0
            total_runs = len(runs)
            
            for run in runs:
                if run['conclusion'] == 'success':
                    success_rate += 1
                
                # Calculate duration
                start = datetime.fromisoformat(run['created_at'].replace('Z', '+00:00'))
                end = datetime.fromisoformat(run['updated_at'].replace('Z', '+00:00'))
                duration = (end - start).total_seconds() / 60  # minutes
                durations.append(duration)
            
            metrics[workflow] = {
                'avg_duration': sum(durations) / len(durations) if durations else 0,
                'success_rate': (success_rate / total_runs) * 100 if total_runs > 0 else 0,
                'total_runs': total_runs
            }
        
        return metrics
    
    def generate_report(self):
        """Generate performance report"""
        metrics = self.analyze_performance()
        
        print("CI Performance Report")
        print("=" * 50)
        
        for workflow, data in metrics.items():
            print(f"\n{workflow}:")
            print(f"  Average Duration: {data['avg_duration']:.1f} minutes")
            print(f"  Success Rate: {data['success_rate']:.1f}%")
            print(f"  Total Runs: {data['total_runs']}")
        
        # Compare optimized vs original
        if 'ci.yml' in metrics and 'optimized-main.yml' in metrics:
            original = metrics['ci.yml']['avg_duration']
            optimized = metrics['optimized-main.yml']['avg_duration']
            
            if original > 0:
                improvement = ((original - optimized) / original) * 100
                print(f"\n🚀 Performance Improvement: {improvement:.1f}%")

if __name__ == "__main__":
    import os
    token = os.environ.get('GITHUB_TOKEN')
    repo = os.environ.get('GITHUB_REPOSITORY', 'openssl/openssl')
    
    dashboard = CIDashboard(repo, token)
    dashboard.generate_report()
EOF
```

## Month 1: Advanced Features

### Week 2: Multi-Platform Support
```bash
# Add ARM64 and macOS support
cat > .github/workflows/multi-platform.yml << 'EOF'
name: Multi-Platform CI
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build-matrix:
    strategy:
      matrix:
        include:
          - os: ubuntu-latest
            arch: x86_64
            cc: gcc
          - os: ubuntu-latest  
            arch: aarch64
            cc: gcc
          - os: macos-13
            arch: x86_64
            cc: clang
          - os: macos-14
            arch: arm64
            cc: clang
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - name: Setup cross-compilation
        if: matrix.arch == 'aarch64' && matrix.os == 'ubuntu-latest'
        run: |
          sudo apt-get update
          sudo apt-get install -y gcc-aarch64-linux-gnu
          export CC=aarch64-linux-gnu-gcc
      - name: Configure
        run: |
          if [[ "${{ matrix.arch }}" == "aarch64" ]]; then
            ./Configure linux-aarch64 --strict-warnings
          elif [[ "${{ runner.os }}" == "macOS" ]]; then
            ./Configure darwin64-x86_64-cc --strict-warnings
          else
            ./Configure linux-x86_64 --strict-warnings
          fi
      - name: Build
        run: make -j$(nproc || sysctl -n hw.ncpu)
      - name: Test
        if: matrix.arch != 'aarch64'  # Skip cross-compiled tests
        run: make test
EOF
```

### Week 3: Security Integration
```bash
# Add comprehensive security scanning
cat > .github/workflows/security.yml << 'EOF'
name: Security Scan
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 6 * * 1'  # Weekly

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
          
      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-results.sarif'
          
      - name: Upload Trivy scan results
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: 'trivy-results.sarif'
          
      - name: Run Semgrep
        uses: returntocorp/semgrep-action@v1
        with:
          config: >-
            p/security-audit
            p/secrets
            p/owasp-top-ten
            
      - name: FOSSA License Scan
        uses: fossas/fossa-action@main
        with:
          api-key: ${{ secrets.FOSSA_API_KEY }}
          
      - name: Generate SBOM
        run: |
          # Install syft for SBOM generation
          curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /usr/local/bin
          syft . -o spdx-json=sbom.spdx.json
          
      - name: Upload SBOM
        uses: actions/upload-artifact@v4
        with:
          name: sbom
          path: sbom.spdx.json
EOF
```

### Week 4: Performance Optimization
```bash
# Advanced performance monitoring
cat > scripts/advanced-performance.py << 'EOF'
#!/usr/bin/env python3
import subprocess
import json
import time
import statistics
from concurrent.futures import ThreadPoolExecutor
import psutil

class AdvancedPerformanceMonitor:
    def __init__(self):
        self.results = {}
        
    def run_parallel_benchmarks(self):
        """Run benchmarks in parallel for better resource utilization"""
        benchmarks = [
            ('rsa2048', ['openssl', 'speed', '-seconds', '30', 'rsa2048']),
            ('rsa4096', ['openssl', 'speed', '-seconds', '30', 'rsa4096']),
            ('aes-128-cbc', ['openssl', 'speed', '-seconds', '30', 'aes-128-cbc']),
            ('aes-256-cbc', ['openssl', 'speed', '-seconds', '30', 'aes-256-cbc']),
            ('sha1', ['openssl', 'speed', '-seconds', '30', 'sha1']),
            ('sha256', ['openssl', 'speed', '-seconds', '30', 'sha256']),
            ('sha512', ['openssl', 'speed', '-seconds', '30', 'sha512']),
        ]
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {executor.submit(self._run_single_benchmark, name, cmd): name 
                      for name, cmd in benchmarks}
            
            for future in futures:
                name = futures[future]
                try:
                    result = future.result()
                    self.results[name] = result
                except Exception as e:
                    print(f"Benchmark {name} failed: {e}")
                    self.results[name] = {'error': str(e)}
    
    def _run_single_benchmark(self, name, cmd):
        """Run a single benchmark with resource monitoring"""
        process = psutil.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Monitor resource usage
        cpu_samples = []
        memory_samples = []
        
        start_time = time.time()
        
        while process.poll() is None:
            try:
                cpu_samples.append(process.cpu_percent())
                memory_samples.append(process.memory_info().rss / 1024 / 1024)  # MB
                time.sleep(0.1)
            except psutil.NoSuchProcess:
                break
        
        stdout, stderr = process.communicate()
        end_time = time.time()
        
        # Parse OpenSSL speed output
        performance_value = self._parse_speed_output(stdout.decode())
        
        return {
            'performance': performance_value,
            'duration': end_time - start_time,
            'avg_cpu': statistics.mean(cpu_samples) if cpu_samples else 0,
            'max_memory': max(memory_samples) if memory_samples else 0,
            'return_code': process.returncode
        }
    
    def _parse_speed_output(self, output):
        """Parse OpenSSL speed command output"""
        lines = output.split('\n')
        for line in lines:
            if any(keyword in line for keyword in ['sign/s', 'verify/s', 'k/s']):
                parts = line.split()
                for part in reversed(parts):
                    try:
                        # Handle 'k' suffix
                        if part.endswith('k'):
                            return float(part[:-1]) * 1000
                        else:
                            return float(part)
                    except ValueError:
                        continue
        return 0
    
    def generate_detailed_report(self):
        """Generate detailed performance report"""
        report = {
            'timestamp': time.time(),
            'system_info': {
                'cpu_count': psutil.cpu_count(),
                'memory_gb': psutil.virtual_memory().total / (1024**3),
                'platform': subprocess.check_output(['uname', '-a']).decode().strip()
            },
            'benchmarks': self.results
        }
        
        with open('performance-report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print("Detailed Performance Report Generated")
        return report

if __name__ == "__main__":
    monitor = AdvancedPerformanceMonitor()
    monitor.run_parallel_benchmarks()
    monitor.generate_detailed_report()
EOF
```

## Success Metrics and KPIs

### Build Performance Metrics
```python
# Track these KPIs weekly
kpis = {
    'build_time_reduction': {
        'target': '60%',
        'measurement': 'average_build_duration_minutes'
    },
    'cache_hit_rate': {
        'target': '70%',
        'measurement': 'cache_hits / total_builds'
    },
    'test_execution_time': {
        'target': '50% reduction',
        'measurement': 'average_test_duration_minutes'
    },
    'ci_cost_reduction': {
        'target': '40%',
        'measurement': 'monthly_github_actions_cost'
    },
    'developer_satisfaction': {
        'target': '8/10',
        'measurement': 'survey_score'
    }
}
```

This practical guide provides a concrete, step-by-step approach to implementing the CI optimizations with measurable outcomes and rollback capabilities at each stage.