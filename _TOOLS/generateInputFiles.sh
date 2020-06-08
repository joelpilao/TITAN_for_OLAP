#!/usr/bin/env bash

find  ../_DATA -name "*.csv" | sed 's/[0-9-]*\-counts.csv$//g' | sort | uniq | sed '/^.*.csv$/d'> inputFileList
