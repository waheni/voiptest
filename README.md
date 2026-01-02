# 📞 voiptest — VoIP Regression Smoke Testing (CI‑Ready)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**voiptest** is an open‑source CLI tool designed to help VoIP / SIP teams automate basic call validation — especially in CI/CD — so you *never ship a broken call flow again*.

It’s simple, developer‑friendly, and built to work with Docker and existing VoIP stacks (Asterisk, Kamailio, Freeswitch, SBCs).

---

## 🚀 Why voiptest?

Testing VoIP systems manually is:
- slow
- error‑prone
- hard to reproduce
- often ignored until production breaks

Existing tools like **SIPp** are powerful, but:
- hard to maintain XML scenarios
- not designed for CI regression testing
- difficult to integrate into pipelines

**voiptest** fills the gap:
✔ YAML‑based test definitions  
✔ Clear PASS / FAIL results  
✔ CI‑friendly (JUnit output)  
✔ Docker‑first (no SIPp installation headaches)  

---

## 📦 Features (v0.1)

- 🧪 Validate basic call flows (answered / failed / busy / no_answer)
- 📋 YAML test definitions
- 🔁 Matrix testing (multiple destinations)
- 📊 JUnit output for CI systems
- 🐳 Docker‑first execution
- ☎️ Asterisk lab included

---

## 🛠 Installation

### 🔹 Option A — Docker (recommended)

```bash
docker build -t voiptest .
```

Run a test:
```bash
docker run --rm --network host   -v "$PWD:/work" -w /work   voiptest run examples/smoke_basic.yaml
```

> ℹ️ `--network host` allows SIP/RTP traffic to reach your local VoIP stack.

---

### 🔹 Option B — Native (Advanced)

```bash
pip install -e .
sudo apt install sip-tester
```

Run:
```bash
voiptest run examples/smoke_basic.yaml
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

## 🛣 Roadmap

| Version | Features |
|-------|----------|
| v0.1 | Basic calls, YAML, Docker, CI |
| v0.2 | DTMF / IVR navigation |
| v0.3 | RTP / audio validation |
| v0.4 | Scenario builder |
| v1.0 | Dashboard + reporting |

---

## ❤️ Contributing

We welcome:
- Feature requests
- Bug reports
- Pull requests

👉 Open an issue to propose new features or improvements.

---

## 📄 License

MIT License — see [LICENSE](LICENSE)

---

## 🙌 Final Note

This project is built for engineers who want **confidence in their VoIP deployments**.

If you use it, star it ⭐ and share feedback!
