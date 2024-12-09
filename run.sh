#! /bin/bash

if [[ $(uname -v) == *"NixOS"* ]]; then 
  nix-shell --command "python3 ./home_ims/src/."
else
  python3 ./home_ims/src/.
fi
