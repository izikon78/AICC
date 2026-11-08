#!/usr/bin/env bash
# Track A: complete calibration/training + 45 stress workers, exactly the original configuration (PROTOCOL section 4).
cd /home/claude/ps/AICC/experiments/processing_study
export PYTHONUTF8=1 PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
echo "command: ../../.venv/bin/python -u run_study.py --output results/anthropic-claude-opus-5.5-2026-11-05-trackA-001 --events 1000000 --repeats 3 --train-jobs 72 --validation-jobs 24 --test-jobs 24 --epochs 900"
echo "start_utc: $(date -u +%FT%T.%3NZ)"
../../.venv/bin/python -u run_study.py --output results/anthropic-claude-opus-5.5-2026-11-05-trackA-001 --events 1000000 --repeats 3 --train-jobs 72 --validation-jobs 24 --test-jobs 24 --epochs 900
rc=$?
echo "end_utc: $(date -u +%FT%T.%3NZ)"
echo "exit_status: $rc"
