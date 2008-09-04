#!/bin/sh
[ -d target ] && rm -rf target
mkdir target
cp -r controller target/
cp common/* target/controller
cp -r manager target/
cp common/* target/manager
cp -r webinterface target/
