"""CLI helper functions for user interaction."""

from typing import List, Optional


def prompt_user(message: str, default: Optional[str] = None) -> str:
    """
    Prompt user for input with optional default
    
    Args:
        message: Prompt message
        default: Default value if user presses Enter
        
    Returns:
        User input or default
    """
    if default:
        prompt = f"{message} [{default}]: "
    else:
        prompt = f"{message}: "
    
    response = input(prompt).strip()
    
    if not response and default:
        return default
    
    return response


def select_from_menu(options: List[str], title: str = "Select an option") -> str:
    """
    Display menu and get user selection
    
    Args:
        options: List of options to display
        title: Menu title
        
    Returns:
        Selected option
    """
    print(f"\n{title}:")
    for i, option in enumerate(options, 1):
        print(f"  {i}. {option}")
    
    while True:
        try:
            choice = input("\nEnter number: ").strip()
            idx = int(choice) - 1
            
            if 0 <= idx < len(options):
                return options[idx]
            else:
                print(f"Please enter a number between 1 and {len(options)}")
        except ValueError:
            print("Please enter a valid number")


def confirm_action(message: str, default: bool = False) -> bool:
    """
    Ask user to confirm action
    
    Args:
        message: Confirmation message
        default: Default response if user presses Enter
        
    Returns:
        True if confirmed, False otherwise
    """
    if default:
        prompt = f"{message} [Y/n]: "
    else:
        prompt = f"{message} [y/N]: "
    
    response = input(prompt).strip().lower()
    
    if not response:
        return default
    
    return response in ['y', 'yes']


def print_header(text: str):
    """
    Print formatted header
    
    Args:
        text: Header text
    """
    print(f"\n{'=' * 60}")
    print(f"  {text}")
    print('=' * 60)


def print_success(message: str):
    """Print success message"""
    print(f"✓ {message}")


def print_error(message: str):
    """Print error message"""
    print(f"✗ {message}")


def print_warning(message: str):
    """Print warning message"""
    print(f"⚠ {message}")


def print_info(message: str):
    """Print info message"""
    print(f"ℹ {message}")
