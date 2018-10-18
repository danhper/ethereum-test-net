#!/bin/bash

TARDIR=geth-alltools-linux-amd64-1.8.18-unstable-cdf5982c
TARFILE=$TARDIR.tar.gz

if ! [ -f "$TARFILE" ]; then
  wget https://gethstore.blob.core.windows.net/builds/geth-alltools-linux-amd64-1.8.18-unstable-cdf5982c.tar.gz
fi

if ! [ -d "$TARDIR" ]; then
  tar xvzf geth-alltools-linux-amd64-1.8.18-unstable-cdf5982c.tar.gz
fi

if ! [ -f "bootnode" ]; then
  cp "$TARDIR/bootnode" .
fi
