#!/bin/bash

\rm sal.txt

for i in file_x*   
do
    count=$(grep INFO $i | wc -l)
    echo "$i - $count" >> sal.txt
done

grep -v 500 sal.txt

