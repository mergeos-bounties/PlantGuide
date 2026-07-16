# Species Photo Evidence Requirements

> Applies to all species-pack bounties in mergeos-bounties/PlantGuide

## Minimum Requirements

Every species-pack PR **must** include at least **2 original photographs** showing the plant. Screenshots, AI-generated images, or unlicensed web scrapes are not accepted.

## Required Angles

| # | Angle | Purpose | Example Composition |
|---|-------|---------|-------------------|
| 1 | **Full plant / habit** | Shows overall growth form, size, branching pattern, pot/context | Frame the entire plant from base to tip against a plain background |
| 2 | **Leaf close-up (adaxial)** | Shows leaf shape, color, veins, margin, texture | Fill ~70% of the frame with 1–3 leaves, lit from the side |
| 3 | **Leaf close-up (abaxial)** *(strongly recommended)* | Shows underside color, vein prominence, pests | Turn a leaf over under diffuse light |
| 4 | **Flower / fruit / stem detail** *(if applicable)* | Confirms reproductive features for identification | Macro shot of flower, berry, or distinctive bark/stem texture |

> Angle 1 + Angle 2 are **mandatory**. Angles 3–4 add strong evidence but are not required for the 25 MRG tier.

## Technical Specifications

| Parameter | Minimum | Recommended |
|-----------|---------|-------------|
| Resolution | 1920 × 1080 px | 4032 × 3024 px (phone camera native) |
| File size per image | — | ≤ 5 MB (JPEG) |
| Format | JPEG or PNG | JPEG (smaller) |
| Color space | sRGB | sRGB |
| Sharpness | In focus on subject | Manual tap-to-focus on leaf/plant |
| Background | Plain / non-distracting | Solid wall, fabric, or out-of-focus natural background |

## Lighting & Composition

- **Preferred**: Diffuse natural daylight (overcast sky, window light, shade)
- **Avoid**: Direct harsh sunlight (washes out color, creates hard shadows)
- **Avoid**: Flash (flattens texture, creates hotspots on glossy leaves)
- **Keep**: Camera parallel to the leaf surface for close-ups (minimize distortion)
- **Scale reference**: Include a coin, ruler, or hand in at least one shot to show size

## Attribution & Licensing

- All photos must be **original** (taken by you) OR clearly licensed for use
- If not original: include source URL and license type (CC0, CC-BY, public domain)
- **Do not** scrape images from Pinterest, Instagram, or commercial nursery websites
- Preferred: photos from your own plant, a friend's plant, a public botanical garden, or a nursery visit
- Add a note in the PR description: `"Photos taken by me at [location] on [date]"`

## Submission Format

Attach photos directly to the PR description (drag-and-drop onto GitHub's comment box). GitHub hosts the images at `https://user-images.githubusercontent.com/...` and they render inline.

```markdown
## Photo Evidence

**Full plant:** ![full](https://user-images.githubusercontent.com/.../full-plant.jpg)
*Snake Plant in 8" pot, east-facing window*

**Leaf close-up:** ![leaf](https://user-images.githubusercontent.com/.../leaf-closeup.jpg)
*Top of leaf, showing yellow margin variegation*
```

## Photo Naming Convention

```
species-id_angle_number.jpeg

Examples:
snake_plant_full_01.jpeg
snake_plant_leaf_01.jpeg
snake_plant_flower_01.jpeg
```

## Checklist for PR Authors

- [ ] ≥ 2 original photos attached
- [ ] Full plant angle included
- [ ] Leaf close-up included (top surface)
- [ ] Photos are in focus and well-lit
- [ ] Scale reference visible in at least one photo
- [ ] Attribution note added (if not self-taken)
- [ ] Images uploaded to PR (not external links)
- [ ] Toxicity disclaimer present in species JSON if relevant
- [ ] No private PII visible (faces, address numbers, license plates)

## Review Notes for Maintainers

- Verify photos appear original (reverse image search if suspicious)
- Confirm ≥ 2 angles are present and distinguishable
- Check that species JSON traits match visible plant features
- Flag any PII or unlicensed images before merging

