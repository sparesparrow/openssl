# OpenSSL Repository Separation Plan - Final Architecture

## Overview
This document outlines the completed separation of build orchestration and advanced tooling into the `openssl-tools` repository to simplify the `openssl` repository and improve build system maintainability.

## Final Architecture

### OpenSSL Repository (Minimal & Focused)
```
openssl/
├── conanfile.py                    # Main Conan recipe (production)
├── conanfile-minimal.py           # Minimal Conan recipe (optional)
├── conan/
│   ├── default.profile            # Basic profile
│   └── ci-minimal.yml             # Minimal CI configuration
├── .github/workflows/
│   ├── trigger-tools.yml          # Trigger for openssl-tools
│   └── basic-validation.yml       # Basic validation workflow
├── VERSION.dat                     # OpenSSL version
├── Configure                       # OpenSSL configure script
├── config                         # OpenSSL config
└── [OpenSSL source code]          # Core OpenSSL implementation
```

### OpenSSL-Tools Repository (Build Orchestration)
```
openssl-tools/
├── scripts/
│   ├── orchestration/              # Build orchestration
│   ├── ci/                         # CI/CD automation
│   ├── validation/                 # Advanced validation
│   ├── metrics/                    # Build metrics collection
│   └── warm-up/                    # Cache warming
├── profiles/                       # Advanced Conan profiles
├── configs/                        # Configuration management
├── .github/workflows/              # Advanced CI workflows
└── docs/                          # Detailed documentation
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