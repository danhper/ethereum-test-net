#!/bin/bash

TARDIR=geth-alltools-linux-amd64-1.8.17-8bbe7207
# TARDIR=geth-alltools-linux-amd64-1.8.18-unstable-cdf5982c
TARFILE=$TARDIR.tar.gz

if ! [ -f "$TARFILE" ]; then
  wget https://gethstore.blob.core.windows.net/builds/$TARFILE
fi

if ! [ -d "$TARDIR" ]; then
  tar xvzf $TARFILE
fi

if ! [ -f "bootnode" ]; then
  cp "$TARDIR/bootnode" .
fi
