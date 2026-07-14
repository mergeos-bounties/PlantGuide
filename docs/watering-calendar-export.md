import { Plant } from '../types/Plant';

interface WateringEvent {
  plantName: string;
  dueDate: Date;
  description: string;
}

export function generateWateringCalendarICS(plants: Plant[]): string {
  const events: WateringEvent[] = [];
  const now = new Date();

  // Calculate watering events for the next 90 days
  plants.forEach(plant => {
    if (!plant.wateringFrequencyDays || plant.wateringFrequencyDays <= 0) {
      return;
    }

    const lastWatered = plant.lastWatered ? new Date(plant.lastWatered) : new Date();
    let nextWatering = new Date(lastWatered);
    nextWatering.setDate(nextWatering.getDate() + plant.wateringFrequencyDays);

    // Generate events for next 90 days
    const endDate = new Date(now);
    endDate.setDate(endDate.getDate() + 90);

    while (nextWatering <= endDate) {
      if (nextWatering >= now) {
        events.push({
          plantName: plant.name,
          dueDate: new Date(nextWatering),
          description: plant.notes || `Water ${plant.name}`
        });
      }
      nextWatering = new Date(nextWatering);
      nextWatering.setDate(nextWatering.getDate() + plant.wateringFrequencyDays);
    }
  });

  // Sort events by date
  events.sort((a, b) => a.dueDate.getTime() - b.dueDate.getTime());

  return buildICS(events);
}

function buildICS(events: WateringEvent[]): string {
  const lines: string[] = [
    'BEGIN:VCALENDAR',
    'VERSION:2.0',
    'PRODID:-//PlantGuide//Watering Calendar//EN',
    'CALSCALE:GREGORIAN',
    'METHOD:PUBLISH',
    'X-WR-CALNAME:Plant Watering Schedule',
    'X-WR-TIMEZONE:UTC'
  ];

  events.forEach((event, index) => {
    const uid = `watering-${Date.now()}-${index}@plantguide.local`;
    const dtstamp = formatICSDate(new Date());
    const dtstart = formatICSDate(event.dueDate);
    
    // Create all-day event
    const dtstartDate = formatICSDateOnly(event.dueDate);

    lines.push('BEGIN:VEVENT');
    lines.push(`UID:${uid}`);
    lines.push(`DTSTAMP:${dtstamp}`);
    lines.push(`DTSTART;VALUE=DATE:${dtstartDate}`);
    lines.push(`SUMMARY:Water ${event.plantName}`);
    lines.push(`DESCRIPTION:${escapeICSText(event.description)}`);
    lines.push('STATUS:CONFIRMED');
    lines.push('TRANSP:TRANSPARENT');
    lines.push('BEGIN:VALARM');
    lines.push('TRIGGER:-PT2H');
    lines.push('ACTION:DISPLAY');
    lines.push(`DESCRIPTION:Time to water ${event.plantName}`);
    lines.push('END:VALARM');
    lines.push('END:VEVENT');
  });

  lines.push('END:VCALENDAR');

  return lines.join('\r\n');
}

function formatICSDate(date: Date): string {
  const year = date.getUTCFullYear();
  const month = String(date.getUTCMonth() + 1).padStart(2, '0');
  const day = String(date.getUTCDate()).padStart(2, '0');
  const hours = String(date.getUTCHours()).padStart(2, '0');
  const minutes = String(date.getUTCMinutes()).padStart(2, '0');
  const seconds = String(date.getUTCSeconds()).padStart(2, '0');
  return `${year}${month}${day}T${hours}${minutes}${seconds}Z`;
}

function formatICSDateOnly(date: Date): string {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}${month}${day}`;
}

function escapeICSText(text: string): string {
  return text
    .replace(/\\/g, '\\\\')
    .replace(/;/g, '\\;')
    .replace(/,/g, '\\,')
    .replace(/\n/g, '\\n');
}

export function downloadICS(plants: Plant[], filename: string = 'watering-schedule.ics'): void {
  const icsContent = generateWateringCalendarICS(plants);
  const blob = new Blob([icsContent], { type: 'text/calendar;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}