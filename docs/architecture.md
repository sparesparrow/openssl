## OpenSSL Ecosystem Architecture (Color-coded)

**Legend:**
- 🔵 **Actors** (Developers, Consumers): Blue - Human participants in the ecosystem
- 🟢 **Actions** (CI/CD steps, Conan commands): Green - Operations and workflows
- 🟡 **Repositories** (Git repos): Yellow - Source code repositories
- 🟣 **Packages/Artifacts** (Conan packages, binaries): Purple - Built and cached artifacts
- 🟠 **Workflows** (GitHub Actions): Orange - Automated processes

### High-Level Architecture Diagram

```mermaid
graph TB
    %% Actors (Blue)
    Alice(Developer Alice):::blue
    Bob(Developer Bob):::blue
    Consumer(Consumer Project):::blue

    %% Repositories (Yellow)
    subgraph "🔐 Foundation Layer"
        BASE[openssl-conan-base<br/>📦 Utilities + Profiles]:::yellow
        POLICY[openssl-fips-policy<br/>📦 FIPS Certificates]:::yellow
    end

    subgraph "🛠️ Tooling Layer"
        TOOLS[openssl-tools<br/>CI/CD, Conan orchestration]:::yellow
    end

    subgraph "🌐 Domain Layer"
        OPENSSL[openssl<br/>🔐 Cryptographic Library]:::yellow
    end

    subgraph "🤖 Orchestration Layer (Optional)"
        MCP[mcp-project-orchestrator<br/>AI Templates + MCP]:::yellow
    end

    %% Infrastructure (Purple)
    subgraph "🔧 Infrastructure"
        PYENV[Profiles<br/>~/.conan2/profiles/]:::purple
        CACHE[Conan Cache<br/>~/.conan2/p/]:::purple
        REMOTE[Remote Registry<br/>Cloudsmith/Artifactory]:::purple
    end

    %% Actions (Green)
    Alice -->|🔄 push/PR| OPENSSL
    Bob -->|🔄 push/PR| OPENSSL
    Consumer -->|📦 conan install| REMOTE

    %% Dependencies
    TOOLS -.->|tool_requires| BASE
    TOOLS -.->|tool_requires| POLICY
    OPENSSL -.->|tool_requires| TOOLS

    MCP -.->|optional pip install| TOOLS
    MCP -.->|MCP protocol| TOOLS

    %% Package Flow
    BASE -->|📦 conan create| CACHE
    POLICY -->|📦 conan create| CACHE
    TOOLS -->|📦 conan create| CACHE
    OPENSSL -->|📦 conan create| CACHE

    CACHE -->|⬆️ conan upload| REMOTE
    REMOTE -->|⬇️ conan install| Consumer

    %% Profile Deployment
    BASE -->|⚙️ deploy profiles| PYENV
    PYENV -->|📋 conan profile| OPENSSL

    classDef blue fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef yellow fill:#fff9c4,stroke:#fbc02d,stroke-width:2px
    classDef purple fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef green fill:#e8f5e8,stroke:#2e7d32,stroke-width:2px
    classDef orange fill:#ffe0b2,stroke:#e65100,stroke-width:2px
```

### Detailed Developer Workflow

