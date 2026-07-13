PYTHON ?= python3

.PHONY: verify test chronology chronology-index chronology-report chronology-verify

verify: chronology-verify
	$(PYTHON) scripts/doctrine_lint.py
	$(PYTHON) scripts/run_decision_scenario_suite.py
	$(MAKE) test PYTHON=$(PYTHON)
	git diff --check

test:
	@for test_file in $$(find tests -name 'test_*.py' | sort); do \
		echo "Running $$test_file"; \
		$(PYTHON) -m pytest -q "$$test_file" || exit 1; \
	done

chronology:
	$(PYTHON) scripts/chronology/validate_chronology.py

chronology-index:
	$(PYTHON) scripts/chronology/build_master_index.py

chronology-report:
	$(PYTHON) scripts/chronology/write_cleanliness_report.py

chronology-verify:
	$(PYTHON) scripts/chronology/validate_chronology.py
	$(PYTHON) scripts/chronology/build_master_index.py
	$(PYTHON) scripts/chronology/write_cleanliness_report.py
