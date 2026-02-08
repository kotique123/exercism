#!/bin/bash

# Build Module - Handles CMake configuration and compilation
# Usage: ./build.sh <project_directory>

set -e

PROJECT_DIR="$1"

if [ -z "$PROJECT_DIR" ]; then
    echo "Error: No project directory specified"
    exit 1
fi

if [ ! -d "$PROJECT_DIR" ]; then
    echo "Error: Project directory '$PROJECT_DIR' does not exist"
    exit 1
fi

if [ ! -f "$PROJECT_DIR/CMakeLists.txt" ]; then
    echo "Error: CMakeLists.txt not found in '$PROJECT_DIR'"
    exit 1
fi

cd "$PROJECT_DIR"

# Get project name for later use
PROJECT_NAME=$(basename "$PWD")

# Clean and create build directory
rm -rf build
mkdir build
cd build

# Configure with CMake (enable all tests for progressive testing)
if ! cmake -DEXERCISM_RUN_ALL_TESTS=ON .. > cmake_config.log 2>&1; then
    echo "Configuration failed. See build/cmake_config.log"
    cat cmake_config.log
    exit 1
fi

# Build the project (only the executable, skip auto-test target)
if ! cmake --build . --target "$PROJECT_NAME" > cmake_build.log 2>&1; then
    echo "Build failed. See build/cmake_build.log"
    cat cmake_build.log
    exit 1
fi

# Find and return the executable path
if [ -f "./$PROJECT_NAME" ]; then
    echo "./$PROJECT_NAME"
else
    # Find any executable
    EXECUTABLE=$(find . -maxdepth 1 -type f -perm +111 ! -name "*.dSYM" 2>/dev/null | head -n 1)
    if [ -z "$EXECUTABLE" ]; then
        echo "Error: No executable found"
        exit 1
    fi
    echo "$EXECUTABLE"
fi
