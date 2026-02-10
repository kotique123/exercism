#!/usr/bin/env python3
"""
Main Orchestrator - Coordinates build, test, and submission modules
Usage: ./run.py <project_directory> [--submit|-s]
"""

import subprocess
import sys
import argparse
from pathlib import Path


class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'


def print_header(text: str):
    """Print formatted header"""
    print(f"\n{Colors.BLUE}{'='*50}{Colors.NC}")
    print(f"{Colors.BLUE}{text}{Colors.NC}")
    print(f"{Colors.BLUE}{'='*50}{Colors.NC}\n")


def resolve_project_path(project_input: str, script_dir: Path) -> Path:
    """Resolve project directory from various input formats"""
    project_path = Path(project_input)
    
    # If absolute path, use directly
    if project_path.is_absolute():
        return project_path
    
    # Try relative to current working directory
    cwd_path = Path.cwd() / project_input
    if cwd_path.exists():
        return cwd_path.resolve()
    
    # Try relative to cpp directory (script_dir parent)
    cpp_dir = script_dir.parent
    cpp_path = cpp_dir / project_input
    if cpp_path.exists():
        return cpp_path.resolve()
    
    # Try with cpp/ prefix
    workspace_root = cpp_dir.parent
    workspace_path = workspace_root / project_input
    if workspace_path.exists():
        return workspace_path.resolve()
    
    # Try cpp/<project_input>
    cpp_prefixed = workspace_root / "cpp" / project_input
    if cpp_prefixed.exists():
        return cpp_prefixed.resolve()
    
    # Return as-is and let validation fail with clear error
    return project_path.resolve()


def run_module(module_script: Path, args: list, step_name: str, interactive: bool = False) -> tuple[bool, str]:
    """Run a module script and return success status and output
    
    Args:
        module_script: Path to the module script
        args: Arguments to pass to the script
        step_name: Name for error messages
        interactive: If True, don't capture output (for user interaction)
    """
    try:
        if interactive:
            # Don't capture output - let module interact with terminal
            result = subprocess.run(
                [str(module_script)] + args,
                timeout=120
            )
            return result.returncode == 0, ""
        else:
            # Capture output for display
            result = subprocess.run(
                [str(module_script)] + args,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            output = result.stdout.strip()
            errors = result.stderr.strip()
            
            full_output = output
            if errors:
                full_output = f"{output}\n{errors}" if output else errors
            
            return result.returncode == 0, full_output
    
    except subprocess.TimeoutExpired:
        return False, f"{step_name} timed out"
    except Exception as e:
        return False, f"Error running {step_name}: {str(e)}"


def main():
    parser = argparse.ArgumentParser(
        description='Build, test, and submit Exercism C++ projects',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s lasagna              Build and test
  %(prog)s lasagna --submit     Build, test, and auto-submit
  %(prog)s cpp/lasagna -s       Same with full path
        """
    )
    
    parser.add_argument('project', help='Project directory (e.g., "lasagna" or "cpp/lasagna")')
    parser.add_argument('-s', '--submit', action='store_true', 
                       help='Auto-submit to Exercism if tests pass')
    
    args = parser.parse_args()
    
    # Get script directory and resolve paths
    script_dir = Path(__file__).parent.resolve()
    modules_dir = script_dir / "modules"
    
    project_dir = resolve_project_path(args.project, script_dir)
    project_name = project_dir.name
    
    # Validate project directory
    if not project_dir.exists():
        print(f"{Colors.RED}Error: Project directory '{project_dir}' does not exist{Colors.NC}")
        sys.exit(1)
    
    if not (project_dir / "CMakeLists.txt").exists():
        print(f"{Colors.RED}Error: CMakeLists.txt not found in '{project_dir}'{Colors.NC}")
        sys.exit(1)
    
    print_header(f"Building and Testing: {project_name}")
    
    # Step 1: Build
    print(f"{Colors.YELLOW}[1/3] Building project...{Colors.NC}")
    build_script = modules_dir / "build.sh"
    
    success, output = run_module(build_script, [str(project_dir)], "Build")
    
    if not success:
        print(f"{Colors.RED}✗ Build failed{Colors.NC}")
        print(output)
        sys.exit(1)
    
    executable_path = output.strip().split('\n')[-1]  # Last line is the executable path
    print(f"{Colors.GREEN}✓ Build successful{Colors.NC}")
    print(f"{Colors.BLUE}  Executable: {executable_path}{Colors.NC}")
    
    # Step 2: Test (Progressive)
    print(f"\n{Colors.YELLOW}[2/3] Running progressive tests...{Colors.NC}\n")
    test_script = modules_dir / "test.py"
    
    success, output = run_module(test_script, [str(project_dir), executable_path], "Test")
    print(output)
    
    if not success:
        print(f"\n{Colors.RED}✗ Tests failed{Colors.NC}")
        sys.exit(1)
    
    # Step 3: Submit (if requested and tests passed)
    print(f"\n{Colors.YELLOW}[3/3] Submission...{Colors.NC}")
    submit_script = modules_dir / "submit.py"
    
    submit_args = [str(project_dir)]
    if args.submit:
        submit_args.append("--auto")
    
    # Run interactively if not auto-submitting (needs user input)
    is_interactive = not args.submit
    success, output = run_module(submit_script, submit_args, "Submit", interactive=is_interactive)
    
    if output:  # Only print if there's captured output (non-interactive mode)
        print(output)
    
    if not success and args.submit:
        # Don't fail the whole process if submission fails
        print(f"{Colors.YELLOW}Note: Submission step had issues but tests passed{Colors.NC}")
    
    print(f"\n{Colors.GREEN}{'='*50}{Colors.NC}")
    print(f"{Colors.GREEN}✓ Process completed successfully!{Colors.NC}")
    print(f"{Colors.GREEN}{'='*50}{Colors.NC}\n")


if __name__ == "__main__":
    main()
