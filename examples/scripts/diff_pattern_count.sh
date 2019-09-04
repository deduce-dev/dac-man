#!/bin/bash

set -e

source_a=$1
source_b=$2

pattern="e"

echo "a: $source_a"
echo "b: $source_b"
echo "pattern: \"$pattern\""

count_a=$(grep -o "$pattern" "$source_a" | wc -l)
count_b=$(grep -o "$pattern" "$source_b" | wc -l)

echo "count_a: $count_a"
echo "count_b: $count_b"

difference=$(echo "$count_a" - "$count_b" | bc)
echo "Difference is: $difference"

exit 0
