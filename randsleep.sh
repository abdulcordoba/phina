#!/bin/bash

randsleep() {
    x=$(jot -r 1 20 30)
    echo "About to sleep $x seconds"
    sleep $x
}
