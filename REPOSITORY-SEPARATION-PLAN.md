# OpenSSL Repository Separation Plan

## Cíl
Separovat build orchestraci, skripty pro matrix/status/metrics a warm-up do `openssl-tools`, zatímco `openssl` repo bude obsahovat pouze `conanfile.py`, minimální profily a trigger workflow.

## Struktura po separaci

### OpenSSL Repository (minimální)
```
openssl/
├── conanfile.py                    # Hlavní Conan recipe (zjednodušený)
├── conan/
│   ├── default.profile            # Základní profil
│   └── ci-minimal.yml             # Minimální CI konfigurace
├── .github/workflows/
│   ├── trigger-tools.yml          # Trigger pro openssl-tools (zachovat)
│   ├── basic-validation.yml       # Základní syntax/lint checks
│   └── templates/
│       └── standard-setup.yml     # Základní setup template
├── VERSION.dat
├── Configure
├── config
├── [všechny OpenSSL source soubory - apps/, crypto/, ssl/, include/, atd.]
└── README.md                      # Aktualizovaný s odkazy na tools
```

### OpenSSL-Tools Repository (orchestrace)
```
openssl-tools/
├── scripts/
│   ├── orchestration/
│   │   ├── build_matrix_manager.py      # Z openssl/scripts/conan/
│   │   ├── conan_orchestrator.py        # Z openssl/scripts/conan/
│   │   ├── dependency_manager.py        # Z openssl/scripts/conan/
│   │   └── performance_benchmark.py     # Z openssl/scripts/conan/
│   ├── ci/
│   │   ├── conan_automation.py          # Z openssl/scripts/ci/
│   │   ├── performance_tests.py         # Z openssl/scripts/ci/
│   │   ├── test_harness.py              # Z openssl/scripts/ci/
│   │   └── deploy.py                    # Z openssl/scripts/ci/
│   ├── validation/
│   │   ├── pre-build-validation.py      # Z openssl/scripts/validation/
│   │   ├── cache-optimization.py        # Z openssl/scripts/validation/
│   │   ├── secure-key-manager.py        # Z openssl/scripts/validation/
│   │   └── artifact-lifecycle-manager.py # Z openssl/scripts/validation/
│   ├── metrics/
│   │   ├── build_metrics_collector.py   # Nový
│   │   ├── status_reporter.py           # Nový
│   │   └── performance_analyzer.py      # Nový
│   └── warm-up/
│       ├── cache_warmer.py              # Nový
│       ├── dependency_preloader.py      # Nový
│       └── environment_preparer.py      # Nový
├── profiles/
│   ├── production/                      # Z openssl/conan-profiles/
│   ├── development/                     # Z openssl/conan-dev/
│   ├── testing/                         # Nové profily
│   └── specialized/                     # FIPS, sanitizers, atd.
├── configs/
│   ├── ci-matrix.yml                    # Build matrix konfigurace
│   ├── platform-configs.yml            # Platform-specific nastavení
│   ├── artifact-lifecycle.yml          # Z openssl/conan-dev/
│   └── cache-optimization.yml          # Z openssl/conan-dev/
├── .github/workflows/
│   ├── openssl-ci-dispatcher.yml       # Hlavní orchestrace (už existuje)
│   ├── matrix-builds.yml               # Matrix build workflows
│   ├── performance-tests.yml           # Performance testing
│   ├── security-scans.yml              # Security scanning
│   ├── artifact-management.yml         # Artifact lifecycle
│   └── warm-up-caches.yml              # Cache warming
├── templates/
│   ├── conanfile-variants/             # Různé varianty conanfile.py
│   ├── profile-templates/              # Template profily
│   └── workflow-templates/             # GitHub Actions templates
└── docs/
    ├── BUILD-ORCHESTRATION.md
    ├── MATRIX-CONFIGURATION.md
    └── PERFORMANCE-OPTIMIZATION.md
```

## Migrace kroky

### Fáze 1: Příprava openssl-tools
1. **Rozšířit openssl-tools strukturu**
   - Vytvořit adresářovou strukturu
   - Přesunout skripty z openssl/scripts/
   - Přesunout profily z openssl/conan-dev/ a conan-profiles/
   - Přesunout pokročilé workflow soubory

2. **Aktualizovat orchestraci**
   - Rozšířit build_matrix_generator.py
   - Implementovat metrics collection
   - Přidat warm-up mechanismy

