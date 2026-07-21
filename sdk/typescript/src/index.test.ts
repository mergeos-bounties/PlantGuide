/**
 * Tests for sdk/typescript — validates the type contracts match real
 * Python SDK payloads by re-using bundled sample species/observation JSON.
 *
 * Run with:  npm run build && npm test
 */

import { strict as assert } from "node:assert";
import { test } from "node:test";
import * as fs from "node:fs";
import * as path from "node:path";

import {
  isSpecies,
  isIdentifyResponse,
  topSpeciesId,
  topScore,
  type Species,
  type Observation,
} from "./index";

// Resolve bundled fixtures relative to this test file. After `tsc`,
// `dist/index.test.js` and `dist/index.js` sit side by side; the
// ../../../.. walk goes up to repo root.
const repoRoot = path.resolve(__dirname, "..", "..", "..", "..");

test("calathea_orbifolia.json validates as Species", () => {
  const text = fs.readFileSync(path.join(repoRoot, "data/species/calathea_orbifolia.json"), "utf-8");
  const s = JSON.parse(text) as Species;
  assert.ok(isSpecies(s));
  assert.equal(s.id, "calathea_orbifolia");
  assert.equal(typeof s.care.summary, "string");
  assert.ok(Array.isArray(s.tags));
});

test("monstera_deliciosa.json validates as Species", () => {
  const text = fs.readFileSync(path.join(repoRoot, "data/species/monstera_deliciosa.json"), "utf-8");
  const s = JSON.parse(text) as Species;
  assert.ok(isSpecies(s));
  assert.equal(s.id, "monstera_deliciosa");
});

test("observation sample validates against expected_species convention", () => {
  const text = fs.readFileSync(path.join(repoRoot, "data/samples/obs_calathea.json"), "utf-8");
  const o = JSON.parse(text) as Observation;
  assert.ok(typeof o.id === "string");
  assert.ok(Array.isArray(o.tags));
  assert.ok(o.tags.length > 0);
  if (o.expected_species) {
    assert.equal(typeof o.expected_species, "string");
  }
});

test("isIdentifyResponse accepts a well-formed matches[] array", () => {
  const r = {
    matches: [
      { species_id: "calathea_orbifolia", common_name: "Calathea Orbifolia", score: 0.9 },
      { species_id: "calathea_medallion", common_name: "Calathea Medallion", score: 0.4 },
    ],
  };
  assert.ok(isIdentifyResponse(r));
});

test("isIdentifyResponse rejects payloads without matches", () => {
  assert.equal(isIdentifyResponse(null), false);
  assert.equal(isIdentifyResponse({}), false);
  assert.equal(isIdentifyResponse({ matches: "nope" }), false);
});

test("topSpeciesId / topScore helpers", () => {
  const r = {
    matches: [
      { species_id: "zz_plant", common_name: "ZZ Plant", score: 0.5 },
    ],
  } as const;
  assert.equal(topSpeciesId(r), "zz_plant");
  assert.equal(topScore(r), 0.5);
});

test("top helpers return undefined / 0 for empty matches", () => {
  assert.equal(topSpeciesId({ matches: [] }), undefined);
  assert.equal(topScore({ matches: [] }), 0);
});