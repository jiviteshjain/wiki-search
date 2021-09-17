#!/bin/bash
python3 src-en/main.py --action='search' --index="$1" --queries="$2" --results="$3"
