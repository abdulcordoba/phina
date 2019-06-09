#!/bin/bash
grep INFO file_*.log | cut -c 61- | cut -d, -f2- > todos.csv
