PY ?= python3

.PHONY: test lint check

test:
	$(PY) -m unittest discover -s tests -v

lint:
	$(PY) -m py_compile bin/ask bin/capture bin/flow plugin/hooks/*.py plugin/statusline/*.py
	for f in raycast/*.sh; do bash -n $$f || exit 1; done
	for f in plugin/hooks/hooks.json plugin/.claude-plugin/plugin.json .claude-plugin/marketplace.json; do $(PY) -m json.tool $$f > /dev/null || exit 1; done

check: lint test
