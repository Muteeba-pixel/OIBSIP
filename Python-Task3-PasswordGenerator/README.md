# SecurePass

**Password Security Workstation**

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![UI Framework](https://img.shields.io/badge/UI-CustomTkinter-blueviolet.svg)](https://github.com/TomSchimansky/CustomTkinter)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](#installation)
[![Tests](https://img.shields.io/badge/tests-29%20passed%20%7C%20100%25-success.svg)](#testing)

---

## Overview

**SecurePass** is a professional desktop password security and generation workstation built with Python. Designed for developers and security professionals, SecurePass combines **cryptographically secure randomness, Information Theory entropy evaluation, and a refined developer-tool aesthetic**.

The application operates **100% locally and offline**. It uses Python's standard `secrets` module to pull entropy directly from operating system kernel sources (`BCryptGenRandom` on Windows, `getrandom` on Linux), provides practical one-click presets, calculates Shannon information entropy, and enforces zero-persistence memory isolation.

---

## Visual Design & Architecture

SecurePass avoids common AI-generated and generic dashboard templates:
- **Workstation Layout**: A cohesive two-pane desktop workstation (1100 × 780 px) with a dominant primary generator area, a supporting security analysis panel, and a volatile session history buffer.
- **Refined Color Palette**: Deep charcoal and graphite surfaces (`#0D1117`, `#161B22`, `#1C2128`), restrained borders (`#30363D`), crisp high-contrast text (`#F0F6FC`), and a distinctive warm amber/gold accent (`#D29922`).
- **Hero Password Display**: A large, recessed credential well featuring `Consolas` / `Cascadia Mono` typography (18pt bold), integrated `SHOW` / `HIDE` and `COPY` actions, and an understated strength meter.
- **Desktop Authenticity**: Native Windows system fonts (`Segoe UI`), believable control proportions, keyboard navigation (`Enter`/`Space` to generate, `Ctrl+C` to copy), and transient clipboard feedback (`COPIED!` for 1.8s).

---

## Key Features

- **Cryptographically Secure Randomness**: Powered by Python's `secrets` module leveraging operating system kernel entropy.
- **Policy Presets**: One-click professional presets (`STANDARD` 14c, `STRONG` 20c, `MAXIMUM` 32c) with manual customization.
- **Character Policy Guarantees**: Guaranteed representation of every enabled character set (uppercase, lowercase, digits, symbols).
- **Ambiguous-Character Exclusion**: Eliminates visually confusing characters (`0`, `O`, `o`, `1`, `l`, `I`, `|`, etc.) to prevent manual transcription errors.
- **Repeat & Sequence Protection**: Options to avoid adjacent duplicate characters (`aa`, `11`) and 3-character sequential runs (`abc`, `123`).
- **Information Theory Entropy Engine**: Evaluates theoretical alphabet pool size and Shannon information entropy aligned with NIST SP 800-63B guidelines.
- **Character Composition Telemetry**: Real-time breakdown of character classes (uppercase, lowercase, numbers, symbols) with compact horizontal meters.
- **Volatile Session History**: Keeps an in-memory buffer of recent passwords with on-demand masking (`••••••••`), individual copy actions, and instant purge capability.
- **Zero Disk Persistence**: Passwords are never written to disk, cache files, temporary files, or logs.
- **Resilient Clipboard Manager**: Contextual `COPIED!` visual feedback with native OS Win32 fallback.

---

## Security Design & Cryptographic Foundations

### Why `secrets` Instead of `random`?

A common vulnerability in amateur password tools is the misuse of Python's standard `random` module:

```python
# INSECURE (Pseudorandom - Mersenne Twister MT19937)
import random
pwd = "".join(random.choice(chars) for _ in range(20))
```

The standard `random` module is powered by the **Mersenne Twister (MT19937)** algorithm. While statistically uniform, Mersenne Twister is **completely deterministic and not cryptographically secure**:
- Its internal state comprises exactly 624 32-bit words (19,937 bits).
- An adversary observing 624 consecutive outputs can fully reconstruct the generator's internal state.
- Once reconstructed, the adversary can accurately predict all future and previous password outputs.

### Cryptographic PRNG (CSPRNG) Implementation

SecurePass relies exclusively on Python's `secrets` module, which delegates to the operating system's cryptographic random subsystem:
- **Windows**: `CryptGenRandom` / `BCryptGenRandom` via Cryptography API: Next Generation (CNG).
- **Linux**: Kernel CSPRNG via `getrandom(2)` / `/dev/urandom`.
- **macOS / BSD**: Kernel CSPRNG via `arc4random_buf` / `getentropy(2)`.

```python
# SECURE (Cryptographically Secure PRNG)
import secrets
pwd_char = secrets.choice(character_pool)
```

Kernel entropy pools aggregate unpredictable physical hardware noise (interrupt timings, disk head latency, thermal fluctuations, packet arrival intervals), providing genuine information-theoretic unpredictability.

### Uniform Position Shuffling (Fisher-Yates)

To guarantee character set composition without introducing predictable structural bias (such as always placing an uppercase character at index 0 or digits at the end), SecurePass applies an in-place **Fisher-Yates shuffle** driven by `secrets.randbelow()`:

$$\forall i \in \{n-1, \dots, 1\}, \quad j \xleftarrow{\text{CSPRNG}} \{0, \dots, i\}, \quad \text{swap}(A[i], A[j])$$

This ensures that every possible permutation of the generated password has an identical mathematical probability of $1 / n!$.

### Zero-Persistence Threat Model

| Threat Vector | Mitigation Strategy in SecurePass |
|---|---|
| **Disk Forensics** | Passwords are never written to disk, local databases, cache files, temporary files, or logs. |
| **Network Interception** | 100% offline architecture. Zero HTTP/HTTPS endpoints or remote dependencies exist. |
| **Shoulder Surfing** | Passwords and session histories feature on-demand dot masking (`••••••••`). |
| **Process Termination** | Session history resides strictly in volatile RAM and is immediately purged upon process exit. |

---

## Password Strength & Information Entropy Model

SecurePass avoids simplistic length-only heuristics by calculating theoretical information entropy:

### 1. Character Space Metric (Pool Entropy)

$$R = \sum_{S \in \text{Active Sets}} |S|$$

$$E_{\text{pool}} = L \times \log_2(R)$$

Where $L$ is password length and $R$ is the cardinality of the composite alphabet pool.

### 2. Shannon Information Entropy

To penalize low-variety repetitive strings (such as `aaaaaaaaaaaa1111`), SecurePass computes character frequency probability:

$$H(X) = -\sum_{i=1}^{k} P(x_i) \log_2 P(x_i)$$

$$E_{\text{effective}} = \min\left(E_{\text{pool}}, \; L \times H(X) \times 1.25\right) - \text{Penalties}$$

### 3. Structural Penalties
- **Consecutive Repeats**: $-4.0\text{ bits}$ per repeating adjacent character pair.
- **Sequential Runs**: $-6.0\text{ bits}$ per 3-character alphabetical/numerical run (e.g. `abc`, `123`).
- **Sub-8 Length**: Flat $-25.0\text{ bits}$ penalty.

### 4. Classification Tiers

| Score | Tier | Criteria | Indicator | Composition Guarantee |
|:---:|:---|:---|:---:|:---|
| **4** | **VERY STRONG** | $\ge 16$ chars, $\ge 75$ bits entropy, $\ge 3$ types | Green | High brute-force resistance |
| **3** | **STRONG** | $\ge 12$ chars, $\ge 50$ bits entropy, $\ge 2$ types | Blue | Robust for personal credentials |
| **2** | **MODERATE** | $\ge 8$ chars, $\ge 30$ bits entropy | Amber | Acceptable for low-risk usage |
| **1** | **WEAK** | $< 8$ chars or $< 30$ bits entropy | Red | Vulnerable to attack |

---

## Project Structure

```
Python-Task3-PasswordGenerator/
├── main.py                       # Windows High-DPI bootstrap & application entrypoint
├── requirements.txt              # Dependency specification (customtkinter, darkdetect)
├── README.md                     # Technical documentation & portfolio overview
├── LICENSE                       # MIT License
├── securepass/
│   ├── __init__.py               # Package metadata and versioning
│   ├── core/                     # CORE BUSINESS LOGIC (Zero GUI dependencies)
│   │   ├── __init__.py           # Public service exports
│   │   ├── models.py             # Data contracts (PasswordPolicy, StrengthResult, HistoryEntry)
│   │   ├── generator.py          # CSPRNG generator (secrets, Fisher-Yates, constraint filters)
│   │   ├── evaluator.py          # Shannon & alphabet pool entropy engine
│   │   └── session.py            # Volatile in-memory FIFO session buffer
│   └── ui/                       # WORKBENCH PRESENTATION LAYER
│       ├── __init__.py           # UI package entry
│       ├── theme.py              # Graphite & gold desktop design tokens
│       ├── components.py         # Workstation widgets (SubtleDivider, CompositionIndicator)
│       ├── clipboard.py          # Resilient clipboard manager with Win32 fallback
│       └── app.py                # Workstation controller (Hero Area, Policy, Analysis, Session)
└── tests/                        # AUTOMATED TEST SUITE (29 tests)
    ├── __init__.py
    ├── test_models.py            # Policy validation unit tests
    ├── test_generator.py         # CSPRNG randomness, constraints & repeat filters
    ├── test_evaluator.py         # Entropy calculation & composition stats tests
    ├── test_session.py           # In-memory session manager tests
    └── test_clipboard.py         # Clipboard reliability and callback tests
```

---

## Installation

### Prerequisites

- Python **3.8** or higher
- Desktop OS (Windows 10/11, macOS, Linux)

### Setup

```bash
# Clone the repository
git clone https://github.com/your-username/SecurePass.git
cd SecurePass

# Install lightweight desktop UI dependencies
pip install -r requirements.txt

# Launch the workstation
python main.py
```

---

## Testing

Execute the test suite with Python's built-in `unittest` runner:

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

### Test Output

```text
test_copy_empty_text_returns_false (test_clipboard.TestClipboardManager) ... ok
test_copy_valid_text_succeeds_and_triggers_callback (test_clipboard.TestClipboardManager) ... ok
test_composition_stats (test_evaluator.TestPasswordEvaluator) ... ok
test_empty_password (test_evaluator.TestPasswordEvaluator) ... ok
test_entropy_is_positive_and_rounded (test_evaluator.TestPasswordEvaluator) ... ok
test_moderate_password (test_evaluator.TestPasswordEvaluator) ... ok
test_repeated_characters_penalized (test_evaluator.TestPasswordEvaluator) ... ok
test_sequential_characters_penalized (test_evaluator.TestPasswordEvaluator) ... ok
test_short_password_is_weak (test_evaluator.TestPasswordEvaluator) ... ok
test_very_strong_password (test_evaluator.TestPasswordEvaluator) ... ok
test_ambiguous_character_exclusion (test_generator.TestPasswordGenerator) ... ok
test_avoid_repeats (test_generator.TestPasswordGenerator) ... ok
test_avoid_sequences (test_generator.TestPasswordGenerator) ... ok
test_boundary_lengths (test_generator.TestPasswordGenerator) ... ok
test_default_generation (test_generator.TestPasswordGenerator) ... ok
test_digits_only_policy (test_generator.TestPasswordGenerator) ... ok
test_guaranteed_composition (test_generator.TestPasswordGenerator) ... ok
test_invalid_policy_raises (test_generator.TestPasswordGenerator) ... ok
test_letters_only_policy (test_generator.TestPasswordGenerator) ... ok
test_uniqueness_and_csprng_entropy (test_generator.TestPasswordGenerator) ... ok
test_active_sets_count (test_models.TestPasswordPolicy) ... ok
test_default_policy_is_valid (test_models.TestPasswordPolicy) ... ok
test_empty_character_set_raises_value_error (test_models.TestPasswordPolicy) ... ok
test_length_smaller_than_active_types_raises_value_error (test_models.TestPasswordPolicy) ... ok
test_length_too_long_raises_value_error (test_models.TestPasswordPolicy) ... ok
test_length_too_short_raises_value_error (test_models.TestPasswordPolicy) ... ok
test_add_and_retrieve_entries (test_session.TestSessionHistory) ... ok
test_clear_history (test_session.TestSessionHistory) ... ok
test_fifo_capacity_bound (test_session.TestSessionHistory) ... ok

----------------------------------------------------------------------
Ran 29 tests in 0.154s

OK
```

---

## Technical Highlights for Interviews

1. **CSPRNG vs PRNG**: Explaining why linear congruential or Mersenne Twister generators fail cryptographic requirements and how OS kernel entropy pools (`os.urandom` / `secrets`) solve this.
2. **Fisher-Yates Permutations**: Demonstrating how uniform sampling requires in-place swapping with non-deterministic integer bounds (`secrets.randbelow(i + 1)`).
3. **Information Theory in Security**: Explaining Shannon entropy calculations ($H(X)$) versus theoretical alphabet space size ($L \log_2 R$) to assess credential unpredictability.
4. **Decoupled Architecture**: Demonstrating how domain logic is isolated from the presentation framework, enabling full unit testability without GUI mocks.
5. **Zero-Persistence & Threat Modeling**: Explaining why security tools should minimize credential persistence and enforce volatile RAM bounds.
6. **Defensive Clipboard Engineering**: Managing clipboard locks, cross-platform quirks, and Windows Win32 API fallbacks.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
