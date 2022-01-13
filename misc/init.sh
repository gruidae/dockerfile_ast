#!/bin/bash


function init_pwd() {
  cd $(dirname $0)/..
  # pwd 1>&2
}


function main() {
  init_pwd
}

main
