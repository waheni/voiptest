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
docker run --rm --network host -v $(pwd):/work voiptest run examples/smoke_basic.yaml
docker-compose down
```

Why `--network host`? The Asterisk lab exposes port 5060 on the host. Using `--network host` makes `localhost:5060` inside the test container connect to the same Asterisk instance, allowing SIPp to reach it.

## Native install (optional)

You need Python 3.10+ and SIPp in PATH.
```bash
pip install -e .
voiptest run examples/smoke_basic.yaml
```

## Usage

```bash
voiptest run PATH [--junit] [--out DIR]
# PATH can be a single YAML file or a directory of YAML files
```

Examples:
- Minimal: `voiptest run examples/smoke_basic.yaml`
- All in dir with JUnit: `voiptest run examples/ --junit --out test-results`

Options:
- `--junit` writes `voiptest-results.xml` to the output dir.
- `--out DIR` sets the output dir (default: current directory).

## Supported in v0.1

✅ Basic call outcomes: `answered` | `failed` | `busy` | `no_answer`  
✅ Account-based caller/callee resolution  
✅ Literal destinations (phone numbers, extensions)  
✅ Matrix expansion for multiple destinations  
✅ Final SIP code assertions  
✅ JUnit XML output for CI integration  

❌ DTMF/IVR navigation (planned for v0.2)  
❌ RTP/audio validation (planned for v0.2)  
❌ Call transfers and multi-leg scenarios (planned for v0.2)  

## Example tests

- `examples/smoke_basic.yaml` — happy-path call caller → callee (expects 200)
- `examples/negative_404.yaml` — call to non-existent extension (expects 404)
- `examples/smoke_matrix.yaml` — fan out calls to multiple destinations

## Write a test

```yaml
version: 1
name: "Basic Smoke"

target:
  host: "127.0.0.1"
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
  from: "caller"          # Account key
  to: "callee"            # Account key OR literal (e.g., "2000")
  timeout_s: 30

expect:
  outcome: "answered"     # answered | failed | busy | no_answer
  final_sip_code: 200

# Optional: fan out to multiple destinations
# matrix:
#   to: ["2000", "2001", "2002"]
```

Outcomes:
- **answered**: Call received 200 OK
- **failed**: Call received 4xx/5xx/6xx error (configurable with `final_sip_code`)
- **busy**: Call received 486 Busy
- **no_answer**: Call timed out or received no response

## CI one-liner (Docker)

```bash
docker build -t voiptest .
docker-compose up -d && sleep 10
docker run --rm --network host -v $(pwd):/work voiptest run examples/smoke_basic.yaml
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

MIT. See `LICENSE`.
