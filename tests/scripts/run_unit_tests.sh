#!/usr/bin/env bash

pytest tests/ -x --no-cov-on-fail --cov=c_sar_denarius --cov-report term --cov-report html --junitxml=junit.xml
