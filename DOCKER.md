# VoIPTest Docker Quick Reference

## Build Image

```bash
docker build -t voiptest .
```

## Basic Usage

```bash
# Run single test
docker run --rm --network host -v $(pwd):/work voiptest run examples/smoke_basic.yaml

# Run all tests
docker run --rm --network host -v $(pwd):/work voiptest run examples/

# With JUnit output
docker run --rm --network host -v $(pwd):/work voiptest run examples/ --junit --out test-results

# View help
docker run --rm voiptest --help
```

## Shell Alias (Recommended)

Add to `~/.bashrc` or `~/.zshrc`:

```bash
alias voiptest='docker run --rm --network host -v $(pwd):/work voiptest'
```

Then use like a native command:

```bash
voiptest run examples/smoke_basic.yaml
voiptest run examples/ --junit --out test-results
```

## With Asterisk Lab

```bash
# Start lab
docker-compose up -d
sleep 10

# Run tests
docker run --rm --network host -v $(pwd):/work voiptest run examples/

# Stop lab
docker-compose down
```

## Flags Explained

- `--rm` - Remove container after execution (cleanup)
- `--network host` - Use host networking (required for localhost:5060 access)
- `-v $(pwd):/work` - Mount current directory to /work in container
- `voiptest` - Image name
- Remaining args passed to voiptest command

## Image Details

**Base:** Ubuntu 22.04
**Size:** ~200MB
**Contains:**
- Python 3.10
- SIPp 3.6+
- voiptest CLI
- All Python dependencies

**Build Time:** ~1-2 minutes (first time)
**Run Time:** Near-instant (container startup ~100ms)

## Advanced Usage

### Run with custom network

```bash
docker run --rm --network my-network -v $(pwd):/work voiptest run examples/
```

### Debug inside container

```bash
docker run --rm -it --network host -v $(pwd):/work --entrypoint /bin/bash voiptest
# Inside container:
voiptest run examples/smoke_basic.yaml
sipp -v
python --version
```

### Mount only examples directory

```bash
docker run --rm --network host -v $(pwd)/examples:/work/examples voiptest run examples/
```

## CI/CD Integration

### GitHub Actions

```yaml
- name: Build image
  run: docker build -t voiptest .

- name: Run tests
  run: docker run --rm --network host -v $(pwd):/work voiptest run examples/ --junit --out test-results
```

### GitLab CI

```yaml
script:
  - docker build -t voiptest .
  - docker run --rm --network host -v $(pwd):/work voiptest run examples/ --junit --out test-results
```

### Jenkins

```groovy
sh 'docker build -t voiptest .'
sh 'docker run --rm --network host -v $(pwd):/work voiptest run examples/ --junit --out test-results'
```

## Comparison: Docker vs Native

| Feature | Docker | Native |
|---------|--------|--------|
| Setup | `docker build` | Install Python, SIPp, deps |
| Dependencies | Included | Manual install |
| Isolation | Full | None |
| Portability | High | OS-dependent |
| Startup | ~100ms overhead | Instant |
| Updates | Rebuild image | `pip install -U` |

**Recommendation:** Use Docker for CI/CD and consistent environments. Use native for development iteration.
