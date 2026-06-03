#!/bin/bash

gen() {
  tr -dc A-Z0-9 </dev/urandom | head -c 4
}

echo "BD-KING-R7-$(gen)-$(gen)-$(gen)"