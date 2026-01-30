#!/usr/bin/env bash

if [ -d .venv ]; then
    source .venv/bin/activate
else
    source .direnv/python*/bin/activate
fi

$@