```mermaid
graph LR
    %% Start
    A[Developer makes changes] --> B{conanfile.py changed?}

    B -->|Yes| C[Update version in conanfile.py]
    B -->|No| D[Commit changes]

    C --> D
    D --> E[Push to feature branch]

    E --> F[Create Pull Request]
    F --> G[🚦 PR Developer Flow Check]
    G --> H{Version bump enforced?}

    H -->|✅ Yes| I[✅ Version bump validated]
    H -->|❌ No| J[❌ Version bump required]

    I --> K[✅ Conan recipe syntax check]
    K --> L[✅ Required files check]

    L --> M[🔄 Trigger full CI pipeline]
    M --> N[🧪 Core builds (Linux, macOS, Windows)]
    N --> O[🔍 Security scanning & SBOM]
    O --> P[📦 Upload to remotes]

    P --> Q{All checks pass?}
    Q -->|✅ Yes| R[✅ Ready for merge]
    Q -->|❌ No| S[❌ Fix issues and retry]

    R --> T[Merge to main]
    T --> U[🚀 Release automation]

    %% Styling
    classDef decision fill:#e3f2fd,stroke:#1976d2
    classDef success fill:#e8f5e8,stroke:#2e7d32
    classDef error fill:#ffebee,stroke:#c62828
    classDef process fill:#fff3e0,stroke:#ef6c00

    class B,C,D,E,F,G,H,I,K,L,M,N,O,P,Q,R,S,T,U decision
    class I,K,L,R success
    class J error
    class M,N,O,P,U process
```

### Layer Interaction Details

#### Foundation → Tooling → Domain Flow

```mermaid
graph TD
    %% Foundation Layer
    BASE[openssl-conan-base<br/>v1.0.0] -->|📦 conan create| CACHE1[Local Cache]

    POLICY[openssl-fips-policy<br/>v140-3.1] -->|📦 conan create| CACHE2[Local Cache]

    %% Tooling Layer
    TOOLS[openssl-tools<br/>v1.2.0] -->|tool_requires| BASE
    TOOLS -->|tool_requires| POLICY
    TOOLS -->|📦 conan create| CACHE3[Local Cache]

    %% Domain Layer
    OPENSSL[openssl<br/>v3.4.1] -->|tool_requires| TOOLS
    OPENSSL -->|📦 conan create| CACHE4[Local Cache]

    %% Upload to Remote
    CACHE1 -->|⬆️ conan upload| REMOTE[Cloudsmith]
    CACHE2 -->|⬆️ conan upload| REMOTE
    CACHE3 -->|⬆️ conan upload| REMOTE
    CACHE4 -->|⬆️ conan upload| REMOTE

    %% Consumer Flow
    CONSUMER[Consumer Project] -->|⬇️ conan install| REMOTE

    %% Styling
    classDef foundation fill:#e1f5fe,stroke:#01579b
    classDef tooling fill:#fff9c4,stroke:#fbc02d
    classDef domain fill:#f3e5f5,stroke:#7b1fa2
    classDef cache fill:#fce4ec,stroke:#c62828
    classDef remote fill:#e8f5e8,stroke:#2e7d32
    classDef consumer fill:#fff3e0,stroke:#ef6c00

    class BASE,POLICY foundation
    class TOOLS tooling
    class OPENSSL domain
    class CACHE1,CACHE2,CACHE3,CACHE4 cache
    class REMOTE remote
    class CONSUMER consumer
```

### Key Architecture Principles

1. **🔒 Foundation Layer**: Self-contained utilities with no external dependencies
2. **🛠️ Tooling Layer**: Consumes foundation packages, provides build orchestration
3. **🌐 Domain Layer**: Core cryptographic functionality with Conan packaging
4. **🤖 Orchestration Layer**: Optional AI integration, never a dependency of domain
5. **🔄 Dependency Rule**: Domain → Application → Infrastructure (enforced by tooling)

### Security & Compliance

- **FIPS Compliance**: Separate cache keys prevent FIPS/non-FIPS contamination
- **Supply Chain Security**: All packages signed and scanned for vulnerabilities
- **SBOM Generation**: Comprehensive software bill of materials for transparency
- **Audit Trails**: Complete build and deployment audit logging

### Performance & Reliability

- **Caching Strategy**: Multi-level caching (local → shared → remote)
- **Build Optimization**: Parallel builds with Ninja generator
- **CI/CD Efficiency**: Smart change detection and matrix builds
- **Quality Gates**: Automated testing and security scanning

This architecture ensures maintainable, scalable, and secure OpenSSL ecosystem development with clear separation of concerns and robust automation.


