#!/bin/bash

PYTHON_VERSION="python3.7"
BUILD_DIR="build"
LAYERS_DIR="$BUILD_DIR/layers"
OUTPUT_DIR="$BUILD_DIR/output"
SITE_PACKAGES_DIR="$LAYERS_DIR/python/lib/$PYTHON_VERSION/site-packages"
ZIP_NAME="python_requirements.zip"

echo "Creating $BUILD_DIR directory structure..."
mkdir -p $SITE_PACKAGES_DIR
mkdir -p $OUTPUT_DIR

echo "Installing requirements in docker..."
docker run -v "$PWD":/var/task "lambci/lambda:build-$PYTHON_VERSION" /bin/sh -c "pip install -r requirements.txt -t $SITE_PACKAGES_DIR"

echo "Zipping up requirements..."
PREV_DIR=$(PWD)
cd $LAYERS_DIR && zip -r $PREV_DIR/$OUTPUT_DIR/$ZIP_NAME * >> /dev/null && cd -

echo "Done!"