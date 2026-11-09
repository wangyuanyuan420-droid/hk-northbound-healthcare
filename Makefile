# The public repository deliberately excludes raw/full-text research material.
# Run `make public-check` before publishing. The full workflow remains only in
# the local-only research archive.

PY = python3

.PHONY: public-check clean

public-check:
	$(PY) -B scripts/validate_public_release.py

clean:
	rm -f figures/*.png figures/*.html
