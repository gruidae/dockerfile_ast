#!/bin/bash


function init_pwd() {
  cd $(dirname "$0")/.. || exit
}


function main() {
  init_pwd
  pandoc --from markdown --to rst README.md -o README.rst
}

main
