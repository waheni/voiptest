# 📞 voiptest — VoIP Regression Testing for CI

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**voiptest** is an open-source CLI tool to automate **VoIP call regression testing** using simple YAML files.

It is designed for:
- VoIP engineers
- DevOps / SRE teams
- CI/CD pipelines
- Anyone tired of manually testing call flows

✅ Docker-first  
✅ CI-friendly  
✅ Built around real SIP behavior  
✅ Designed for automation  

---

## 🚀 Why voiptest?

Testing VoIP systems manually is:
- slow  
- error-prone  
- hard to reproduce  
- usually skipped in CI  

Existing tools (like SIPp) are powerful but:
- hard to maintain
- XML-heavy
- not CI-friendly
- not designed for regression testing

**voiptest solves this by providing:**

✔ Simple YAML test definitions  
✔ Clear PASS / FAIL results  
✔ CI-ready output (JUnit)  
✔ Docker-based execution  
✔ Real SIP calls  

---

## ✨ Features (v0.1)

- 📄 YAML-based test definitions
- 📞 Validate call outcomes:
  - answered
  - failed
  - busy
  - no_answer
- 🔁 Matrix testing
- 📊 JUnit output
- 🐳 Docker-first execution
- ☎️ Asterisk test lab included

---

## 📦 Installation

### ✅ Docker (recommended)

```bash
docker build -t voiptest .
```

Run a test:

```bash
docker run --rm --network host   -v "$PWD:/work" -w /work   voiptest run examples/smoke_basic.yaml
```

---

## 🧪 Example Test

```yaml
version: 1
name: "Basic answered call"

target:
  host: "127.0.0.1"
  port: 5060
  transport: "udp"

accounts:
  caller:
    username: "1001"
    domain: "lab.local"
  callee:
    username: "2000"
    domain: "lab.local"

call:
  from: "caller"
  to: "callee"
  timeout_s: 20

expect:
  outcome: "answered"
  final_sip_code: 200
```

---

## 🔁 CI Integration (GitHub Actions)

```yaml
name: VoIP Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run VoIP tests
        run: |
          docker build -t voiptest .
          docker run --rm --network host             -v "${{ github.workspace }}:/work"             -w /work voiptest run examples/smoke_basic.yaml --junit report.xml

      - name: Upload report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: voiptest-report
          path: report.xml
```

---

## 🧪 Local Test Lab (Asterisk)

Start lab:

```bash
make lab-start
```

Stop lab:

```bash
make lab-stop
```

Default lab values:

| Item | Value |
|------|------|
| SIP Host | 127.0.0.1 |
| SIP Port | 5060 |
| Caller | 1001 |
| Callee | 2000 |

---

## 💻 Development

The Docker image is **environment-only** (Python + SIPp + dependencies). Your code is mounted as a volume for instant feedback!

**Only rebuild when `requirements.txt` changes:**

```bash
docker build -t voiptest .
```

**Make code changes** - they're live immediately:

```bash
# Edit voiptest/cli.py, voiptest/engines/sipp.py, etc.
# Then run without rebuilding:
docker run --rm --network host -v "$PWD:/work" voiptest run examples/
```

**Development workflow:**

```bash
# 1. Build image once
make docker-build

# 2. Start lab
make lab-start

# 3. Edit Python files
vim voiptest/runner.py

# 4. Test immediately (no rebuild!)
make docker-test

# 5. Iterate
# Changes to .py files are instant!
# Only rebuild if you modify requirements.txt
```

---

## 🛣 Roadmap

| Version | Features |
|-------|----------|
| v0.1 | Basic calls, Docker, CI |
| v0.2 | DTMF / IVR |
| v0.3 | RTP validation |
| v1.0 | Dashboard |

---

## 🤝 Contributing

Contributions are welcome:
- Bug reports
- Feature requests
- Pull requests

Open an issue to start.

If you tried this, I’d really appreciate feedback — even ‘this is useless’.

---

# 🧑‍💻 Author
**Heni Wael (Neurahex)**  
GitHub: https://github.com/waheni  
Email: *waelheni@neurahex.com*

---

## 📄 License

MIT License — see [LICENSE](LICENSE)

---

## ❤️ Final Note

Built for engineers who want **confidence in VoIP deployments**.

⭐ Star the repo if you find it useful.
