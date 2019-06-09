#!/bin/bash
split -l 500 nucleos.csv
# bild commands
ls x* | xargs -n 16 echo ./download.sh
