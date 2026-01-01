# VoIPTest - Complete File Summary

## Complete Project Implementation

This document provides a complete overview of all files in the voiptest project.

---

## 📁 Project Structure

```
voiptest/
├── voiptest/                          # Main Python package
│   ├── __init__.py                    # Package initialization
│   ├── cli.py                         # CLI using Typer (run command)
│   ├── config.py                      # Pydantic models for YAML
│   ├── runner.py                      # Test orchestration
│   ├── engines/
│   │   ├── __init__.py
│   │   ├── sipp.py                    # ✅ IMPLEMENTED with subprocess
│   │   └── sipp_scenarios/
│   │       └── uac_basic.xml          # ✅ SIPp UAC scenario
│   └── report/
│       ├── __init__.py
│       └── junit.py                   # JUnit XML generation
├── examples/
│   ├── smoke_basic.yaml               # Basic call test
│   ├── negative_404.yaml              # 404 test
│   └── smoke_matrix.yaml              # Matrix test
├── lab/                               # ✅ Docker test lab
│   └── asterisk/
│       ├── extensions.conf            # Dialplan
│       └── pjsip.conf                 # SIP config
├── docker-compose.yml                 # ✅ Asterisk container
├── pyproject.toml                     # Project config
├── .gitignore                         # Git ignore
├── README.md                          # Full documentation
└── IMPLEMENTATION.md                  # Technical reference
```

---

## ✅ Implementation Checklist

### Core Modules
- ✅ `voiptest/cli.py` - Typer CLI with `voiptest run <path> --junit --out`
- ✅ `voiptest/config.py` - Pydantic models (Target, Accounts, Call, Expect, Matrix)
- ✅ `voiptest/runner.py` - Load YAML, validate, expand matrix, run tests
- ✅ `voiptest/engines/sipp.py` - **FULLY IMPLEMENTED** with subprocess
- ✅ `voiptest/report/junit.py` - JUnit XML generation

### SIPp Engine Features
- ✅ CSV injection file generation (to;from_user;domain)
- ✅ Subprocess execution with proper arguments
- ✅ SIPp parameters: -m 1, -l 1, -timeout, -timeout_error, -trace_msg, -trace_err, -nd
- ✅ Message and error log files
- ✅ SIP code extraction (ignoring 1xx, keeping last >=200)
- ✅ Outcome determination (success/failure/timeout)
- ✅ Expectation checking
- ✅ Error handling and helpful messages

### SIPp Scenario
- ✅ `voiptest/engines/sipp_scenarios/uac_basic.xml` - Minimal UAC scenario
  - INVITE with SDP
  - Optional 100, 180, 183
  - Required 200 OK
  - ACK
  - 5s pause
  - BYE
  - 200 OK

### Docker Lab
- ✅ `docker-compose.yml` - Asterisk container with port mappings
- ✅ `lab/asterisk/extensions.conf` - Extensions 2000, 2001, 2002
- ✅ `lab/asterisk/pjsip.conf` - Accounts 1001, 2000-2002
- ✅ SIP UDP 5060 exposed
- ✅ RTP range 10000-10100 exposed

### Examples
- ✅ `examples/smoke_basic.yaml` - Successful call to 2000
- ✅ `examples/negative_404.yaml` - Call to non-existent 9999
- ✅ `examples/smoke_matrix.yaml` - Matrix expansion to multiple destinations

### Documentation
- ✅ `README.md` - Complete installation, usage, and lab instructions
- ✅ `IMPLEMENTATION.md` - Technical reference
- ✅ CI/CD examples (GitHub Actions, GitLab CI, Jenkins)

---

## 🚀 Quick Start Commands

```bash
# 1. Install project
pip install -e .

# 2. Start Asterisk lab
docker-compose up -d

# 3. Run basic test
voiptest run examples/smoke_basic.yaml

# 4. Run all tests with JUnit output
voiptest run examples/ --junit --out test-results

# 5. View Asterisk logs
docker-compose logs -f asterisk

# 6. Stop lab
docker-compose down
```

---

## 📊 SIPp Engine Implementation Details

### Function: `execute_test(config: VoipTestConfig)`
**Purpose:** Main entry point for running a test
**Returns:** Dict with name, passed, config, actual, duration_s, error, logs

### Function: `run_sipp(config: VoipTestConfig)`
**Purpose:** Execute SIPp subprocess
**Process:**
1. Create temp directory
2. Generate CSV injection file
3. Build SIPp command with all arguments
4. Execute subprocess with timeout
5. Read message and error logs
6. Extract final SIP code
7. Return results with logs

**SIPp Arguments:**
```
sipp <host>
  -i 0.0.0.0                    # Local IP
  -p 5061                       # Local port (avoid 5060 conflict)
  -sf uac_basic.xml             # Scenario file
  -inf inject.csv               # CSV injection (to;from_user;domain)
  -m 1                          # Max 1 call
  -l 1                          # Rate limit
  -r 1                          # Call rate
  -timeout <timeout_s>          # Setup timeout
  -timeout_error                # Exit non-zero on timeout
  -trace_msg                    # Log messages
  -trace_err                    # Log errors
  -nd                           # No default behavior
  -rsa <host>:<port>            # Remote address
  -au <username>                # Auth user (optional)
  -ap <password>                # Auth pass (optional)
  -message_file messages.log    # Message log
  -error_file errors.log        # Error log
```

