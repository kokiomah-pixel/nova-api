PYTHON ?= .venv/bin/python

.PHONY: \
	require-venv \
	verify \
	verify-doctrine \
	verify-scenarios \
	verify-tests \
	verify-chronology \
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
	verify-scenarios \
	verify-tests \
	verify-chronology \
	verify-whitespace

verify-doctrine: require-venv
	$(PYTHON) scripts/doctrine_lint.py

verify-scenarios: require-venv
	$(PYTHON) scripts/run_decision_scenario_suite.py

verify-tests: require-venv
	$(PYTHON) -m pytest

verify-chronology: require-venv
	$(MAKE) chronology-verify PYTHON=$(PYTHON)

verify-whitespace:
	git diff --check

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
