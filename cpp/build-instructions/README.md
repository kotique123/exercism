# Build and Test Script Documentation

## Overview

This script automates the build and test process for Exercism C++ projects using CMake. It provides a clean, colored terminal output showing the status of each step.

## Features

- ✅ Automatic project building with CMake
- ✅ Clean build directory management
- ✅ Colored terminal output for easy status tracking
- ✅ Automatic test execution
- ✅ Clear error reporting with log files
- ✅ **Automatic Exercism submission** (optional)
- ✅ Works with any Exercism C++ project that uses CMake

## Prerequisites

- **CMake**: Must be installed on your system
  ```bash
  brew install cmake  # macOS
  ```
- **C++ Compiler**: clang++ or g++
- **Project Structure**: Project must have a `CMakeLists.txt` file
- **Exercism CLI** (optional): For automatic submission feature
  ```bash
  brew install exercism  # macOS
  ```

## Installation

1. The script is located in the `cpp/build-instructions` directory
2. Make the script executable:
   ```bash
   chmod +x cpp/build-instructions/build_and_test.sh
   ```

## Usage

### Basic Usage

```bash
./cpp/build-instructions/build_and_test.sh <project_directory> [--submit|-s]
```

**Flags:**
- `--submit` or `-s`: Automatically submit to Exercism after successful tests (no prompt)

### Examples

**Build and test only:**
```bash
./cpp/build-instructions/build_and_test.sh lasagna
```

**Build, test, and prompt for submission:**
```bash
./cpp/build-instructions/build_and_test.sh lasagna
# After tests pass, you'll be prompted: "Submit to Exercism? (y/N)"
```

**Build, test, and auto-submit:**
```bash
./cpp/build-instructions/build_and_test.sh lasagna --submit
```

Or with full path:
```bash
./cpp/build-instructions/build_and_test.sh cpp/lasagna -s
```

Build from the project directory:
```bash
cd cpp/lasagna
../build-instructions/build_and_test.sh .
```

Build from the cpp directory:
```bash
cd cpp
./build-instructions/build_and_test.sh lasagna
```

## What the Script Does

1. **Validates Input**
   - Checks if project directory is provided
   - Verifies the directory exists
   - Confirms `CMakeLists.txt` is present

2. **Cleans Build Directory**
   - Removes old `build/` directory if it exists
   - Ensures a fresh build every time

3. **Configures Project**
   - Creates new `build/` directory
   - Runs `cmake ..` to configure the project
   - Saves configuration log to `cmake_config.log`

4. **Builds Project**
   - Compiles all source files
   - Links the executable
   - Saves build log to `cmake_build.log`

5. **Runs Tests**
   - Automatically finds and executes the test executable
   - Displays test output in real-time
   - Reports success or failure with color coding

6. **Submits to Exercism** (if enabled)
   - Reads `.exercism/config.json` to find solution files
   - Prompts for submission confirmation (unless `--submit` flag used)
   - Automatically submits using `exercism submit` command
   - Shows submission status

## Output

The script uses colored output for clarity:

- 🔵 **Blue**: Section headers and information
- 🟡 **Yellow**: In-progress operations
- 🟢 **Green**: Successful operations
- 🔴 **Red**: Errors and failures

### Example Success Output

```
==================================================
Building and Testing: lasagna
==================================================

Cleaning up old build directory...
✓ Cleaned

Creating build directory...
✓ Created

Configuring project with CMake...
✓ Configuration successful

Building project...
✓ Build successful

==================================================
Running Tests
==================================================

===============================================================================
All tests passed (1 assertion in 1 test case)

==================================================
✓ All tests completed successfully!
==================================================

Submit to Exercism? Files: lasagna.cpp
Submit? (y/N): y
Submitting to Exercism...
✓ Successfully submitted!
```

## Error Handling

If any step fails:
- The script stops immediately (fail-fast)
- Error message is displayed in red
- Relevant log file is shown
- Non-zero exit code is returned

### Example Error Output

```
Error: Project directory 'cpp/missing' does not exist
```

## Log Files

When build or configuration fails, log files are created in the `build/` directory:
- `cmake_config.log`: CMake configuration output
- `cmake_build.log`: Build process output

## Exercism Submission

### How It Works

After successful tests, the script automatically detects if the project is an Exercism exercise by checking for `.exercism/config.json`. It then:

1. **Reads the config file** to find solution files (specified in `"files.solution"` array)
2. **Prompts for submission** (unless `--submit` flag is used)
3. **Submits to Exercism** using the `exercism submit` command

### Submission Modes

**Interactive Mode (default):**
```bash
./cpp/build-instructions/build_and_test.sh lasagna
# After tests pass, you'll see:
# Submit to Exercism? Files: lasagna.cpp
# Submit? (y/N): 
```

**Auto-submit Mode:**
```bash
./cpp/build-instructions/build_and_test.sh lasagna --submit
# Automatically submits without prompting
```

**Skip Submission:**
- Press `N` or just hit Enter when prompted
- Or don't use the `--submit` flag and answer 'n' to the prompt

### Requirements

- **Exercism CLI** must be installed and configured
  ```bash
  brew install exercism  # macOS
  exercism configure --token=<your-token>
  ```
- Project must have `.exercism/config.json` with solution files defined

### Example config.json

```json
{
  "files": {
    "solution": [
      "lasagna.cpp"
    ],
    "test": [
      "lasagna_test.cpp"
    ]
  }
}
```

## Troubleshooting

### "No project directory specified"
**Problem**: Script called without arguments  
**Solution**: Provide the project directory path
```bash
./cpp/build-instructions/build_and_test.sh lasagna
```

### "CMakeLists.txt not found"
**Problem**: Project directory doesn't contain CMakeLists.txt  
**Solution**: Ensure you're pointing to a valid Exercism C++ project

### "Configuration failed"
**Problem**: CMake configuration error  
**Solution**: Check `build/cmake_config.log` for details

### "Build failed"
**Problem**: Compilation or linking error  
**Solution**: Check `build/cmake_build.log` for compiler errors

### "No executable found"
**Problem**: Build succeeded but no executable created  
**Solution**: Check CMakeLists.txt configuration

## Manual Build (Alternative)

If you prefer to build manually:

```bash
cd cpp/lasagna
mkdir build && cd build
cmake ..
cmake --build .
./lasagna
```

## Tips

1. **Clean Builds**: The script always does a clean build, removing old artifacts
2. **Quick Testing**: Run this script after making code changes to verify everything works
3. **CI/CD**: This script is suitable for continuous integration pipelines
4. **Multiple Projects**: Use it on any Exercism C++ project in the workspace

## Script Location

```
exercism/
└── cpp/
    ├── build-instructions/
    │   ├── build_and_test.sh    # The build script
    │   └── README.md            # This file
    └── lasagna/                 # Example project
        ├── CMakeLists.txt
        ├── lasagna.cpp
        └── lasagna_test.cpp
```

## Exit Codes

- `0`: Success - all tests passed
- `1`: Error - build failed or tests failed
- Non-zero: Test execution returned an error

## License

This script is part of your Exercism workspace and can be freely modified for your needs.
