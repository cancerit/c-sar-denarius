#!/usr/bin/env bash

./tests/scripts/run_unit_tests.sh
exit_unit=$?

pre-commit run --all-files
exit_precommit=$?

! (( $exit_unit || $exit_precommit ))
