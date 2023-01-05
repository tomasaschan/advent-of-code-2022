#!/bin/bash

day=${1?"usage: $0 <day>"}
input=${2:-'input'}
debug=
if [[ ${3:-''} == "debug" ]]; then
    debug="2> src/dec$day/debug.out"
elif [[ ${3:-''} == "nodebug" ]]; then
    debug="2> /dev/null"
fi

find src/dec$day -type f -name '*.py' -or -name '*.txt' | entr -rc sh -c "echo Running dec $day with $input.txt && ./src/dec$day/solve.py < src/dec$day/$input.txt $debug"
