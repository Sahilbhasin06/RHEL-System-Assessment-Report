# rhcheck

A lightweight, cross-compatible CLI health and security diagnostic tool built specifically for **Red Hat Enterprise Linux (RHEL) 8, 9, and 10**. 

`rhcheck` allows system administrators and engineers to quickly assess local server health, software ecosystem compliance, and foundational security postures in real-time, matching local states against engineering baselines. It is designed to run seamlessly across major RHEL versions by targeting system-native APIs (`/proc`) and fallback binary interfaces safely down to Python 3.6.

---

## Key Features

- **Hardware Utilization Analysis**: Monitors real-time CPU and RAM metrics, alongside dynamic, root partition tracking (scanning physical storage of `/`).
- **Subscription & Entitlement Auditing**: Seamlessly detects Red Hat Subscription Manager (RHSM) registration states, providing native compatibility with modern **Simple Content Access (SCA)** frameworks.
- **Software Lifecycle Tracking**: Evaluates pending operating system updates by gracefully mapping DNF and DNF5 exit behaviors across diverse lifecycle platforms.
- **Security & Compliance Auditing**: Reviews core host settings, including live SELinux enforcement states and critical security file attributes (e.g., octal permissions on `/etc/shadow`).
- **Proactive System Diagnostics**: Detects resource-leaking infrastructure faults like zombie/defunct processing tables.
- **Test-Driven Design (TDD)**: Formulated entirely with predictable, mockable unit testing boundaries via `pytest`.

---

## How It Works

The `rhcheck` tool operates as a localized user-space diagnostic broker. It acts as an abstraction layer between the human operator and low-level system endpoints.

                  ┌────────────────────────────────────────┐
                  │          Human Administrator           │
                  └───────────────────┬────────────────────┘
                                      │ (Executes rhcheck)
                                      ▼
                  ┌────────────────────────────────────────┐
                  │       CLI Presentation Layer           │
                  │           (src/main.py)                │
                  └───────────────────┬────────────────────┘
                                      │ (Invokes Checkers)
                                      ▼
                  ┌────────────────────────────────────────┐
                  │         Core Logic Engine              │
                  │         (src/checkers.py)              │
                  └─────────┬───────────────┬──────────────┘
                            │               │
         ┌──────────────────┴──┐         ┌──┴──────────────────┐
         │ System/Kernel APIs  │         │  OS Subprocesses    │
         │(psutil / os modules)│         │ (External Binaries) │
         └──────────┬──────────┘         └──────────┬──────────┘
                    │                               │
    ┌───────────────┼──────────────┐  ┌─────────────┼──────────────┐
    ▼               ▼              ▼  ▼             ▼              ▼
    [/proc]      [/etc/shadow]     [Disk] [sestatus]  [dnf]   [subscription-manager]


1. **Presentation Layer (`src/main.py`)**: Built using `Typer`, it parses user commands and orchestrates execution flow. It captures outputs from the logic engine and passes them to `Rich`, which builds the final color-coded UI grid.
2. **Logic Engine (`src/checkers.py`)**: A decoupled, statically typed broker. It contains zero print statements or CLI flags, allowing it to be tested using `pytest`.
3. **Data Acquisition Pathways**:
   - **Direct Kernel Inspection**: For hardware (CPU, RAM, Disks) and diagnostics (Zombie checks), the engine directly monitors the virtual Linux `/proc` filesystem and kernel tables via `psutil`. This avoids spinning up costly subshells.
   - **Binary Wrapper Pipeline**: For ecosystem states (`sestatus`, `dnf`, `subscription-manager`), the engine uses `subprocess.run` to call system binaries. It isolates standard error output (`stderr`), captures exit return-codes (like DNF's `100`), and maps the string content to clean execution states.

---

## Technical Limitations & Guardrails

When deploying this tool across production RHEL 8, 9, and 10 environments, keep the following architectural constraints in mind:

- **Privilege Requirements (Root vs. Regular User)**: Parsing `/etc/shadow` requires root read access (`UID 0`). If run as an unprivileged user, the tool will safely fallback to displaying `Permission Denied` rather than crashing. Running `dnf check-update` as non-root reads from cached local files, which may be stale.
- **Network Dependency**: The tool wraps live DNF queries. If a host is completely air-gapped or lacks access to an on-premise Red Hat Satellite Server, connection timeouts will cause the tool to return `Check Failed (Repo issue?)`.
- **Python 3.6 Standard Library Limits**: To support legacy RHEL 8 setups, modern features like structural pattern matching (`match/case`) or advanced type union hints (`int | str`) are omitted in favor of broad backwards compatibility.
- **Execution Speed Overhead**: Because external calls to `dnf` require sync polling, generating reports may take several seconds depending on network repo latency.

---

## Project Layout

```text
rhcheck/
├── README.md             # End-user setup, syntax usage, and testing documentation
├── Result.png            # Output of the rhcheck.
├── src/
│   ├── __init__.py       # Marks the directory as an importable Python package
│   ├── main.py           # CLI routing table (Typer) and terminal layout formatting (Rich)
│   └── checkers.py       # Operating system query scripts, parsing logic, and hardware maps
└── tests/
    ├── __init__.py       # Marks the test folder path boundary
    └── test_checkers.py  # Comprehensive pytest unit-test suite using system mocks
```

## Installation & Setup
Because rhcheck is packaged using modern pyproject.toml standards, you can easily deploy it into development environments.

## Prerequisites
Ensure your environment meets the minimum version constraints (fully compatible with default Python installations on RHEL 8/9/10):

Python: >= 3.6

Dependencies: typer, rich, psutil

## Local Development Execution (Without Installing)
You can run the full tool framework without configuring any global system parameters by executing:

```bash
# Generate the full diagnostic status table
python3 src/main.py report

# Access the dynamic CLI documentation and flags
python3 src/main.py --help
```

## Test-Driven Validation Matrix
The project code is structurally decoupled from active kernel metrics using mock objects. This allows the testing matrix to simulate diverse RHEL infrastructures (such as SCA entitlement configurations) on non-Linux machines (Mac, Windows) cleanly.

## Security Baseline Logic Reference

| Target Parameter | Optimal Evaluation Baseline | Non-Compliant/Warning Action Trigger |
| :--- | :--- | :--- |
| **SELinux Status** | `enabled` / `enforcing` | Highlights as `red` or `yellow` warning if disabled. |
| **File Permissions** | `/etc/shadow` matching `0o600` or `0o000` | Flags out-of-compliance permissions as structural `red` failures. |
| **RHSM Entitlement** | `Registered` or `Registered (SCA Active)` | Flags disconnected or unregistered states explicitly. |
| **Infrastructure Faults**| `0 Zombie Processes` | Signals warning alerts if abandoned PID tables leak memory context blocks. |
