#!/bin/bash
cd "$(dirname "$0")/.."
python3 run.py setup
python3 run.py ui
