"""Species toxicity filter CLI."""

import json
from pathlib import Path
from rich.console import Console
from rich.table import Table

console = Console()

def filter_by_toxicity(species_dir, pet_safe=False, toxic_only=False):
    """Filter species by toxicity."""
    species_files = Path(species_dir).glob('*.json')
    
    results = []
    for f in species_files:
        data = json.loads(f.read_text())
        toxicity = data.get('care', {}).get('toxicity', '').lower()
        
        is_toxic = 'toxic' in toxicity
        is_safe = not is_toxic
        
        if pet_safe and is_safe:
            results.append(data)
        elif toxic_only and is_toxic:
            results.append(data)
        elif not pet_safe and not toxic_only:
            results.append(data)
    
    return results

def print_toxicity_table(species_list):
    """Print species with toxicity info."""
    table = Table(title="Species Toxicity")
    table.add_column("Name", style="cyan")
    table.add_column("Toxicity", style="yellow")
    
    for s in species_list:
        name = s.get('common_name', '?')
        toxicity = s.get('care', {}).get('toxicity', 'Unknown')
        style = "red" if "toxic" in toxicity.lower() else "green"
        table.add_row(name, f"[{style}]{toxicity}[/{style}]")
    
    console.print(table)
