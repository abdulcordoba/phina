#!/bin/bash

randsleep() {
    x=$((20 + RANDOM % 10))
    echo "About to sleep $x seconds"
    sleep $x
}
