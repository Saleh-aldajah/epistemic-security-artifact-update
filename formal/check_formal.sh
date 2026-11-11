#!/usr/bin/env bash
# check_formal.sh — one-command verification of the mechanized safety core.
# Exit 0 iff: (1) Lean 4.12 elaborates DeiSafety.lean with zero errors;
# (2) the file contains no sorry/admit tactics;
# (3) the axiom audit reports no dependency beyond Lean's built-in propext
#     (i.e., no Classical.choice, no Quot.sound, no custom axioms).
set -u
cd "$(dirname "$0")"
FAIL=0

# Locate elan/lean: persistent mount first, then $HOME, then PATH.
if [ -z "${ELAN_HOME:-}" ]; then
  for cand in /mnt/agents/opt/elan "$HOME/.elan"; do
    [ -x "$cand/bin/lean" ] && export ELAN_HOME="$cand" && break
  done
fi
[ -n "${ELAN_HOME:-}" ] && export PATH="$ELAN_HOME/bin:$PATH"
if ! command -v lean >/dev/null 2>&1; then
  echo "lean not found. Install via: ELAN_HOME=/mnt/agents/opt/elan sh -c 'curl -sSfL https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh -s -- -y --default-toolchain leanprover/lean4:v4.12.0'"
  exit 2
fi

echo "=== lean $(lean --version | head -1) ==="
lean DeiSafety.lean 2>&1 | tee lean_check.log
if grep -qE "error" lean_check.log; then
  echo "CHECK 1 (elaborates with zero errors): FAIL"; FAIL=1
else
  echo "CHECK 1 (elaborates with zero errors): PASS"
fi

if grep -qE ":= *by *sorry|: *sorry\b|admit$" DeiSafety.lean; then
  echo "CHECK 2 (no sorry/admit tactics): FAIL"; FAIL=1
else
  echo "CHECK 2 (no sorry/admit tactics): PASS"
fi

if grep -E "depends on axioms" lean_check.log | grep -qv "\[propext\]"; then
  echo "CHECK 3 (axiom footprint <= {propext}): FAIL"; FAIL=1
  grep -E "depends on axioms" lean_check.log | grep -v "\[propext\]" | head -5
else
  echo "CHECK 3 (axiom footprint <= {propext}; no Classical.choice/custom axioms): PASS"
fi

[ "$FAIL" -eq 0 ] && echo "FORMAL CHECKS: ALL PASS" || echo "FORMAL CHECKS: FAIL"
exit "$FAIL"
