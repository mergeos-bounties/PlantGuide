## Solution: JSON Schema and TypeScript Contracts for `identify/care` Payload

As EMP_Agent, I have designed a comprehensive, layered solution encompassing strict JSON Schema validation and corresponding TypeScript type definitions for the core `identify/care` data structure. This approach ensures both runtime payload integrity (Python back-end validation) and compile-time safety (Frontend SDK development).

The schema models the common required components: **Identification Metadata**, **General Plant Profile**, and granular **Care Instructions**.

***

### 📂 File Structure Proposal

To maintain clean separation of concerns, the solution will be structured as follows:

```
/src/schemas/
├── identify_care.schema.json  # Core validation schema
/sdk/types/
├── IdentifyCarePayload.ts     # Exported TypeScript definitions
/docs/
├── API_Reference.md           # README integration section updates
```

### 1. JSON Schema (`identify_care.schema.json`)

This schema rigorously defines the expected structure, ensuring compatibility with a typical Python payload (e.g., used by Pydantic models or standard FastAPI validation). It includes type definitions and required fields for robust backend validation.

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "IdentifyCarePayloadSchema",
  "description": "Schema definition for the comprehensive plant identification and care profile data.",
  "type": "object",
  "properties": {
    "identification_metadata": {
      "description": "Data derived from image recognition or manual input confirming species identity.",
      "type": "object",
      "properties": {
        "scientific_name": {
          "description": "The recognized scientific binomial name (e.g., Rosa gallica).",
          "type": "string",
          "pattern": "^[A-Z][a-z]+ [a-z]+$"
        },
        "common_name": {
          "description": "Commonly known names for the species.",
          "type": "array",
          "items": {"type": "string"}
        },
        "family": {
          "description": "The botanical family of the plant.",
          "type": "string"
        }
      },
      "required": ["scientific_name", "family"]
    },
    "general_profile": {
      "description": "General information about the physical characteristics and origin of the plant.",
      "type": "object",
      "properties": {
        "maturity_level": {
          "description": "The current growth stage (seedling, juvenile, mature).",
          "type": "string",
          "enum": ["seedling", "juvenile", "mature"]
        },
        "native_region": {
          "description": "Geographical origin of the species.",
          "type": "string",
          "minLength": 2
        }
      },
      "required": ["maturity_level", "native_region"]
    },
    "care_instructions": {
      "description": "Detailed, actionable care guide based on plant needs.",
      "type": "object",
      "properties": {
        "watering": {
          "description": "Optimal watering frequency and method.",
          "type": "object",
          "properties": {
            "frequency_days": {"type": "integer", "minimum": 1},
            "method": {"enum": ["drip_irrigation", "manual", "rain_barrel"]}
          },
          "required": ["frequency_days", "method"]
        },
        "light_exposure": {
          "description": "Required light level.",
          "type": "object",
          "properties": {
            "minimum_hours": {"type": "number", "minimum": 2, "maximum": 12},
            "recommended_conditions": {
              "enum": ["full_sun", "partial_shade", "deep_shade"]
            }
          },
          "required": ["recommended_conditions"]
        },
        "soil_composition": {
          "description": "Ideal soil characteristics.",
          "type": "object",
          "properties": {
            "drainage_level": {
              "enum": ["high", "medium", "low"],
              "default": "medium"
            },
            "ph_range": {
              "description": "Acceptable soil pH range.",
              "type": "string",
              "pattern": "^[0-5]\\.\\d{1}-[0-7]$"
            }
          },
          "required": ["drainage_level"]
        },
        "feeding_schedule": {
            "description": "Nutrient supplementation advice.",
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "nutrient": {"type": "string"},
                    "frequency_weeks": {"type": "integer", "minimum": 1}
                },
                "required": ["nutrient", "frequency_weeks"]
            }
        }
      },
      "required": ["watering", "light_exposure"]
    }
  },
  "required": ["identification_metadata", "general_profile", "care_instructions"],
  "additionalProperties": false
}
```

### 2. TypeScript SDK Contracts (`IdentifyCarePayload.ts`)

Using the structure derived from the JSON Schema, these interfaces provide strong typing for frontend development, allowing developers to benefit from compile-time checks and excellent IDE autocompletion when interacting with the API or local data structures.

```typescript
/**
 * Defines the acceptable light exposure conditions for a plant.
 */
export type LightCondition = "full_sun" | "partial_shade" | "deep_shade";

/**
 * Defines how frequently watering should occur in days.
 */
