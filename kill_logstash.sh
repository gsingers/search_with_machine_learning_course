#!/bin/bash
for p in $(pgrep -f /home/gitpod/.sdkman/candidates/java/current/bin/java)
do
    echo -e "Killing $p"
    kill -9 $p
done