### Fáze 2: Zjednodušení openssl
1. **Zjednodušit conanfile.py**
   - Odstranit komplexní orchestraci
   - Zachovat pouze základní build logiku
   - Přidat odkazy na openssl-tools

2. **Minimalizovat workflows**
   - Zachovat pouze trigger-tools.yml
   - Přidat basic-validation.yml pro rychlé checks
   - Odstranit komplexní CI workflows

3. **Vyčistit adresáře**
   - Odstranit scripts/ (kromě základních)
   - Odstranit conan-dev/, conan-profiles/
   - Odstranit pokročilé konfigurace

### Fáze 3: Integrace a testování
1. **Aktualizovat trigger mechanismus**
   - Upravit trigger-tools.yml pro novou strukturu
   - Testovat dispatch do openssl-tools

2. **Validace funkčnosti**
   - Otestovat build matrix generování
   - Ověřit metrics collection
   - Validovat artifact management

## Výhody separace

### Pro OpenSSL repository
- **Čistší struktura** - fokus na OpenSSL source code
- **Rychlejší klonování** - menší repository
- **Jednodušší maintenance** - méně CI komplexity
- **Lepší přehlednost** - jasné oddělení concerns

### Pro OpenSSL-Tools repository
- **Specializovaná orchestrace** - dedikovaný prostor pro build automation
- **Flexibilní profily** - rozšířené možnosti konfigurace
- **Pokročilé metriky** - comprehensive monitoring
- **Optimalizované caching** - inteligentní warm-up strategie

### Pro vývojáře
- **Jasné oddělení** - source code vs. build tooling
- **Modulární přístup** - možnost použít tools i pro jiné projekty
- **Lepší testování** - izolované testování build logiky
- **Snadnější příspěvky** - menší cognitive load

## Implementační detaily

### Zjednodušený conanfile.py
```python
class OpenSSLConan(ConanFile):
    name = "openssl"
    version = None  # Z VERSION.dat
    
    # Základní options (zjednodušené)
    options = {
        "shared": [True, False],
        "fips": [True, False],
        # ... pouze nejdůležitější options
    }
    
    def build(self):
        # Základní build logika
        # Komplexní orchestrace v openssl-tools
        pass
```

### Trigger workflow (aktualizovaný)
```yaml
name: Trigger OpenSSL Tools CI
on:
  pull_request:
    paths: ['*.c', '*.h', 'conanfile.py', 'VERSION.dat', ...]
  push:
    branches: [main, master]

jobs:
  trigger-tools-ci:
    runs-on: ubuntu-latest
    steps:
      - name: Dispatch to openssl-tools
        uses: peter-evans/repository-dispatch@v3
        with:
          repository: sparesparrow/openssl-tools
          event-type: openssl-build-triggered
          client-payload: ${{ steps.context.outputs.context }}
```

### Build Matrix v openssl-tools
```python
def generate_build_matrix(source_repo, source_sha, build_scope, changes):
    """Generuje build matrix na základě změn v openssl repo"""
    matrix = {
        "include": []
    }
    
    if build_scope == "full":
        # Plná matrix pro core změny
        matrix["include"].extend(get_full_matrix())
    elif build_scope == "test":
        # Test-focused matrix
        matrix["include"].extend(get_test_matrix())
    
    return matrix
```

## Timeline

### Týden 1-2: Příprava
- Vytvoření rozšířené struktury openssl-tools
- Migrace skriptů a profilů
- Testování v izolaci

### Týden 3: Integrace
- Aktualizace trigger mechanismu
- Testování end-to-end workflow
- Dokumentace změn

### Týden 4: Cleanup
- Vyčištění openssl repository
- Finální testování
- Deployment do produkce

## Rizika a mitigace

### Riziko: Ztráta funkčnosti
**Mitigace:** Postupná migrace s paralelním testováním

### Riziko: Komplexní debugging
**Mitigace:** Comprehensive logging a monitoring

### Riziko: Dependency hell
**Mitigace:** Jasné versioning a compatibility matrix

## Závěr

Tato separace vytvoří čistší architekturu s jasným oddělením concerns:
- `openssl` = source code + minimální build setup
- `openssl-tools` = build orchestrace + advanced tooling

Výsledkem bude maintainable, scalable a efficient build systém.