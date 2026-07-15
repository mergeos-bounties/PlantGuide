import { describe, it, expect } from 'vitest';
import { plants } from './plants';

describe('PlantGuide - Arid Climate Species', () => {
  it('should have at least 3 arid climate species', () => {
    const aridPlants = plants.filter(plant => 
      plant.climate === 'arid' || plant.climate === 'desert'
    );
    expect(aridPlants.length).toBeGreaterThanOrEqual(3);
  });

  it('should have complete care cards for arid species', () => {
    const aridPlants = plants.filter(plant => 
      plant.climate === 'arid' || plant.climate === 'desert'
    );
    
    aridPlants.forEach(plant => {
      expect(plant.name).toBeDefined();
      expect(plant.scientificName).toBeDefined();
      expect(plant.careCard).toBeDefined();
      expect(plant.careCard.water).toBeDefined();
      expect(plant.careCard.sunlight).toBeDefined();
      expect(plant.careCard.soil).toBeDefined();
      expect(plant.careCard.temperature).toBeDefined();
    });
  });

  it('should have sample images for arid species', () => {
    const aridPlants = plants.filter(plant => 
      plant.climate === 'arid' || plant.climate === 'desert'
    );
    
    aridPlants.forEach(plant => {
      expect(plant.sampleImage).toBeDefined();
      expect(plant.sampleImage).toMatch(/\.(jpg|png|webp)$/);
    });
  });

  it('should include Barrel Cactus species', () => {
    const barrelCactus = plants.find(plant => 
      plant.name.toLowerCase().includes('barrel cactus')
    );
    expect(barrelCactus).toBeDefined();
    expect(barrelCactus?.climate).toMatch(/arid|desert/);
  });

  it('should include Aloe Vera species', () => {
    const aloeVera = plants.find(plant => 
      plant.name.toLowerCase().includes('aloe')
    );
    expect(aloeVera).toBeDefined();
    expect(aloeVera?.climate).toMatch(/arid|desert/);
  });

  it('should include Agave species', () => {
    const agave = plants.find(plant => 
      plant.name.toLowerCase().includes('agave')
    );
    expect(agave).toBeDefined();
    expect(agave?.climate).toMatch(/arid|desert/);
  });

  it('should have appropriate water requirements for arid plants', () => {
    const aridPlants = plants.filter(plant => 
      plant.climate === 'arid' || plant.climate === 'desert'
    );
    
    aridPlants.forEach(plant => {
      expect(plant.careCard.water).toMatch(/low|minimal|sparse|infrequent/i);
    });
  });

  it('should have appropriate sunlight requirements for arid plants', () => {
    const aridPlants = plants.filter(plant => 
      plant.climate === 'arid' || plant.climate === 'desert'
    );
    
    aridPlants.forEach(plant => {
      expect(plant.careCard.sunlight).toMatch(/full sun|direct|bright/i);
    });
  });
});

export const plants = [
  {
    id: 'barrel-cactus-001',
    name: 'Golden Barrel Cactus',
    scientificName: 'Echinocactus grusonii',
    climate: 'arid',
    careCard: {
      water: 'Low - water sparingly every 2-3 weeks in growing season, monthly in winter',
      sunlight: 'Full sun to partial shade, 6+ hours direct sunlight',
      soil: 'Well-draining cactus mix with sand and perlite',
      temperature: '50-85°F (10-29°C), protect from frost',
      humidity: 'Low, 10-30%',
      fertilizer: 'Diluted cactus fertilizer once in spring',
      notes: 'Drought-tolerant, slow-growing, can reach 3 feet diameter'
    },
    sampleImage: 'samples/golden-barrel-cactus.jpg',
    native: 'Central Mexico',
    wateringFrequency: 'bi-weekly'
  },
  {
    id: 'aloe-vera-001',
    name: 'Aloe Vera',
    scientificName: 'Aloe barbadensis miller',
    climate: 'arid',
    careCard: {
      water: 'Low to moderate - water deeply when soil is completely dry, every 2-3 weeks',
      sunlight: 'Bright indirect to full sun, 6-8 hours light',
      soil: 'Sandy, well-draining succulent soil with pH 7.0-8.5',
      temperature: '55-80°F (13-27°C), avoid frost',
      humidity: 'Low to moderate, 20-40%',
      fertilizer: 'Balanced liquid fertilizer diluted to half strength, once in spring',
      notes: 'Medicinal properties, gel used for burns and skin care'
    },
    sampleImage: 'samples/aloe-vera.jpg',
    native: 'Arabian Peninsula',
    wateringFrequency: 'bi-weekly'
  },
  {
    id: 'agave-americana-001',
    name: 'Century Plant',
    scientificName: 'Agave americana',
    climate: 'desert',
    careCard: {
      water: 'Minimal - water infrequently, every 3-4 weeks during growing season',
      sunlight: 'Full sun, thrives in intense direct sunlight',
      soil: 'Extremely well-draining, sandy or gravelly soil',
      temperature: '50-90°F (10-32°C), cold hardy to 20°F (-6°C)',
      humidity: 'Very low, 10-20%',
      fertilizer: 'Minimal feeding, once per year in spring if needed',
      notes: 'Large rosette formation, sharp spines on leaf tips, blooms once after 10-30 years'
    },
    sampleImage: 'samples/century-plant-agave.jpg',
    native: 'Mexico and southwestern United States',
    wateringFrequency: 'monthly'
  }
];