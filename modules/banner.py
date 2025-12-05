"""
EYE - Banner Module
Displays the application logo and information
"""

from rich.console import Console
from pyfiglet import Figlet

console = Console()


def show_logo():
    """
    Display the EYE logo with ASCII art and project information
    """
    # Create figlet object with slant font
    figlet = Figlet(font='slant')
    eye_text = figlet.renderText('EYE')
    
    # Print the pyfiglet text in bold bright green
    console.print(eye_text, style="bold bright_green")
    
    # Print the ASCII eye art in bold bright green
    eye_art = """       _______
    .-'       '-.
   /   (_>O<_)   \\
  |     \\   /     |
   \\     '-'     /
    '-._______.-'"""
    
    console.print(eye_art, style="bold bright_green")
    
    # Print separator line
    console.print("─" * 50, style="bright_white")
    
    # Print version information in white
    console.print("Automated Attack Surface Manager v1.0", style="white")
    
    # Print creator information in bold red
    console.print("Created by: John Ripper", style="bold red")
    
    # Print another separator
    console.print("─" * 50, style="bright_white")
    console.print()  # Empty line for spacing
