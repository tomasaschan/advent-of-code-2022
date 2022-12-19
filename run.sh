#!/bin/bash

day=${1?"usage: $0 <day>"}

find src/dec$day -type f | entr -rc sh -c "./src/dec$day/solve.py < src/dec$day/input.txt"
