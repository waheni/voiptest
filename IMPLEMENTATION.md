# VoIPTest - Quick Reference

## Project Structure

```
voiptest/
├── voiptest/                           # Main package
│   ├── __init__.py                     # Package init
│   ├── cli.py                          # CLI with Typer (run command)
│   ├── config.py                       # Pydantic models for YAML validation
│   ├── runner.py                       # Test orchestration and matrix expansion
│   ├── engines/
│   │   ├── __init__.py
│   │   ├── sipp.py                     # SIPp subprocess execution
│   │   └── sipp_scenarios/
│   │       └── uac_basic.xml           # Basic UAC SIP scenario
│   └── report/
│       ├── __init__.py
│       └── junit.py                    # JUnit XML generation
├── examples/                           # Example test files
│   ├── smoke_basic.yaml                # Basic successful call
│   ├── negative_404.yaml               # 404 Not Found test
│   └── smoke_matrix.yaml               # Matrix expansion test
├── lab/                                # Docker lab configuration
│   └── asterisk/
│       ├── extensions.conf             # Dialplan with extensions 2000-2002
│       └── pjsip.conf                  # SIP accounts 1001, 2000-2002
├── docker-compose.yml                  # Asterisk lab environment
├── pyproject.toml                      # Python project config
├── .gitignore                          # Git ignore patterns
└── README.md                           # Full documentation

```

## Quick Start

```bash
# 1. Install dependencies
pip install -e .

# 2. Start Docker lab
docker-compose up -d

# 3. Run tests
voiptest run examples/smoke_basic.yaml

# 4. Run all tests with JUnit output
voiptest run examples/ --junit --out test-results

# 5. Stop lab
docker-compose down
```

## Key Implementation Details

### SIPp Engine (voiptest/engines/sipp.py)

**Functions:**
- `execute_test(config)` - Main entry point, returns test results
- `run_sipp(config)` - Executes SIPp subprocess with proper arguments
- `generate_csv_file(path, config)` - Creates CSV injection file (to;from_user;domain)
- `extract_final_sip_code(log)` - Parses message log for SIP response codes (ignores 1xx)
- `determine_outcome(result, config)` - Maps SIPp results to outcome (success/failure/timeout)
- `check_expectations(config, actual, result)` - Compares actual vs expected
- `validate_sipp_installed()` - Checks if sipp is in PATH
- `get_sipp_version()` - Returns SIPp version string

**SIPp Command Arguments:**
```bash
sipp <host>
  -i 0.0.0.0              # Local IP
  -p 5061                 # Local port
  -sf uac_basic.xml       # Scenario file
  -inf inject.csv         # CSV injection file
  -m 1                    # Max calls
  -l 1                    # Call rate limit
  -r 1                    # Call rate
  -timeout <N>            # Timeout in seconds
  -timeout_error          # Treat timeout as error
  -trace_msg              # Log SIP messages
  -trace_err              # Log errors
  -nd                     # No default behavior
  -rsa <host>:<port>      # Remote socket address
  -au <username>          # Auth username
  -ap <password>          # Auth password
  -message_file <path>    # Message log path
  -error_file <path>      # Error log path
```

**Return Format:**
```python
{
    "name": str,
    "passed": bool,
    "config": dict,         # Original config
    "actual": {
        "outcome": str,     # success/failure/timeout
        "sip_code": int,    # Final SIP response code
        "answer_time_s": None,
        "duration_s": float
    },
    "duration_s": float,
    "error": str,           # Optional
    "logs": {               # Optional
        "stdout": str,
        "stderr": str,
        "message_log": str,
        "error_log": str,
        "temp_dir": str
    }
}
```

### UAC Scenario (uac_basic.xml)

**Flow:**
1. INVITE → target
2. Receive 100 Trying (optional)
3. Receive 180/183 (optional)
4. Receive 200 OK (required)
5. ACK → target
6. Pause 5000ms
7. BYE → target
8. Receive 200 OK

**CSV Injection Fields:**
- `[field0]` - to (extension)
- `[field1]` - from_user (caller)
- `[field2]` - domain

### Docker Lab

**Asterisk Extensions:**
- **2000** - Answers, plays demo-thanks, waits 3s, hangs up
- **2001** - Answers, plays tt-monkeys, waits 2s, hangs up
- **2002** - Echo test
- **9999** - Non-existent (404)

**Test Accounts:**
- 1001 / secret123
- 2000 / secret456
- 2001 / secret789
- 2002 / secret000

**Ports:**
- 5060/udp,tcp - SIP
- 10000-10100/udp - RTP

## Testing the Implementation

```bash
# Test 1: Basic successful call
voiptest run examples/smoke_basic.yaml
# Expected: ✅ PASSED

# Test 2: Negative test (404)
voiptest run examples/negative_404.yaml
# Expected: ✅ PASSED (expects failure)

# Test 3: Matrix expansion
voiptest run examples/smoke_matrix.yaml
# Expected: 3 test cases, all passing

# Test 4: All examples with JUnit
voiptest run examples/ --junit --out test-results
# Expected: Creates test-results/voiptest-results.xml

# Inspect SIPp logs (from last run)
# Check /tmp/voiptest_sipp_* directories
```

## YAML Configuration Schema

```yaml
version: "1.0"                    # Required
name: "Test Name"                 # Required

target:                           # Required
  host: "localhost"               # Required
  port: 5060                      # Default: 5060
  transport: "udp"                # Default: udp (udp/tcp/tls)
  domain: "localhost"             # Optional

accounts:                         # Required
  caller:
    username: "1001"              # Required
    password: "secret123"         # Required
    display_name: "Caller"        # Optional
  callee:
    username: "2000"              # Required
    password: "secret456"         # Required
    display_name: "Callee"        # Optional

call:                             # Required
  from: "sip:1001@localhost"      # Required
  to: "sip:2000@localhost"        # Required
  timeout_s: 30                   # Default: 30
  max_duration_s: 60              # Default: 60

expect:                           # Required
  outcome: "success"              # Required (success/failure/busy/timeout)
  final_sip_code: 200             # Optional
  answer_within_s: 10             # Optional
  min_duration_s: 5               # Optional

matrix:                           # Optional
  to:                             # List of destination URIs
    - "sip:2000@localhost"
    - "sip:2001@localhost"
```

## Dependencies

```toml
dependencies = [
    "typer>=0.9.0",      # CLI framework
    "pyyaml>=6.0",       # YAML parsing
    "pydantic>=2.0",     # Data validation
]
```

## CI/CD Integration

**GitHub Actions:** See README.md "CI/CD Integration Examples"
**GitLab CI:** See README.md "CI/CD Integration Examples"
**Jenkins:** See README.md "CI/CD Integration Examples"

All examples include:
1. Starting Asterisk service/container
2. Installing SIPp
3. Installing voiptest
4. Running tests with --junit
5. Publishing JUnit XML results
