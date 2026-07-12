# PlantGuide — How to contribute a species (photo pack)

Earn **MRG** by adding one plant species with original photos and a care card.

**Repository:** https://github.com/mergeos-bounties/PlantGuide  
**All languages:** [README.md](README.md)  
**Species issues:** https://github.com/mergeos-bounties/PlantGuide/issues?q=is%3Aissue+is%3Aopen+label%3Aspecies-pack

## Steps

1. **Star** [PlantGuide](https://github.com/mergeos-bounties/PlantGuide) and [mergeos](https://github.com/mergeos-bounties/mergeos).
2. Open a **species-pack** issue: https://github.com/mergeos-bounties/PlantGuide/issues?q=is%3Aissue+is%3Aopen+label%3Aspecies-pack
3. Comment on that issue: `I claim this bounty`
4. Also comment on MergeOS [Claim Token #1](https://github.com/mergeos-bounties/mergeos/issues/1) with the issue link.
5. Take **≥2 original photos** (whole plant + leaf/flower close-up). No stolen web images.
6. Add files in a PR to **PlantGuide** `master`:
   - `data/species/<id>.json` (tags + full care object)
   - `data/samples/obs_<id>.json` (`expected_species`, tags)
7. PR body: `Fixes #<issue>` + link photos + consent note.
8. Locally: `pip install -e ".[dev]"` then `plantguide care show -s <id>` and `pytest -q` and `ruff check src tests`

## Acceptance

- Species + sample JSON merged
- `plantguide care show` works
- Photo evidence in PR
- Tests and ruff pass
- Toxicity disclaimer when relevant

## Payout

Maintainer merges → ledger credit **25 MRG** typical for one species (scale 25/50/100/200).

## Ethics

Educational care only. Not medical advice for poisoning. Prefer photos of plants you own or gardens that allow photography.

---
Policy: [BOUNTY.md](../BOUNTY.md) · MergeOS: https://mergeos.shop · Lang: `en`
