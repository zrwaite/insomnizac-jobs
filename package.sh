#!/bin/bash

set -e  # Exit on error

# Define directories
JOBS_DIR="jobs"
SHARED_DIR="shared"
PACKAGE_DIR="package"
TERRAFORM_DIR="terraform"

# Function to package a single job
build_lambda() {
    JOB_NAME="$1"
    JOB_PATH="$JOBS_DIR/$JOB_NAME"
    ZIP_FILE="$TERRAFORM_DIR/${JOB_NAME}.zip"

    if [ ! -d "$JOB_PATH" ]; then
        echo "Error: Job '$JOB_NAME' does not exist in '$JOBS_DIR'."
        exit 1
    fi

    echo "Building Lambda package for job: $JOB_NAME"

    # Clean up any old package
    rm -rf "$PACKAGE_DIR" "$ZIP_FILE"
    mkdir -p "$PACKAGE_DIR"

    # Install dependencies
    if [ -f "$JOB_PATH/requirements.txt" ]; then
        pip install -r "$JOB_PATH/requirements.txt" -t "$PACKAGE_DIR"
    fi

    # Copy job files
    cp -r "$JOB_PATH"/* "$PACKAGE_DIR"

    # Copy shared folder
    cp -r "$SHARED_DIR" "$PACKAGE_DIR"

    # Copy .env
    cp .env "$PACKAGE_DIR"

    # Zip everything
    cd "$PACKAGE_DIR" || exit
    zip -r "../$ZIP_FILE" .
    cd ..

    # Clean up temp folder
    rm -rf "$PACKAGE_DIR"

    echo "✅ Successfully built: $ZIP_FILE"
}

# Check if a specific job was provided as an argument
if [ "$#" -eq 1 ]; then
    build_lambda "$1"
else
    echo "No specific job provided. Building all jobs in '$JOBS_DIR'..."
    for JOB in "$JOBS_DIR"/*/; do
        JOB_NAME=$(basename "$JOB")
        build_lambda "$JOB_NAME"
    done
fi
