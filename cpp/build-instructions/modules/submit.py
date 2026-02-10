#!/usr/bin/env python3
"""
Submit Module - Handles Exercism submission
Reads config.json and submits solution files
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import List, Optional


class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'


def read_config(project_dir: Path) -> Optional[dict]:
    """Read .exercism/config.json"""
    config_file = project_dir / ".exercism" / "config.json"
    
    if not config_file.exists():
        return None
    
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"{Colors.RED}Error reading config.json: {e}{Colors.NC}")
        return None


def get_solution_files(config: dict) -> List[str]:
    """Extract solution files from config"""
    try:
        solution_files = config.get("files", {}).get("solution", [])
        return [f for f in solution_files if f.endswith('.cpp')]
    except Exception:
        return []


def submit_to_exercism(project_dir: Path, files: List[str], auto_submit: bool = False) -> bool:
    """Submit files to Exercism"""
    if not files:
        print(f"{Colors.YELLOW}No solution files found in config.json{Colors.NC}")
        return False
    
    print()
    print(f"{Colors.BLUE}{'='*50}{Colors.NC}")
    print(f"{Colors.BLUE}Exercism Submission{Colors.NC}")
    print(f"{Colors.BLUE}{'='*50}{Colors.NC}")
    print(f"{Colors.YELLOW}Files: {', '.join(files)}{Colors.NC}")
    print()
    
    if not auto_submit:
        try:
            response = input(f"Submit to Exercism? (y/N): ").strip().lower()
            if response not in ['y', 'yes']:
                print(f"{Colors.YELLOW}Submission skipped{Colors.NC}")
                return False
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}Submission cancelled{Colors.NC}")
            return False
    
    # Submit using exercism CLI
    try:
        result = subprocess.run(
            ["exercism", "submit"] + files,
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        output = result.stdout + result.stderr
        print(output)
        
        if result.returncode == 0:
            print(f"{Colors.GREEN}✓ Successfully submitted to Exercism!{Colors.NC}")
            return True
        else:
            print(f"{Colors.RED}✗ Submission failed{Colors.NC}")
            if "No files you submitted have changed" in output:
                print(f"{Colors.YELLOW}Note: Files unchanged since last submission{Colors.NC}")
            else:
                print(f"{Colors.YELLOW}Tip: Make sure exercism CLI is installed and configured{Colors.NC}")
            return False
    
    except FileNotFoundError:
        print(f"{Colors.RED}Error: exercism CLI not found{Colors.NC}")
        print(f"{Colors.YELLOW}Install: brew install exercism{Colors.NC}")
        return False
    except subprocess.TimeoutExpired:
        print(f"{Colors.RED}Error: Submission timed out{Colors.NC}")
        return False
    except Exception as e:
        print(f"{Colors.RED}Error: {str(e)}{Colors.NC}")
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: submit.py <project_directory> [--auto]")
        sys.exit(1)
    
    project_dir = Path(sys.argv[1]).resolve()
    auto_submit = "--auto" in sys.argv
    
    if not project_dir.exists():
        print(f"{Colors.RED}Error: Project directory not found{Colors.NC}")
        sys.exit(1)
    
    config = read_config(project_dir)
    
    if not config:
        print(f"{Colors.YELLOW}No Exercism config found - skipping submission{Colors.NC}")
        sys.exit(0)
    
    solution_files = get_solution_files(config)
    
    if not solution_files:
        print(f"{Colors.YELLOW}No solution files found - skipping submission{Colors.NC}")
        sys.exit(0)
    
    success = submit_to_exercism(project_dir, solution_files, auto_submit)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
