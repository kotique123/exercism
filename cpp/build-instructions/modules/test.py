#!/usr/bin/env python3
"""
Test Module - Handles progressive test execution using Catch2 tags
Runs tests incrementally by task tags without rebuilding
"""

import subprocess
import sys
import re
from pathlib import Path
from typing import List, Tuple, Optional


class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'


def extract_test_tags(test_file: Path) -> List[str]:
    """Extract test tags from the test file (e.g., [task_1], [task_2])"""
    if not test_file.exists():
        return []
    
    tags = set()
    tag_pattern = re.compile(r'\[task_(\d+)\]')
    
    with open(test_file, 'r') as f:
        for line in f:
            matches = tag_pattern.findall(line)
            for match in matches:
                tags.add(f"task_{match}")
    
    # Sort by task number
    sorted_tags = sorted(tags, key=lambda x: int(x.split('_')[1]))
    return sorted_tags


def run_tests_by_tag(executable: Path, tag: str) -> Tuple[bool, str]:
    """Run tests with a specific tag using Catch2's tag filtering"""
    try:
        # Use Catch2's tag syntax to run specific tests
        result = subprocess.run(
            [str(executable), f"[{tag}]", "-s"],  # -s shows successful assertions
            cwd=executable.parent,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        output = result.stdout + result.stderr
        success = result.returncode == 0
        
        return success, output
    
    except subprocess.TimeoutExpired:
        return False, "Test execution timed out"
    except Exception as e:
        return False, f"Error running tests: {str(e)}"


def run_all_tests(executable: Path) -> Tuple[bool, str]:
    """Run all tests without filtering"""
    try:
        result = subprocess.run(
            [str(executable)],
            cwd=executable.parent,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        output = result.stdout + result.stderr
        success = result.returncode == 0
        
        return success, output
    
    except subprocess.TimeoutExpired:
        return False, "Test execution timed out"
    except Exception as e:
        return False, f"Error running tests: {str(e)}"


def progressive_test(project_dir: Path, executable: Path, task_filter: Optional[List[str]] = None) -> bool:
    """
    Run tests progressively - start with task_1, then add more tasks until failure
    Returns True if all tests pass, False otherwise
    
    Args:
        project_dir: Project directory path
        executable: Path to test executable
        task_filter: Optional list of specific tasks to run (e.g., ['task_1', 'task_2'])
    """
    # Find test file
    test_files = list(project_dir.glob("*_test.cpp"))
    if not test_files:
        print(f"{Colors.RED}Error: No test file found{Colors.NC}")
        return False
    
    test_file = test_files[0]
    tags = extract_test_tags(test_file)
    
    # Apply task filter if specified
    if task_filter:
        original_tags = tags[:]
        tags = [tag for tag in tags if tag in task_filter]
        if not tags:
            print(f"{Colors.RED}Error: None of the specified tasks found in test file{Colors.NC}")
            print(f"{Colors.YELLOW}Available tasks: {', '.join(original_tags)}{Colors.NC}")
            print(f"{Colors.YELLOW}Requested tasks: {', '.join(task_filter)}{Colors.NC}")
            return False
        print(f"{Colors.BLUE}Running only specified tasks: {', '.join(tags)}{Colors.NC}\n")
    
    if not tags:
        # No tags found, just run all tests normally
        print(f"{Colors.YELLOW}No task tags found, running all tests...{Colors.NC}")
        success, output = run_all_tests(executable)
        print(output)
        return success
    
    print(f"{Colors.BLUE}{'='*50}{Colors.NC}")
    print(f"{Colors.BLUE}Progressive Test Execution{Colors.NC}")
    print(f"{Colors.BLUE}Found {len(tags)} test tasks{Colors.NC}")
    print(f"{Colors.BLUE}{'='*50}{Colors.NC}")
    print()
    
    passed_tasks = []
    
    for i, tag in enumerate(tags, 1):
        print(f"{Colors.YELLOW}[{i}/{len(tags)}] Running {tag}...{Colors.NC}")
        
        success, output = run_tests_by_tag(executable, tag)
        
        if success:
            # Extract test count from output
            match = re.search(r'(\d+) test case[s]?', output)
            test_count = match.group(1) if match else "?"
            
            match = re.search(r'(\d+) assertion[s]?', output)
            assertion_count = match.group(1) if match else "?"
            
            print(f"{Colors.GREEN}✓ {tag} passed ({assertion_count} assertions in {test_count} test case(s)){Colors.NC}")
            passed_tasks.append(tag)
        else:
            print(f"{Colors.RED}✗ {tag} failed{Colors.NC}")
            print()
            print(f"{Colors.RED}{'='*50}{Colors.NC}")
            print(f"{Colors.RED}Test Output:{Colors.NC}")
            print(f"{Colors.RED}{'='*50}{Colors.NC}")
            print(output)
            print()
            print(f"{Colors.YELLOW}Summary:{Colors.NC}")
            print(f"{Colors.GREEN}  Passed: {', '.join(passed_tasks) if passed_tasks else 'None'}{Colors.NC}")
            print(f"{Colors.RED}  Failed: {tag}{Colors.NC}")
            print(f"{Colors.YELLOW}  Not tested: {', '.join(tags[i:])}{Colors.NC}" if i < len(tags) else "")
            return False
        
        print()
    
    # All tasks passed, run complete test suite to be sure (unless filtering specific tasks)
    if task_filter:
        # User requested specific tasks only, don't run complete suite
        print()
        print(f"{Colors.GREEN}{'='*50}{Colors.NC}")
        print(f"{Colors.GREEN}✓ Specified tasks passed!{Colors.NC}")
        print(f"{Colors.GREEN}  Completed tasks: {', '.join(passed_tasks)}{Colors.NC}")
        print(f"{Colors.GREEN}{'='*50}{Colors.NC}")
        return True
    
    print(f"{Colors.BLUE}{'='*50}{Colors.NC}")
    print(f"{Colors.BLUE}Running complete test suite...{Colors.NC}")
    print(f"{Colors.BLUE}{'='*50}{Colors.NC}")
    print()
    
    success, output = run_all_tests(executable)
    print(output)
    
    if success:
        print()
        print(f"{Colors.GREEN}{'='*50}{Colors.NC}")
        print(f"{Colors.GREEN}✓ All tests passed!{Colors.NC}")
        print(f"{Colors.GREEN}  Completed tasks: {', '.join(passed_tasks)}{Colors.NC}")
        print(f"{Colors.GREEN}{'='*50}{Colors.NC}")
        return True
    else:
        print()
        print(f"{Colors.RED}{'='*50}{Colors.NC}")
        print(f"{Colors.RED}✗ Complete test suite failed{Colors.NC}")
        print(f"{Colors.RED}{'='*50}{Colors.NC}")
        return False


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Run progressive tests')
    parser.add_argument('project_dir', help='Project directory path')
    parser.add_argument('executable', help='Test executable path')
    parser.add_argument('--task', type=str, help='Run only specific task(s) (comma-separated)')
    
    args = parser.parse_args()
    
    project_dir = Path(args.project_dir).resolve()
    executable = Path(args.executable)
    
    if not executable.is_absolute():
        executable = project_dir / "build" / executable
    
    if not executable.exists():
        print(f"{Colors.RED}Error: Executable not found: {executable}{Colors.NC}")
        sys.exit(1)
    
    # Parse task filter if provided
    task_filter = None
    if args.task:
        task_filter = [t.strip() for t in args.task.split(',')]
    
    success = progressive_test(project_dir, executable, task_filter)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
