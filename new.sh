#!/bin/bash

day=${1?"usage: $0 <day>"}

mkdir -p src/dec$day
echo "#!/usr/bin/env python3" > src/dec$day/solve.py
chmod +x src/dec$day/solve.py
touch src/dec$day/input.txt
touch src/dec$day/example.txt