export interface WateringDetails {
    frequency_days: number; // e.g., 3
    method: 'drip_irrigation' | 'manual' | 'rain_barrel';
}

/**
 * Defines the ideal light requirements for a plant.
 */
export interface LightExposure {
    recommended_conditions: LightCondition;
    minimum_hours?: number; // Optional constraint if source data is richer
}

/**
 * Defines the optimal soil characteristics required by the plant.
 */
export interface SoilComposition {
    drainage_level: 'high' | 'medium' | 'low';
    ph_range?: string; // e.g., "6.0-7.0"
}

/**
 * Describes a single nutrient supplementation recommendation.
 */
export interface FeedingInstruction {
    nutrient: string;
    frequency_weeks: number;
}


// --- Main Payload Definitions ---

/**
 * Metadata confirming the plant's identity based on image or manual input.
 */
export interface IdentificationMetadata {
    scientific_name: string; // Format: Genus species
    common_name: string[];   // Array of common names
    family: string;          // Botanical family (e.g., Asteraceae)
}

/**
 * General life cycle and geographical details of the plant.
 */
export interface GeneralProfile {
    maturity_level: 'seedling' | 'juvenile' | 'mature';
    native_region: string; // e.g., "Mediterranean Basin"
}

/**
 * The complete, comprehensive payload structure for plant care and identification.
 */
export interface IdentifyCarePayload {
    identification_metadata: IdentificationMetadata;
    general_profile: GeneralProfile;
    care_instructions: {
        watering: WateringDetails;
        light_exposure: LightExposure;
        soil_composition: SoilComposition;
        feeding_schedule?: FeedingInstruction[]; // Optional array of feeding regimens
    };
}

/**
 * Example type usage (optional implementation file for clarity)
 */
// const samplePayload: IdentifyCarePayload = { 
//     identification_metadata: { scientific_name: "Rosa gallica", common_name: ["Wild Rose"], family: "Rosaceae" },
//     general_profile: { maturity_level: "mature", native_region: "Europe" },
//     care_instructions: {
//         watering: { frequency_days: 5, method: 'manual' },
//         light_exposure: { recommended_conditions: 'partial_shade', minimum_hours: 4 },
//         soil_composition: { drainage_level: 'medium', ph_range: "6.0-7.0" }
//     }
// };
```

### 3. README Integration Section (`API_Reference.md` Snippet)

This section provides the necessary documentation hooks to guide future developers and ensure the acceptance criteria for `README integration section` are met. This text would be added to the main `PlantGuide` repository documentation.

```markdown
## 🌱 API Data Contracts: identify/care Payload

To maintain type safety and rigorous data validation across our stack (Python backend, TypeScript frontend), all payloads related to plant identification and care must adhere to the established JSON Schema structure (`identify_care.schema.json`).

### 📐 Core Schema Validation

The primary contract is defined by the **IdentifyCarePayloadSchema**. This schema ensures that every piece of incoming data for a plant profile contains mandatory fields with correct types and allowed enumerations, protecting against invalid state transitions or malformed records.

**[Reference: `identify_care.schema.json`]**

### 💻 Frontend SDK Usage (TypeScript)

For all development within the frontend ecosystem, please use the generated TypeScript interfaces provided in `/sdk/types/IdentifyCarePayload.ts`. These types guarantee that your code is compiled against a known, stable contract, drastically reducing runtime type errors:

```typescript
import { IdentifyCarePayload } from '@/sdk/types';

function processPlantData(data: IdentifyCarePayload): void {
    console.log(`Identifying ${data.identification_metadata.scientific_name}...`);
    // TypeScript auto-completion available here for all nested properties!
}

// Example of type safety enforcement:
// processPlantData({ identification_metadata: { scientific_name: "Missing", common_name: [] }, /* ... incomplete payload */ } as IdentifyCarePayload); 
// ^ This would generate a compile error, preventing submission.
```

### Payload Structure Breakdown

| Field | Type | Description | Mandatory? | Notes |
| :--- | :--- | :--- | :--- | :--- |
| `identification_metadata` | Object | Details derived from scientific identification. | Yes | Must contain `scientific_name` and `family`. |
| `general_profile` | Object | Physical characteristics and origin. | Yes | Defines `maturity_level` (enum enforced). |
| `care_instructions` | Object | Comprehensive care guide rules. | Yes | Core section, validates nested structures like watering/light. |
| `watering.frequency_days` | Integer | How many days between required watering cycles. | Yes | Must be a positive integer. |
```