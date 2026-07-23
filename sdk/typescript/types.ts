// PlantGuide App SDK TypeScript Types
// Generated from PlantGoose schemas - DO NOT EDIT MANUALLY

export interface AssessForAppResult {
  /** The tags used for plant identification */
  query_tags: string[];
  
  /** Array of matched plant species with scores */
  matches: PlantMatch[];
  
  /** Identifier of the identification model used */
  model: string;
  
  /** Whether the result is ready for UI display */
  ready_for_ui: boolean;
  
  /** Version of the PlantGuide SDK integration contract */
  integration_version: string;
  
  /** Care card for the top-matched species (nullable if no matches or care unavailable) */
  top_care: PlantCareCard | null;
  
  /** Species ID of the top match (nullable if no matches) */
  top_species_id: string | null;
}

export interface PlantMatch {
  /** Unique species identifier */
  species_id: string;
  
  /** Common name of the plant */
  common_name: string;
  
  /** Scientific name of the plant */
  scientific_name: string;
  
  /** Normalized match score (0-1) */
  score: number;
  
  /** Confidence level (0-1) */
  confidence: number;
  
  /** Overlapping tags between query and plant */
  tag_overlap: string[];
}

export interface PlantCareCard {
  /** Unique species identifier */
  species_id: string;
  
  /** Common name of the plant */
  common_name: string;
  
  /** Scientific name of the plant */
  scientific_name: string;
  
  /** Brief summary of the plant */
  summary: string;
  
  /** Light requirements */
  light: string;
  
  /** Watering requirements */
  water: string;
  
  /** Soil preferences */
  soil: string;
  
  /** Humidity requirements */
  humidity: string;
  
  /** Temperature range in Celsius (format: "min-max" or single value) */
  temperature_c: string;
  
  /** Fertilizer recommendations */
  fertilizer: string;
  
  /** Toxicity information */
  toxicity: string;
  
  /** Common issues with this plant */
  common_issues: string[];
  
  /** Care tips for this plant */
  tips: string[];
}

export interface CareForAppResult extends PlantCareCard {
  /** Version of the PlantGuide SDK integration contract */
  integration_version: string;
}