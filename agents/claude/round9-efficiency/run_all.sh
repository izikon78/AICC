#!/usr/bin/env bash
# Reproduce every measurement in AICC_Efficiency_Research_Report_Claude.md.
# Prerequisites: Round 7 packet at /home/claude/r7/AI_Think_Tank_Round7_Test_Packet and Round 8 packet at
# /home/claude/r8/AI_Think_Tank_Round8_Packet (with the earlier submissions), v2 lang.py at /home/claude/sym,
# Node with wabt under /home/claude/sym/node_modules, numpy, and tiktoken with o200k_base (TIKTOKEN_CACHE_DIR if offline).
set -u
sec() { echo; echo "======================================================== $*"; }
sec "E1-E3 runtime overhead";                 python3 bench_runtime.py
sec "E2b WebAssembly boundary";               node bench_wasm.js
sec "E4 harness trials (10 per arm)";         python3 harness_trials.py
sec "Tokenizer table";                        python3 token_table.py
sec "Measurement CSV";                        python3 build_csv.py
sec "Cost model (MODEL)";                     python3 cost_model.py
sec "Power simulation (SIMULATION)";          python3 power_sim.py
sec "Power simulation, larger designs";       python3 power_sim_ext.py
sec "Decisive benchmark harness, dry run (synthetic fixture)"; python3 decisive_benchmark_harness.py --dry-run
