#!/usr/bin/env python3
"""
Run Fresh-Context Handoff Test 001 as one unlinked OpenAI Responses API request.

This script:
- reads only the prepared exact-model-input.md file
- makes one API request
- defines no tools
- sends no previous_response_id
- sends no conversation identifier
- sets store=False
- preserves the request metadata
- preserves the complete API response
- extracts and preserves the first model answer
- records SHA-256 hashes

It does not score the answer.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TEST_ID = "fresh-context-handoff-test-001"
WORK_DIR = Path(
    os.environ.get(
        "NOVA_TEST_WORK_DIR",
        f"{os.environ.get('TMPDIR', '/tmp').rstrip('/')}/nova-{TEST_ID}",
    )
).resolve()

OUTPUT_DIR = WORK_DIR / "output"
EXACT_INPUT_FILE = OUTPUT_DIR / "exact-model-input.md"

REQUEST_RECORD_FILE = OUTPUT_DIR / "api-request-record.json"
API_RESPONSE_FILE = OUTPUT_DIR / "api-response.json"
RAW_RESPONSE_FILE = OUTPUT_DIR / "raw-model-response.md"
RAW_RESPONSE_HASH_FILE = OUTPUT_DIR / "raw-model-response-sha256.txt"
REQUEST_HASH_FILE = OUTPUT_DIR / "api-request-record-sha256.txt"
EXECUTION_RECEIPT_FILE = OUTPUT_DIR / "execution-receipt.yaml"

API_URL = "https://api.openai.com/v1/responses"


class TestExecutionError(RuntimeError):
    """Raised when the isolated request cannot be completed safely."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def fail(message: str, exit_code: int = 1) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(exit_code)


