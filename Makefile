# Content Atlas. JSON is the source; xlsx and md are outputs rendered from it.
# Run `make` to list the targets.

PY ?= python3
L  := tools
RESULT_FLAGS ?=

.DEFAULT_GOAL := help
.PHONY: help build derive derive-place derive-fit-maps derive-recipes derive-transformations derive-template render render-xlsx render-md check check-derived check-xlsx check-md verify schema reference coherence assignments audit audit-all resolve map check-routes filter export-xlsx clean

help: ## list the targets
	@awk 'BEGIN {FS = ":.*## "} /^[a-z-]+:.*## / {printf "  %-16s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build: derive render check ## derive, render, then check that every output equals its JSON

# 1. views inside each vertical
derive: ## recompute every view inside its vertical (writes JSON)
	$(PY) $(L)/derive.py all
derive-place: ## recompute the Full matrix, Compact matrix and Content unit ↔ Recipe
	$(PY) $(L)/derive.py place
derive-fit-maps: ## recompute the 4 derived fit maps from the 7 source maps and the space
	$(PY) $(L)/derive.py fit-maps
derive-recipes: ## recompute Possibilities: what fits each audience at each state
	$(PY) $(L)/derive.py recipes
derive-transformations: ## recompute Candidates, Content unit ↔ Transformation and Content unit ↔ Repurposing
	$(PY) $(L)/derive.py transformations
derive-template: ## recompute the Template counts per state from the recipes and the content units
	$(PY) $(L)/derive.py template


# 3. human-readable outputs
render: ## write every xlsx and md from the JSON
	$(PY) $(L)/render.py all
render-xlsx: ## write every xlsx from its JSON
	$(PY) $(L)/render.py xlsx
render-md: ## write the md beside every JSON table and document, and the spec of each vertical
	$(PY) $(L)/render.py md

# 4. outputs equal the JSON
check: ## strict: xlsx and md equal the JSON, derived values and views current (exit 1 on any difference)
	$(PY) $(L)/check.py
check-derived: ## derived values and views current
	$(PY) $(L)/check.py derived
check-xlsx: ## every xlsx cell equals the JSON
	$(PY) $(L)/check.py xlsx
check-md: ## every md equals its JSON
	$(PY) $(L)/check.py md

# 5. verdicts over the models
verify: schema reference coherence assignments audit ## run every check
schema: ## Full matrix against the rules in content-units.json: header, required values, allowed values
	$(PY) $(L)/schema.py
reference: ## ID prefixes, counts, next IDs, ID integrity, channel vocabularies
	$(PY) $(L)/reference.py
coherence: ## every pair of values in content units and recipe options against the fit maps
	$(PY) $(L)/coherence.py
assignments: ## each content unit's Recipe against that recipe: state and track
	$(PY) $(L)/assignments.py
audit: ## inventory and audit steps 1-8 for the Catalog
	$(PY) $(L)/audit.py
audit-all: ## audit across every product
	$(PY) $(L)/audit.py --product All

# 6. the worker's program operations (contracts/inputs.md, contracts/outputs.md)
resolve: ## steps and links reachable from REQUEST's anchors → artifacts/<name>/
	$(PY) $(L)/possibilities.py resolve $(REQUEST) $(RESULT_FLAGS)
map: ## existing pieces in REQUEST placed and checked, then steps and links from them → artifacts/<name>/
	$(PY) $(L)/possibilities.py map $(REQUEST) $(RESULT_FLAGS)
check-routes: ## check the composed routes in RESULT/routes.json and add them to RESULT
	$(PY) $(L)/possibilities.py check $(RESULT) $(RESULT_FLAGS)
filter: ## narrow RESULT by PARAMS into a new artifact
	$(PY) $(L)/possibilities.py filter $(RESULT) $(PARAMS) $(RESULT_FLAGS)

export-xlsx: ## render RESULT's workbook from saved JSON, without recomputing possibilities
	$(PY) $(L)/possibilities.py export-xlsx $(RESULT)

clean: ## remove Python caches
	rm -rf $(L)/__pycache__ $(L)/__pycache__
