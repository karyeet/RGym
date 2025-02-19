#!/bin/bash

# $0 is command
# $1 is hash
# $2 is .config

cd /linux
git checkout $1
echo $2 > .config

make -j`nproc`

cp arch/x86/boot/bzImage /share/bzImage-$1