### Function: `generate_csv_file(path, config)`
**Purpose:** Create CSV injection file
**Format:** `to;from_user;domain` (semicolon-delimited, no header)
**Example:** `2000;1001;localhost`

### Function: `extract_final_sip_code(message_log)`
**Purpose:** Parse message log for final SIP response
**Logic:**
- Regex: `SIP/2\.0\s+(\d{3})`
- Ignore codes 100-199 (provisional)
- Return last code >= 200 (final response)

### Function: `determine_outcome(sipp_result, config)`
**Purpose:** Map SIPp results to outcome
**Logic:**
- "timeout" if timeout in reason
- "success" if code 200-299 or exit 0
- "failure" if code 400-699 or exit non-zero

### Function: `check_expectations(config, actual, sipp_result)`
**Purpose:** Compare actual vs expected
**Checks:**
- outcome matches
- final_sip_code matches (if specified)
- Returns True/False

---

## 🧪 Test Lab Configuration

### Asterisk Extensions (extensions.conf)

**Extension 2000:** Answer → demo-thanks → wait 3s → hangup
**Extension 2001:** Answer → tt-monkeys → wait 2s → hangup
**Extension 2002:** Answer → echo test → hangup
**Extension 9999:** Not configured (returns 404)

### Asterisk Accounts (pjsip.conf)

| Account | Password  | Purpose |
|---------|-----------|---------|
| 1001    | secret123 | Caller  |
| 2000    | secret456 | Callee  |
| 2001    | secret789 | Test    |
| 2002    | secret000 | Test    |

### Network Ports

| Port Range      | Protocol | Purpose      |
|-----------------|----------|--------------|
| 5060            | UDP/TCP  | SIP          |
| 10000-10100     | UDP      | RTP (media)  |

---

## 📝 YAML Test Configuration

### Required Fields
```yaml
version: "1.0"
name: "Test Name"
target: {host, port?, transport?, domain?}
accounts: {caller: {username, password}, callee: {username, password}}
call: {from, to, timeout_s?, max_duration_s?}
expect: {outcome, final_sip_code?, answer_within_s?, min_duration_s?}
```

### Optional Fields
```yaml
matrix: {to: [list of URIs]}  # Expands into multiple tests
```

### Example: Basic Test
```yaml
version: "1.0"
name: "Basic Test"
target:
  host: "localhost"
  port: 5060
  transport: "udp"
accounts:
  caller: {username: "1001", password: "secret123"}
  callee: {username: "2000", password: "secret456"}
call:
  from: "sip:1001@localhost"
  to: "sip:2000@localhost"
  timeout_s: 30
expect:
  outcome: "success"
  final_sip_code: 200
```

---

## 📦 Dependencies

```toml
[project]
dependencies = [
    "typer>=0.9.0",      # CLI framework
    "pyyaml>=6.0",       # YAML parsing
    "pydantic>=2.0",     # Data validation
]

[project.scripts]
voiptest = "voiptest.cli:app"
```

---

## 🔍 Testing the Implementation

### Test Scenarios

**1. Basic successful call:**
```bash
voiptest run examples/smoke_basic.yaml
# Expected: ✅ PASSED (1/1 tests passed)
```

**2. Negative test (404):**
```bash
voiptest run examples/negative_404.yaml
# Expected: ✅ PASSED (expects failure, gets 404)
```

**3. Matrix expansion:**
```bash
voiptest run examples/smoke_matrix.yaml
# Expected: ✅ PASSED (3/3 tests passed)
# Creates 3 separate tests for destinations 2000, 2001, 2002
```

**4. All tests with JUnit:**
```bash
voiptest run examples/ --junit --out test-results
# Expected: Creates test-results/voiptest-results.xml
# Summary: X passed, 0 failed
```

### Debugging

**View SIPp logs:**
```bash
# Logs are in temporary directories
# Path shown in output: /tmp/voiptest_sipp_XXXXX/
# Files: messages.log, errors.log, inject.csv
```

**View Asterisk logs:**
```bash
docker-compose logs -f asterisk
```

**Test SIPp directly:**
```bash
# Manual SIPp test
echo "2000;1001;localhost" > test.csv
sipp localhost -sf voiptest/engines/sipp_scenarios/uac_basic.xml \
  -inf test.csv -m 1 -trace_msg
```

---

## 🎯 Key Features Implemented

✅ **Complete SIPp Integration** - Subprocess execution with all required parameters
✅ **CSV Injection** - Dynamic test data (to;from_user;domain)
✅ **Log Parsing** - Extract SIP codes from message logs
✅ **Error Handling** - Timeouts, exit codes, helpful error messages
✅ **Docker Lab** - Complete Asterisk environment for testing
✅ **Matrix Expansion** - Test multiple destinations from single config
✅ **JUnit Output** - CI/CD integration ready
✅ **CLI** - Simple command-line interface with Typer
✅ **Validation** - Pydantic-based YAML validation

---

## 📚 Additional Documentation

- `README.md` - Complete user documentation with installation, usage, examples
- `IMPLEMENTATION.md` - Technical reference and quick start
- CI/CD examples for GitHub Actions, GitLab CI, Jenkins
- Troubleshooting guide
- Configuration reference tables

---

## 🎉 Project Status: COMPLETE

All requirements have been fully implemented:
- ✅ Core modules (cli, config, runner, engines, report)
- ✅ SIPp engine with subprocess execution
- ✅ UAC scenario XML
- ✅ Docker Compose lab with Asterisk
- ✅ Example YAML test files
- ✅ Complete documentation

The project is ready to use!
