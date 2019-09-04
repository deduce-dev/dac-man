#!/bin/bash

echo "------- Start test: simple --------"

echo "*** Dac-Man diff (filesystem-level) data directories ***"
dacman diff data/simple/v0 data/simple/v1

sleep 2

echo "*** Dac-Man diff (data-level) data directories ***"
dacman diff data/simple/v0 data/simple/v1 --datachange --script /usr/bin/diff

echo "------- End test: simple --------"