def require_environment_variable(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        fail(f"{name} is not set.")
    return value


def extract_output_text(response_data: dict[str, Any]) -> str:
    """
    Extract assistant text from the Responses API payload.

    The helper first checks output_text when present, then walks output items.
    """
    direct_text = response_data.get("output_text")
    if isinstance(direct_text, str) and direct_text.strip():
        return direct_text.strip()

    text_parts: list[str] = []

    output_items = response_data.get("output", [])
    if not isinstance(output_items, list):
        return ""

    for item in output_items:
        if not isinstance(item, dict):
            continue

        content_items = item.get("content", [])
        if not isinstance(content_items, list):
            continue

        for content in content_items:
            if not isinstance(content, dict):
                continue

            text = content.get("text")
            if isinstance(text, str) and text.strip():
                text_parts.append(text.strip())

    return "\n\n".join(text_parts).strip()


def verify_preconditions() -> None:
    if not WORK_DIR.is_dir():
        raise TestExecutionError(f"Isolated workspace does not exist: {WORK_DIR}")

    if not OUTPUT_DIR.is_dir():
        raise TestExecutionError(f"Output directory does not exist: {OUTPUT_DIR}")

    if not EXACT_INPUT_FILE.is_file():
        raise TestExecutionError(f"Prepared exact input is missing: {EXACT_INPUT_FILE}")

    exact_input = EXACT_INPUT_FILE.read_text(encoding="utf-8")

    if not exact_input.strip():
        raise TestExecutionError("Exact model input is empty.")

    if "Fresh-Context Handoff Test 001" not in exact_input:
        raise TestExecutionError(
            "Exact input does not appear to contain the approved test prompt."
        )

    prior_result_files = [
        API_RESPONSE_FILE,
        RAW_RESPONSE_HASH_FILE,
        EXECUTION_RECEIPT_FILE,
    ]

    existing_results = [str(path) for path in prior_result_files if path.exists()]

    if existing_results and os.environ.get("NOVA_ALLOW_TEST_OVERWRITE") != "true":
        raise TestExecutionError(
            "Execution evidence already exists. Refusing to overwrite:\n- "
            + "\n- ".join(existing_results)
            + "\nSet NOVA_ALLOW_TEST_OVERWRITE=true only for an approved rerun."
        )


def build_payload(model: str, exact_input: str) -> dict[str, Any]:
    return {
        "model": model,
        "instructions": (
            "Follow the supplied test instructions exactly. "
            "Use only the content in the user input. "
            "Do not use outside knowledge, prior conversation context, "
            "web access, tools, retrieval, or unstated project context. "
            "If the supplied material does not answer a question, "
            "state that the context is insufficient."
        ),
        "input": exact_input,
        "tools": [],
        "tool_choice": "none",
        "store": False,
    }


def write_request_record(
    *,
    payload: dict[str, Any],
    exact_input_hash: str,
    started_at: str,
) -> None:
    """
    Preserve the request structure without storing the API key.

    The complete prompt already exists in exact-model-input.md, so the request
    record stores its hash rather than duplicating the full text.
    """
    safe_record = {
        "test_id": TEST_ID,
        "started_at_utc": started_at,
        "endpoint": API_URL,
        "request_method": "POST",
        "model": payload["model"],
        "instructions": payload["instructions"],
        "input_source": str(EXACT_INPUT_FILE),
        "input_sha256": exact_input_hash,
        "tools": payload["tools"],
        "tool_choice": payload["tool_choice"],
        "store": payload["store"],
        "previous_response_id_supplied": False,
        "conversation_id_supplied": False,
        "prior_messages_supplied": False,
        "authorization_header_recorded": False,
    }

    encoded = json.dumps(safe_record, indent=2, sort_keys=True).encode("utf-8")

    REQUEST_RECORD_FILE.write_bytes(encoded)

    REQUEST_HASH_FILE.write_text(
        f"{sha256_bytes(encoded)}  {REQUEST_RECORD_FILE.name}\n",
        encoding="utf-8",
    )


def make_request(
    *,
    api_key: str,
    payload: dict[str, Any],
) -> tuple[int, str]:
    body = json.dumps(payload).encode("utf-8")

    http_request = urllib.request.Request(
        API_URL,
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(http_request, timeout=300) as response:
            status_code = int(response.status)
            response_body = response.read().decode("utf-8")
            return status_code, response_body

    except urllib.error.HTTPError as exc:
        response_body = exc.read().decode("utf-8", errors="replace")

        technical_failure_file = OUTPUT_DIR / "api-technical-failure.txt"
        technical_failure_file.write_text(
            (
                f"HTTP status: {exc.code}\n"
                f"Reason: {exc.reason}\n\n"
                f"{response_body}"
            ),
            encoding="utf-8",
        )

        raise TestExecutionError(
            f"OpenAI API returned HTTP {exc.code}. "
            f"Technical failure preserved at {technical_failure_file}"
        ) from exc

    except urllib.error.URLError as exc:
        raise TestExecutionError(f"Network error before model response: {exc.reason}") from exc

    except TimeoutError as exc:
        raise TestExecutionError(
            "Request timed out before a model response was preserved."
        ) from exc


def write_raw_response(
    *,
    output_text: str,
    model: str,
    response_id: str,
    completed_at: str,
) -> str:
    raw_record = f"""# Fresh-Context Handoff Test 001 - Raw Model Response

## Status

```yaml
status: completed
```

## Execution Reference

```yaml
test_id: {TEST_ID}
execution_time_utc: {completed_at}
model: {model}
response_id: {response_id}
request_count: 1
response_regenerated: false
```

## Raw Response

The content below is the first model response and must not be edited.

---

{output_text}
"""

    RAW_RESPONSE_FILE.write_text(raw_record, encoding="utf-8")

    digest = sha256_file(RAW_RESPONSE_FILE)

    RAW_RESPONSE_HASH_FILE.write_text(
        f"{digest}  {RAW_RESPONSE_FILE.name}\n",
        encoding="utf-8",
    )

    return digest


def write_execution_receipt(
    *,
    started_at: str,
    completed_at: str,
    model: str,
    http_status: int,
    response_id: str,
    exact_input_hash: str,
    raw_response_hash: str,
) -> None:
    receipt = f"""test_session:
  test_id: {TEST_ID}
  execution_started_utc: {started_at}
  execution_completed_utc: {completed_at}
  execution_surface: VS_Code_stateless_API_request
  isolated_workspace: {WORK_DIR}

model:
  provider: OpenAI
  model_name: {model}
  response_id: {response_id}

request_controls:
  request_count: 1
  prior_messages_supplied: false
  previous_response_id_supplied: false
  conversation_id_supplied: false
  tools_defined: false
  tool_choice: none
  store: false
  repository_workspace_exposed_to_model: false
  repository_indexing_exposed_to_model: false
  web_access_supplied: false
  external_retrieval_supplied: false
  additional_files_supplied: false
  expected_answers_supplied: false
  operator_coaching_supplied: false
  response_regenerated: false

transport:
  endpoint: {API_URL}
  http_status: {http_status}

evidence:
  exact_input_file: {EXACT_INPUT_FILE}
  exact_input_sha256: {exact_input_hash}
  request_record_file: {REQUEST_RECORD_FILE}
  request_record_sha256_file: {REQUEST_HASH_FILE}
  full_api_response_file: {API_RESPONSE_FILE}
  raw_response_file: {RAW_RESPONSE_FILE}
  raw_response_sha256: {raw_response_hash}
"""

    EXECUTION_RECEIPT_FILE.write_text(receipt, encoding="utf-8")


def main() -> None:
    try:
        verify_preconditions()

        api_key = require_environment_variable("OPENAI_API_KEY")
        model = require_environment_variable("OPENAI_MODEL")

        exact_input = EXACT_INPUT_FILE.read_text(encoding="utf-8")
        exact_input_hash = sha256_file(EXACT_INPUT_FILE)
        started_at = datetime.now(timezone.utc).isoformat()

        payload = build_payload(model, exact_input)

        write_request_record(
            payload=payload,
            exact_input_hash=exact_input_hash,
            started_at=started_at,
        )

        http_status, response_body = make_request(
            api_key=api_key,
            payload=payload,
        )

        API_RESPONSE_FILE.write_text(response_body, encoding="utf-8")

        try:
            response_data = json.loads(response_body)
        except json.JSONDecodeError as exc:
            raise TestExecutionError(
                f"API response was not valid JSON. Raw response preserved at {API_RESPONSE_FILE}"
            ) from exc

        output_text = extract_output_text(response_data)

        if not output_text:
            raise TestExecutionError(
                f"No model text was found. Complete API response preserved at {API_RESPONSE_FILE}"
            )

        completed_at = datetime.now(timezone.utc).isoformat()
        response_id = str(response_data.get("id", "not_exposed"))

        raw_response_hash = write_raw_response(
            output_text=output_text,
            model=model,
            response_id=response_id,
            completed_at=completed_at,
        )

        write_execution_receipt(
            started_at=started_at,
            completed_at=completed_at,
            model=model,
            http_status=http_status,
            response_id=response_id,
            exact_input_hash=exact_input_hash,
            raw_response_hash=raw_response_hash,
        )

        print()
        print("Fresh-Context Handoff Test 001 request completed.")
        print(f"Workspace: {WORK_DIR}")
        print(f"Model: {model}")
        print(f"Response ID: {response_id}")
        print(f"Raw response: {RAW_RESPONSE_FILE}")
        print(f"Raw response hash: {RAW_RESPONSE_HASH_FILE}")
        print(f"API response: {API_RESPONSE_FILE}")
        print(f"Execution receipt: {EXECUTION_RECEIPT_FILE}")
        print()
        print("Do not rerun the request before scoring the preserved result.")

    except TestExecutionError as exc:
        fail(str(exc))


if __name__ == "__main__":
    main()
