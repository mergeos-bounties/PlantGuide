export interface PlantGuideMatch {
  species_id: string;
  common_name: string;
  scientific_name: string;
  score: number;
  matched_tags: string[];
  [key: string]: unknown;
}

export interface PlantGuideCareCard {
  species_id: string;
  common_name: string;
  scientific_name: string;
  summary: string;
  light: string;
  water: string;
  soil: string;
  humidity: string;
  temperature_c: string;
  fertilizer: string;
  toxicity: string;
  common_issues: string[];
  tips: string[];
  [key: string]: unknown;
}

export interface PlantGuideLicenseSafeEvidence {
  source: string;
  source_type: "sample_fixture" | "inline_tags";
  external_assets: string[];
}

export interface PlantGuideCareReport {
  report_type: "plantguide.app.care_report.v1";
  integration_version: "plantguide.sdk.v1";
  ready_for_ui: boolean;
  sample_id: string | null;
  source: string | null;
  query_tags: string[];
  expected_species: string | null;
  hit_top1: boolean | null;
  top_species_id: string | null;
  top_match: PlantGuideMatch | null;
  matches: PlantGuideMatch[];
  care_card: PlantGuideCareCard | null;
  license_safe_evidence: PlantGuideLicenseSafeEvidence;
}

export declare function assessForApp(tags: string | string[], topK?: number): Promise<unknown>;
export declare function careForApp(speciesId: string): Promise<PlantGuideCareCard>;
export declare function careReportFromSample(
  samplePath: string,
  topK?: number,
): Promise<PlantGuideCareReport>;
export declare function careReportFromTags(
  tags: string | string[],
  topK?: number,
): Promise<PlantGuideCareReport>;
