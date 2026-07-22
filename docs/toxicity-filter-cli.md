# Toxicity and pet-safety flags

PlantGuide exposes a normalized `toxicity` list on every species returned by the data
loader. The supported tags are:

- `pet_safe`: the catalog explicitly describes the plant as safe or non-toxic to pets,
  cats, or dogs.
- `toxic_to_pets`: the catalog contains a toxicity warning. Toxic warnings take
  precedence over safe language when both appear.
- `unknown`: the catalog does not contain a clear pet-safety statement.
- `toxic_to_horses`: an additional horse-specific warning.
- `edible`: an additional human-edibility tag; it does not imply pet safety.

Exactly one of `pet_safe`, `toxic_to_pets`, or `unknown` is present after loading. Legacy
string fields and care-card notes are normalized at load time, so callers do not need to
handle multiple toxicity shapes.

## CLI filter

```console
plantguide species list --pet-safe
```

The filter includes only records normalized to `pet_safe`. Records marked `unknown` are
excluded rather than assumed safe.

Pet-safety flags are informational only, not veterinary advice. Confirm a plant's
identity and safety with a veterinarian or trusted toxicology source before allowing a
pet access to it. Toxicity can vary by animal, plant part, dose, and exposure route.
