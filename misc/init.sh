#!/bin/bash


function init_pwd() {
  cd $(dirname "$0")/.. || exit
}


function main() {
  init_pwd
}

main
