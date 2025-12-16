#!/bin/sh

PACKAGE_NAME=censys-platform-soar

if ! soarapps package build --output-file $PACKAGE_NAME.tgz; then
    echo "Failed to build package"
    return 1
fi

echo "Unpacking manifest..."
if ! tar xzf $PACKAGE_NAME.tgz; then
    echo "Failed to unpack manifest."
    return 1
fi

echo "Fixing manifest dependencies..."
if ! python ./fix_manifest.py; then
    echo "Failed to fix manifest dependencies."
    return 1
fi

echo "Repacking manifest..."
if ! tar -cvzf $PACKAGE_NAME.tgz $PACKAGE_NAME; then
    echo "Failed to fix manifest dependencies."
    return 1
fi

echo "Cleaning unpacked directory..."
if ! rm -rf ./$PACKAGE_NAME/; then
    echo "Failed to clean up unpacked directory."
    return 1
fi

echo "Done."
