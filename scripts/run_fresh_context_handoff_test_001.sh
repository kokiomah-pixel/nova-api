#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel)"
TEST_ID="fresh-context-handoff-test-001"
WORK_DIR="/tmp/nova-${TEST_ID}"
INPUT_DIR="${WORK_DIR}/input"
OUTPUT_DIR="${WORK_DIR}/output"

PROMPT_SOURCE="${ROOT_DIR}/docs/operations/tests/fresh-context-handoff-test-001-prompt.md"
HANDOFF_SOURCE="${ROOT_DIR}/docs/operations/records/decision-state-handoff-001.md"
STATE_SOURCE="${ROOT_DIR}/docs/operations/current-system-state.md"
AUTHORITY_SOURCE="${ROOT_DIR}/docs/operations/current-authority-and-escalation-map.md"

for file in \
  "${PROMPT_SOURCE}" \
  "${HANDOFF_SOURCE}" \
  "${STATE_SOURCE}" \
  "${AUTHORITY_SOURCE}"
do
  if [ ! -f "${file}" ]; then
    echo "Missing required input: ${file}" >&2
    exit 1
  fi
done

rm -rf "${WORK_DIR}"
mkdir -p "${INPUT_DIR}" "${OUTPUT_DIR}"

cp "${PROMPT_SOURCE}" "${INPUT_DIR}/"
cp "${HANDOFF_SOURCE}" "${INPUT_DIR}/"
cp "${STATE_SOURCE}" "${INPUT_DIR}/"
cp "${AUTHORITY_SOURCE}" "${INPUT_DIR}/"

find "${INPUT_DIR}" -maxdepth 1 -type f -print | sort \
  > "${OUTPUT_DIR}/input-file-list.txt"

INPUT_COUNT="$(find "${INPUT_DIR}" -maxdepth 1 -type f | wc -l | tr -d ' ')"

if [ "${INPUT_COUNT}" != "4" ]; then
  echo "Isolation failure: expected exactly 4 input files, found ${INPUT_COUNT}" >&2
  exit 1
fi

sha256sum "${INPUT_DIR}"/* \
  > "${OUTPUT_DIR}/input-sha256.txt"

{
  echo "# FRESH-CONTEXT HANDOFF TEST 001"
  echo
  echo "# TEST PROMPT"
  cat "${INPUT_DIR}/fresh-context-handoff-test-001-prompt.md"
  echo
  echo "# SOURCE 1 — DECISION-STATE HANDOFF"
  cat "${INPUT_DIR}/decision-state-handoff-001.md"
  echo
  echo "# SOURCE 2 — CURRENT SYSTEM STATE"
  cat "${INPUT_DIR}/current-system-state.md"
  echo
  echo "# SOURCE 3 — AUTHORITY AND ESCALATION MAP"
  cat "${INPUT_DIR}/current-authority-and-escalation-map.md"
} > "${OUTPUT_DIR}/exact-model-input.md"

sha256sum "${OUTPUT_DIR}/exact-model-input.md" \
  > "${OUTPUT_DIR}/exact-model-input-sha256.txt"

cat > "${OUTPUT_DIR}/execution-metadata.yaml" <<EOF
test_session:
  test_id: ${TEST_ID}
  execution_date:
  execution_time_utc:
  executed_by:
  execution_surface: VS_Code
  workspace_path: ${WORK_DIR}

  model:
    provider:
    model_name:
    model_version_if_visible:

  isolation:
    new_session: true
    prior_Nova_context_present: false
    persistent_memory_enabled: false
    repository_workspace_exposed: false
    repository_indexing_enabled: false
    external_tools_enabled: false
    external_tools_used: false
    web_access_enabled: false
    additional_files_supplied: false
    operator_coaching_provided: false

  approved_inputs:
    - fresh-context-handoff-test-001-prompt.md
    - decision-state-handoff-001.md
    - current-system-state.md
    - current-authority-and-escalation-map.md

  evidence:
    input_file_list: output/input-file-list.txt
    input_hashes: output/input-sha256.txt
    exact_model_input: output/exact-model-input.md
    exact_model_input_hash: output/exact-model-input-sha256.txt
    raw_response: output/raw-model-response.md
    raw_response_hash: output/raw-model-response-sha256.txt
EOF

cat > "${OUTPUT_DIR}/raw-model-response.md" <<'EOF'
# Fresh-Context Handoff Test 001 — Raw Model Response

status: pending_execution

Replace only the content below this line with the unedited first model response.

---

PENDING
EOF

cat > "${OUTPUT_DIR}/isolation-attestation.md" <<'EOF'
# Fresh-Context Handoff Test 001 — Isolation Attestation

I attest that this test was executed under the following conditions:

- A new model session was used.
- The session had no prior Sharpe Nova OS conversation history.
- Persistent memory was disabled or unavailable.
- Only the four approved files were supplied.
- The full Sharpe Nova OS repository was not exposed to the model.
- Repository indexing and repository-aware retrieval were disabled.
- Web access and external retrieval were disabled.
- No repository tools, shell tools, or file-search tools were available to the model under test.
- No expected answers were supplied.
- No coaching or corrections were provided during execution.
- The first model response was preserved without editing.
- Input and output hashes were recorded.

```yaml
attestation:
  executed_by:
  execution_date:
  conditions_confirmed:
  contamination_known:
  notes:
```

This attestation records operator-controlled conditions.

It does not cryptographically prove the model provider's hidden internal state.
EOF

echo
echo "Fresh-context test workspace created:"
echo "${WORK_DIR}"
echo
echo "Approved inputs:"
cat "${OUTPUT_DIR}/input-file-list.txt"
echo
echo "Next steps:"
echo "1. Open only this workspace in a new VS Code window."
echo "2. Use output/exact-model-input.md in one clean model request."
echo "3. Save the unedited response to output/raw-model-response.md."
echo "4. Hash the raw response."
echo "5. Complete metadata and isolation attestation."
echo "6. Copy the evidence back into canonical repository result files."
