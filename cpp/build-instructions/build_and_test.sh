#!/bin/bash

# Build and Test Script for Exercism C++ Projects
# Usage: ./build_and_test.sh <project_directory> [--submit|-s]
# Example: ./build_and_test.sh lasagna
# Example: ./build_and_test.sh lasagna --submit

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse arguments
AUTO_SUBMIT=false
PROJECT_DIR=""

for arg in "$@"; do
    case $arg in
        --submit|-s)
            AUTO_SUBMIT=true
            ;;
        *)
            if [ -z "$PROJECT_DIR" ]; then
                PROJECT_DIR="$arg"
            fi
            ;;
    esac
done

# Check if project directory argument is provided
if [ -z "$PROJECT_DIR" ]; then
    echo -e "${RED}Error: No project directory specified${NC}"
    echo "Usage: $0 <project_directory> [--submit|-s]"
    echo "Example: $0 lasagna"
    echo "Example: $0 lasagna --submit  # Auto-submit after successful tests"
    exit 1
fi

# Get the script's directory and workspace root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
CPP_DIR="$(dirname "$SCRIPT_DIR")"

# Convert to absolute path if relative
if [[ ! "$PROJECT_DIR" = /* ]]; then
    # Try multiple locations for the project
    if [ -d "$PWD/$PROJECT_DIR" ]; then
        # Relative to current working directory
        PROJECT_DIR="$PWD/$PROJECT_DIR"
    elif [ -d "$CPP_DIR/$PROJECT_DIR" ]; then
        # Relative to cpp directory (e.g., "lasagna" -> "cpp/lasagna")
        PROJECT_DIR="$CPP_DIR/$PROJECT_DIR"
    elif [ -d "$WORKSPACE_ROOT/$PROJECT_DIR" ]; then
        # Relative to workspace root (e.g., "cpp/lasagna")
        PROJECT_DIR="$WORKSPACE_ROOT/$PROJECT_DIR"
    else
        # Keep as is and let it fail below with a clear error
        PROJECT_DIR="$WORKSPACE_ROOT/$PROJECT_DIR"
    fi
fi

# Check if project directory exists
if [ ! -d "$PROJECT_DIR" ]; then
    echo -e "${RED}Error: Project directory '$PROJECT_DIR' does not exist${NC}"
    exit 1
fi

# Check if CMakeLists.txt exists
if [ ! -f "$PROJECT_DIR/CMakeLists.txt" ]; then
    echo -e "${RED}Error: CMakeLists.txt not found in '$PROJECT_DIR'${NC}"
    exit 1
fi

# Get the actual project name (handles "." case)
PROJECT_NAME=$(cd "$PROJECT_DIR" && basename "$PWD")

echo -e "${BLUE}==================================================${NC}"
echo -e "${BLUE}Building and Testing: $PROJECT_NAME${NC}"
echo -e "${BLUE}==================================================${NC}"
echo

# Navigate to project directory
cd "$PROJECT_DIR"

# Clean up old build directory
if [ -d "build" ]; then
    echo -e "${YELLOW}Cleaning up old build directory...${NC}"
    rm -rf build
    echo -e "${GREEN}✓ Cleaned${NC}"
    echo
fi

# Create build directory
echo -e "${YELLOW}Creating build directory...${NC}"
mkdir build
cd build
echo -e "${GREEN}✓ Created${NC}"
echo

# Configure with CMake
echo -e "${YELLOW}Configuring project with CMake...${NC}"
if cmake .. > cmake_config.log 2>&1; then
    echo -e "${GREEN}✓ Configuration successful${NC}"
else
    echo -e "${RED}✗ Configuration failed${NC}"
    echo -e "${RED}See cmake_config.log for details${NC}"
    cat cmake_config.log
    exit 1
fi
echo

# Build the project
echo -e "${YELLOW}Building project...${NC}"
if cmake --build . > cmake_build.log 2>&1; then
    echo -e "${GREEN}✓ Build successful${NC}"
else
    echo -e "${RED}✗ Build failed${NC}"
    echo -e "${RED}See cmake_build.log for details${NC}"
    cat cmake_build.log
    exit 1
fi
echo

# Find the executable (usually named after the project directory)
EXECUTABLE="./$PROJECT_NAME"

if [ ! -f "$EXECUTABLE" ]; then
    # Try to find any executable in the build directory (macOS compatible)
    EXECUTABLE=$(find . -maxdepth 1 -type f -perm +111 ! -name "*.dSYM" | head -n 1)
    if [ -z "$EXECUTABLE" ]; then
        echo -e "${RED}Error: No executable found in build directory${NC}"
        exit 1
    fi
fi

# Run tests
echo -e "${BLUE}==================================================${NC}"
echo -e "${BLUE}Running Tests${NC}"
echo -e "${BLUE}==================================================${NC}"
echo

if $EXECUTABLE; then
    echo
    echo -e "${GREEN}==================================================${NC}"
    echo -e "${GREEN}✓ All tests completed successfully!${NC}"
    echo -e "${GREEN}==================================================${NC}"
    
    # Check for Exercism submission
    CONFIG_FILE="$PROJECT_DIR/.exercism/config.json"
    if [ -f "$CONFIG_FILE" ]; then
        # Extract solution files from config.json (only from "solution" array)
        SOLUTION_FILES=$(sed -n '/"solution"/,/\]/p' "$CONFIG_FILE" | grep -o '"[^"]*\.cpp"' | tr -d '"' | tr '\n' ' ')
        
        if [ -n "$SOLUTION_FILES" ]; then
            if [ "$AUTO_SUBMIT" = true ]; then
                # Auto-submit without prompting
                echo
                echo -e "${BLUE}==================================================${NC}"
                echo -e "${BLUE}Submitting to Exercism${NC}"
                echo -e "${BLUE}==================================================${NC}"
                echo -e "${YELLOW}Files: $SOLUTION_FILES${NC}"
                echo
                
                cd "$PROJECT_DIR"
                if exercism submit $SOLUTION_FILES; then
                    echo
                    echo -e "${GREEN}✓ Successfully submitted to Exercism!${NC}"
                else
                    echo
                    echo -e "${RED}✗ Submission failed${NC}"
                    echo -e "${YELLOW}Tip: Make sure exercism CLI is installed and configured${NC}"
                fi
            else
                # Prompt user for submission
                echo
                echo -e "${YELLOW}Submit to Exercism? Files: $SOLUTION_FILES${NC}"
                read -p "Submit? (y/N): " -n 1 -r
                echo
                if [[ $REPLY =~ ^[Yy]$ ]]; then
                    echo -e "${BLUE}Submitting to Exercism...${NC}"
                    cd "$PROJECT_DIR"
                    if exercism submit $SOLUTION_FILES; then
                        echo -e "${GREEN}✓ Successfully submitted!${NC}"
                    else
                        echo -e "${RED}✗ Submission failed${NC}"
                    fi
                else
                    echo -e "${YELLOW}Skipped submission${NC}"
                    echo -e "${YELLOW}Tip: Use --submit flag to auto-submit: $0 $PROJECT_NAME --submit${NC}"
                fi
            fi
        fi
    fi
    
    exit 0
else
    EXIT_CODE=$?
    echo
    echo -e "${RED}==================================================${NC}"
    echo -e "${RED}✗ Tests failed with exit code $EXIT_CODE${NC}"
    echo -e "${RED}==================================================${NC}"
    exit $EXIT_CODE
fi
