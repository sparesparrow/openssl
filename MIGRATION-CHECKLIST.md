# OpenSSL Repository Separation - Migration Checklist

## Fáze 1: Příprava (✅ Dokončeno)

### OpenSSL Repository - Minimalizace
- [x] Vytvořit zjednodušený `conanfile-minimal.py`
- [x] Vytvořit základní profil `conan/default.profile`
- [x] Vytvořit minimální CI konfiguraci `conan/ci-minimal.yml`
- [x] Vytvořit `basic-validation.yml` workflow
- [x] Aktualizovat `trigger-tools.yml` workflow

### OpenSSL-Tools Repository - Rozšíření
- [x] Vytvořit strukturu adresářů
- [x] Implementovat `build_orchestrator.py`
- [x] Implementovat `build_metrics_collector.py`
- [x] Vytvořit `ci-matrix.yml` konfiguraci
- [x] Vytvořit dokumentaci `README.md`

## Fáze 2: Implementace (🔄 V průběhu)

### Migrace skriptů z OpenSSL do OpenSSL-Tools
- [ ] Přesunout `scripts/conan/` → `openssl-tools/scripts/orchestration/`
- [ ] Přesunout `scripts/ci/` → `openssl-tools/scripts/ci/`
- [ ] Přesunout `scripts/validation/` → `openssl-tools/scripts/validation/`
- [ ] Přesunout `conan-dev/` → `openssl-tools/profiles/development/`
- [ ] Přesunout `conan-profiles/` → `openssl-tools/profiles/production/`

### Aktualizace OpenSSL workflows
- [ ] Odstranit komplexní workflows (zachovat pouze trigger a basic-validation)
- [ ] Aktualizovat odkazy na openssl-tools
- [ ] Testovat trigger mechanismus

### Rozšíření OpenSSL-Tools workflows
- [ ] Implementovat `matrix-builds.yml`
- [ ] Implementovat `performance-tests.yml`
- [ ] Implementovat `security-scans.yml`
- [ ] Implementovat `artifact-management.yml`

## Fáze 3: Testování (⏳ Čeká)

### Funkční testování
- [ ] Testovat trigger z OpenSSL do OpenSSL-Tools
- [ ] Testovat build matrix generování
- [ ] Testovat metrics collection
- [ ] Testovat status reporting zpět do OpenSSL

### Performance testování
- [ ] Porovnat build časy před/po separaci
- [ ] Testovat cache hit rates
- [ ] Validovat resource utilization

### Integrace testování
- [ ] End-to-end test celého workflow
- [ ] Test error handling a recovery
- [ ] Test různých build scopes (minimal, standard, full)

## Fáze 4: Deployment (⏳ Čeká)

### OpenSSL Repository cleanup
- [ ] Odstranit přesunuté skripty a konfigurace
- [ ] Aktualizovat README.md s odkazy na openssl-tools
- [ ] Vyčistit nepoužívané workflows
- [ ] Nahradit `conanfile.py` za `conanfile-minimal.py`

### OpenSSL-Tools finalizace
- [ ] Dokončit všechny workflows
- [ ] Přidat comprehensive dokumentaci
- [ ] Nastavit proper permissions a secrets
- [ ] Implementovat monitoring a alerting

### Dokumentace
- [ ] Aktualizovat CONTRIBUTING.md v obou repositories
- [ ] Vytvořit migration guide pro vývojáře
- [ ] Dokumentovat nový workflow pro přispěvatele

## Aktuální stav souborů

### Vytvořené soubory (OpenSSL - minimal)
```
✅ conanfile-minimal.py              # Zjednodušený conanfile
✅ conan/default.profile             # Základní profil
✅ conan/ci-minimal.yml             # Minimální CI konfigurace
✅ .github/workflows/basic-validation.yml  # Základní validace
✅ .github/workflows/trigger-tools.yml (aktualizován)
```

### Vytvořené soubory (OpenSSL-Tools struktura)
```
✅ openssl-tools-structure/README.md
✅ openssl-tools-structure/scripts/orchestration/build_orchestrator.py
✅ openssl-tools-structure/scripts/metrics/build_metrics_collector.py
✅ openssl-tools-structure/configs/ci-matrix.yml
```

### Soubory k migraci (z OpenSSL do OpenSSL-Tools)
```
📦 scripts/conan/build_matrix_manager.py
📦 scripts/conan/conan_orchestrator.py
📦 scripts/conan/dependency_manager.py
📦 scripts/conan/performance_benchmark.py
📦 scripts/ci/conan_automation.py
📦 scripts/ci/performance_tests.py
📦 scripts/ci/test_harness.py
📦 scripts/validation/pre-build-validation.py
📦 scripts/validation/cache-optimization.py
📦 conan-dev/ (celý adresář)
📦 conan-profiles/ (celý adresář)
```

### Workflows k odstranění z OpenSSL
```
❌ .github/workflows/conan-ci.yml
❌ .github/workflows/conan-release.yml
❌ .github/workflows/conan-pr-tests.yml
❌ .github/workflows/modern-ci.yml
❌ .github/workflows/optimized-ci.yml
❌ .github/workflows/binary-first-ci.yml
❌ .github/workflows/package-artifacts-upload.yml
❌ .github/workflows/python-environment-package.yml
```

## Další kroky

### Okamžité akce
1. **Testovat základní validaci**: Spustit `basic-validation.yml` workflow
2. **Implementovat chybějící skripty**: Dokončit metrics a warm-up skripty
3. **Vytvořit OpenSSL-Tools repository**: Nahrát strukturu do skutečného repository

### Střednodobé akce
1. **Postupná migrace**: Přesunout skripty jeden po druhém s testováním
2. **Workflow implementace**: Vytvořit všechny potřebné GitHub Actions
3. **Performance monitoring**: Implementovat comprehensive metrics

### Dlouhodobé akce
1. **Optimalizace**: Vyladit performance a caching
2. **Monitoring**: Přidat alerting a dashboards
3. **Dokumentace**: Kompletní dokumentace pro vývojáře

## Rizika a mitigace

### Vysoké riziko
- **Ztráta funkčnosti během migrace**
  - *Mitigace*: Postupná migrace s paralelním testováním
- **Komplexní debugging cross-repository**
  - *Mitigace*: Comprehensive logging a correlation IDs

### Střední riziko
- **Performance regrese**
  - *Mitigace*: Benchmark testing před/po migraci
- **Cache invalidation issues**
  - *Mitigace*: Careful cache key management

### Nízké riziko
- **Developer confusion**
  - *Mitigace*: Clear documentation a migration guide

## Úspěšné dokončení

Migrace bude považována za úspěšnou když:
- [x] OpenSSL repository obsahuje pouze minimální build setup
- [ ] OpenSSL-Tools repository zvládá veškerou orchestraci
- [ ] Build časy jsou stejné nebo lepší než před migrací
- [ ] Všechny existující workflows fungují
- [ ] Vývojáři mohou přispívat bez změny workflow
- [ ] Monitoring a metrics fungují správně