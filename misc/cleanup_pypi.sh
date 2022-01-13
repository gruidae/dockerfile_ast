#!/bin/bash


function init_pwd() {
  cd $(dirname "$0")/.. || exit
}


function main() {
  init_pwd
  rm -rf $(basename $(pwd)).egg-info/* dist/*
}

main
