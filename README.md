# VoIPTest

Lightweight SIP smoke tests for CI. Define calls in YAML, run them with SIPp, get a pass/fail and optional JUnit XML.

**What you can do**
- Prove a basic INVITE/200/ACK/BYE flow still works (or fails with the code you expect)
- Run against the bundled Asterisk lab or your own PBX/SBC
- Fan out destinations with a simple matrix, and emit JUnit for CI

## Quick start (Docker)

```bash
make docker-build     # build image with SIPp and cli
make lab-start        # start Asterisk lab (docker-compose)
make docker-test      # run examples/smoke_basic.yaml
make lab-stop         # stop lab
```

Direct without Make:
```bash
docker build -t voiptest .
docker-compose up -d && sleep 10
docker run --rm --network host -v $(pwd):/work voiptest examples/smoke_basic.yaml
docker-compose down
```

Why `--network host`? SIPp in the container must reach Asterisk on localhost:5060.

## Native install (optional)

You need Python 3.10+ and SIPp in PATH.
```bash
pip install -e .
voiptest examples/smoke_basic.yaml
```

## Usage

```bash
voiptest PATH [--junit] [--out DIR]
# PATH can be a single YAML file or a directory of YAML files
```

Examples:
- Single test: `voiptest examples/smoke_basic.yaml`
- All in dir with JUnit: `voiptest examples/ --junit --out test-results`

## Example tests

- `examples/smoke_basic.yaml` — happy-path call 1001 -> 2000 (expects 200)
- `examples/negative_404.yaml` — missing user (expects 404 failure)
- `examples/smoke_matrix.yaml` — same call fanned out via matrix

## Write a test

```yaml
version: "1.0"
name: "Basic Smoke"

target:
  host: "localhost"
  port: 5060
  transport: "udp"
  domain: "localhost"

accounts:
  caller:
    username: "1001"
    password: "secret123"
  callee:
    username: "2000"
    password: "secret456"

call:
  from: "sip:1001@localhost"
  to: "sip:2000@localhost"
  timeout_s: 30

expect:
  outcome: "success"      # success | failure | timeout
  final_sip_code: 200

# Optional: fan out destinations
# matrix:
#   to: ["sip:2000@localhost", "sip:2001@localhost"]
```

## CI one-liner (Docker)

```bash
docker build -t voiptest .
docker-compose up -d && sleep 10
docker run --rm --network host -v $(pwd):/work voiptest examples/ --junit --out test-results
docker-compose down
```

## Project layout

```
voiptest/
  voiptest/            # CLI + engines
    engines/sipp.py    # SIPp runner
    engines/sipp_scenarios/uac_basic.xml
  examples/            # Ready-to-run YAML tests
  lab/asterisk/        # Test lab config
  docker-compose.yml   # Lab services
```

## Troubleshooting (quick)

- Needs host networking: add `--network host` when targeting localhost services.
- "SIPp not found" (native): install SIPp from your package manager.
- Scenario missing when installed: ensure you reinstall after `git pull` (scenario XML is shipped in the wheel).

## License

Specify your license here.
