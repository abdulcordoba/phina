#!/bin/bash
source ./randsleep.sh

for i in $*
do
randsleep
python scrape.py $i
done

