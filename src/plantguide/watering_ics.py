"""Watering calendar ICS export."""

from datetime import datetime, timedelta
from pathlib import Path

def generate_watering_ics(collection, output_path):
    """Generate ICS file for watering schedule."""
    ics_content = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//PlantGuide//Watering Calendar//EN
BEGIN:VEVENT"""
    
    for plant in collection:
        name = plant.get('name', 'Plant')
        water_days = plant.get('water_days', 7)
        
        next_water = datetime.now() + timedelta(days=water_days)
        
        ics_content += f"""
DTSTART:{next_water.strftime('%Y%m%d')}
SUMMARY:Water {name}
DESCRIPTION:Water your {name}
RRULE:FREQ=DAILY;INTERVAL={water_days}
END:VEVENT"""
    
    ics_content += "
END:VCALENDAR"
    
    Path(output_path).write_text(ics_content)
    return output_path
