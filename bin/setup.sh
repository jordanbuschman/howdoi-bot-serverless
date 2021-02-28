#!/bin/bash

PYTHON_VERSION="python3.7"
PYTHON_DIR="src"
BUILD_DIR="build"
LAYERS_DIR="$BUILD_DIR/layers"
OUTPUT_DIR="$BUILD_DIR/output"
SITE_PACKAGES_DIR="$LAYERS_DIR/python/lib/$PYTHON_VERSION/site-packages"
REQUIREMENTS_ZIP_NAME="python_requirements.zip"
PYTHON_ZIP_NAME="lambda_function.zip"

echo "Creating $BUILD_DIR directory structure..."
mkdir -p $SITE_PACKAGES_DIR
mkdir -p $OUTPUT_DIR

echo "Installing requirements in docker..."
docker run -v "$PWD":/var/task "lambci/lambda:build-$PYTHON_VERSION" /bin/sh -c "pip install -r requirements.txt -t $SITE_PACKAGES_DIR"

echo "Zipping up requirements..."
PREV_DIR=$(PWD)
cd $LAYERS_DIR && zip -r $PREV_DIR/$OUTPUT_DIR/$REQUIREMENTS_ZIP_NAME * >> /dev/null && cd -

echo "Zipping up python folder..."
zip -r $OUTPUT_DIR/$PYTHON_ZIP_NAME $PYTHON_DIR/*.py >> /dev/null

echo "Done!"
