PYTHON ?= .venv/bin/python

.PHONY: \
	require-venv \
	verify \
	verify-doctrine \
	verify-cco-operating-spine \
	verify-arc-market-signal-watch \
	verify-market-signal-scan \
	verify-scenarios \
	verify-tests \
	verify-chronology \
	verify-public-surface \
	verify-whitespace \
	test \
	test-isolated \
	chronology \
	chronology-index \
	chronology-report \
	chronology-verify

require-venv:
	@test -x "$(PYTHON)" || \
	  (echo "Repository Python not found: $(PYTHON)" >&2; \
	   echo "Run the repository bootstrap command first." >&2; \
	   exit 1)

verify: \
	verify-doctrine \
	verify-cco-operating-spine \
	verify-arc-market-signal-watch \
	verify-market-signal-scan \
	verify-scenarios \
	verify-tests \
	verify-chronology \
	verify-public-surface \
	verify-whitespace

verify-doctrine: require-venv
	$(PYTHON) scripts/doctrine_lint.py

verify-cco-operating-spine: require-venv
	$(PYTHON) scripts/validate_cco_operating_spine.py

verify-arc-market-signal-watch: require-venv
	$(PYTHON) scripts/validate_arc_market_signal_watch.py

verify-market-signal-scan: require-venv
	$(PYTHON) scripts/validate_market_signal_scan_coverage.py

verify-scenarios: require-venv
	$(PYTHON) scripts/run_decision_scenario_suite.py

verify-tests: require-venv
	$(PYTHON) -m pytest

verify-chronology: require-venv
	$(MAKE) chronology-verify PYTHON=$(PYTHON)

verify-whitespace:
	git diff --check

verify-public-surface: require-venv
	$(PYTHON) scripts/validate_public_surface_coherence.py

test: verify-tests

test-isolated: require-venv
	@for test_file in $$(find tests -name 'test_*.py' | sort); do \
		echo "Running $$test_file"; \
		$(PYTHON) -m pytest -q "$$test_file" || exit 1; \
	done

chronology: require-venv
	$(PYTHON) scripts/chronology/validate_chronology.py

chronology-index: require-venv
	$(PYTHON) scripts/chronology/build_master_index.py

chronology-report: require-venv
	$(PYTHON) scripts/chronology/write_cleanliness_report.py

chronology-verify: require-venv
	$(PYTHON) scripts/chronology/validate_chronology.py
	$(PYTHON) scripts/chronology/build_master_index.py
	$(PYTHON) scripts/chronology/write_cleanliness_report.py
