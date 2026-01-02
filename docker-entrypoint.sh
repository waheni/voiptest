#!/bin/sh
# Entrypoint wrapper for voiptest Docker container
# Ensures PYTHONPATH includes mounted code

set -e

# If /work/voiptest exists (mounted), use it
if [ -d "/work/voiptest" ]; then
    export PYTHONPATH="/work:${PYTHONPATH}"
    exec python -m voiptest.cli "$@"
else
    # Fallback to installed version
    exec voiptest "$@"
fi
