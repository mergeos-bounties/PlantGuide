import { execSync } from 'node:child_process';
import { mkdtempSync, writeFileSync, rmSync } from 'node:fs';
import { join } from 'node:path';
import { tmpdir } from 'node:os';

const REPO = 'mergeos-bounties/PlantGuide';

function sh(cmd) {
  return execSync(cmd, { encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] }).trim();
}

function ensureLabel(name, color, description) {
  try {
    sh(
      `gh label create ${JSON.stringify(name)} --repo ${REPO} --color ${color} --description ${JSON.stringify(description)}`,
    );
  } catch {
    try {
      sh(
        `gh label edit ${JSON.stringify(name)} --repo ${REPO} --color ${color} --description ${JSON.stringify(description)}`,
      );
    } catch {
      // ignore
    }
  }
}

function createIssue(title, body, labels) {
  const dir = mkdtempSync(join(tmpdir(), 'plantguide-species-'));
  const file = join(dir, 'body.md');
  try {
    writeFileSync(file, body, 'utf8');
    const labelFlags = labels.map((l) => `--label ${JSON.stringify(l)}`).join(' ');
    const out = sh(
      `gh issue create --repo ${REPO} --title ${JSON.stringify(title)} --body-file ${JSON.stringify(file)} ${labelFlags}`,
    );
    console.log(out);
    return out;
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
}

for (const [name, color, description] of [
  ['species-pack', 'BFDADC', 'Per-species catalog + photo contribution'],
  ['photo', 'FBCA04', 'Needs contributor photos'],
]) {
  ensureLabel(name, color, description);
}

const footer = `

## Claim (MergeOS MRG)

1. Star https://github.com/mergeos-bounties/PlantGuide and https://github.com/mergeos-bounties/mergeos  
2. Comment on **this issue**: \`I claim this bounty\`  
3. Comment on MergeOS [Claim Token #1](https://github.com/mergeos-bounties/mergeos/issues/1) with this issue link  
4. Open a PR to **PlantGuide** with \`Fixes #<this-issue>\`

Policy: [docs/BOUNTY.md](../blob/master/docs/BOUNTY.md)

## Payout

Maintainer reviews PR → merge → **MRG credit** (25/50/100/200 scale; this pack is typically **25 MRG** / species unless noted).
`;

/**
 * Each entry becomes one bounty issue: contributor photographs the plant
 * and lands species JSON + sample traits + photo evidence in the PR.
 */
const species = [
  // Popular houseplants
  { id: 'calathea_orbifolia', common: 'Calathea Orbifolia', sci: 'Goeppertia orbifolia', tags: 'prayer plant, large round leaves, stripes, humidity loving, indoor', region: 'tropical houseplant' },
  { id: 'calathea_medallion', common: 'Calathea Medallion', sci: 'Goeppertia roseopicta', tags: 'prayer plant, patterned leaves, purple underside, indoor', region: 'tropical houseplant' },
  { id: 'maranta_leuconeura', common: 'Prayer Plant', sci: 'Maranta leuconeura', tags: 'prayer plant, red veins, folds at night, indoor', region: 'tropical houseplant' },
  { id: 'philodendron_birkin', common: 'Philodendron Birkin', sci: 'Philodendron Birkin', tags: 'aroid, white pinstripes, compact, indoor', region: 'houseplant' },
  { id: 'philodendron_brasil', common: 'Philodendron Brasil', sci: 'Philodendron hederaceum Brasil', tags: 'trailing, heart leaves, yellow variegation, easy', region: 'houseplant' },
  { id: 'philodendron_pink_princess', common: 'Pink Princess Philodendron', sci: 'Philodendron erubescens Pink Princess', tags: 'aroid, pink variegation, climbing, indoor', region: 'collector houseplant' },
  { id: 'anthurium_andraeanum', common: 'Anthurium / Flamingo Flower', sci: 'Anthurium andraeanum', tags: 'red spathe, glossy leaves, tropical, indoor', region: 'tropical houseplant' },
  { id: 'dieffenbachia_seguine', common: 'Dieffenbachia / Dumb Cane', sci: 'Dieffenbachia seguine', tags: 'variegated, large leaves, indoor, toxic', region: 'houseplant' },
  { id: 'aglaonema_red', common: 'Red Aglaonema', sci: 'Aglaonema commutatum', tags: 'chinese evergreen, red variegation, low light, indoor', region: 'houseplant' },
  { id: 'dracaena_marginata', common: 'Dragon Tree', sci: 'Dracaena marginata', tags: 'spiky leaves, cane stem, indoor, drought tolerant', region: 'houseplant' },
  { id: 'dracaena_fragrans', common: 'Corn Plant', sci: 'Dracaena fragrans', tags: 'corn plant, yellow stripe, cane, indoor', region: 'houseplant' },
  { id: 'yucca_elephantipes', common: 'Spineless Yucca', sci: 'Yucca elephantipes', tags: 'sword leaves, woody trunk, bright light, indoor outdoor', region: 'houseplant' },
  { id: 'sansevieria_cylindrica', common: 'Cylindrical Snake Plant', sci: 'Dracaena angolensis', tags: 'succulent, round spears, drought, indoor', region: 'succulent' },
  { id: 'haworthia_fasciata', common: 'Zebra Haworthia', sci: 'Haworthiopsis fasciata', tags: 'succulent, white stripes, small, windowsill', region: 'succulent' },
  { id: 'echeveria_elegans', common: 'Mexican Snowball', sci: 'Echeveria elegans', tags: 'succulent, rosette, powdery blue, full sun', region: 'succulent' },
  { id: 'crassula_ovata_gollum', common: 'Gollum Jade', sci: 'Crassula ovata Gollum', tags: 'succulent, tubular leaves, woody, drought', region: 'succulent' },
  { id: 'senecio_rowleyanus', common: 'String of Pearls', sci: 'Curio rowleyanus', tags: 'trailing, bead leaves, succulent, hanging', region: 'succulent' },
  { id: 'sedum_morganianum', common: 'Burro\'s Tail', sci: 'Sedum morganianum', tags: 'trailing succulent, plump leaves, hanging', region: 'succulent' },
  { id: 'opuntia_microdasys', common: 'Bunny Ear Cactus', sci: 'Opuntia microdasys', tags: 'cactus, pads, glochids, full sun', region: 'cactus' },
  { id: 'mammillaria_elongata', common: 'Ladyfinger Cactus', sci: 'Mammillaria elongata', tags: 'cactus, clustered columns, spines, sun', region: 'cactus' },
  { id: 'schlumbergera_truncata', common: 'Christmas Cactus', sci: 'Schlumbergera truncata', tags: 'cactus, segmented stems, hanging, blooms winter', region: 'cactus' },
  { id: 'epiphyllum_oxypetalum', common: 'Queen of the Night', sci: 'Epiphyllum oxypetalum', tags: 'orchid cactus, night bloom, flat stems, tropical', region: 'epiphyte' },
  { id: 'hoya_carnosa', common: 'Wax Plant / Hoya', sci: 'Hoya carnosa', tags: 'trailing, waxy leaves, fragrant flowers, climbing', region: 'houseplant' },
  { id: 'hoya_kerrii', common: 'Sweetheart Hoya', sci: 'Hoya kerrii', tags: 'heart shaped leaf, succulent-like, gift plant', region: 'houseplant' },
  { id: 'peperomia_obtusifolia', common: 'Baby Rubber Plant', sci: 'Peperomia obtusifolia', tags: 'thick leaves, compact, indoor, easy', region: 'houseplant' },
  { id: 'peperomia_watermelon', common: 'Watermelon Peperomia', sci: 'Peperomia argyreia', tags: 'striped leaves, compact, humidity, indoor', region: 'houseplant' },
  { id: 'pilea_peperomioides', common: 'Chinese Money Plant', sci: 'Pilea peperomioides', tags: 'round leaves, coin shaped, upright, indoor', region: 'houseplant' },
  { id: 'tradescantia_zebrina', common: 'Wandering Jew / Inch Plant', sci: 'Tradescantia zebrina', tags: 'trailing, purple stripes, fast grower, hanging', region: 'houseplant' },
  { id: 'chlorophytum_comosum_vittatum', common: 'Spider Plant Vittatum', sci: 'Chlorophytum comosum Vittatum', tags: 'arching, white center stripe, plantlets, hanging', region: 'houseplant' },
  { id: 'aspidistra_elatior', common: 'Cast Iron Plant', sci: 'Aspidistra elatior', tags: 'dark green, low light, tough, indoor', region: 'houseplant' },
  { id: 'asparagus_setaceus', common: 'Asparagus Fern', sci: 'Asparagus setaceus', tags: 'feathery foliage, airy, indoor, humidity', region: 'houseplant' },
  { id: 'nephrolepis_exaltata', common: 'Boston Fern', sci: 'Nephrolepis exaltata', tags: 'fern, fronds, humidity, hanging, bathroom', region: 'fern' },
  { id: 'platycerium_bifurcatum', common: 'Staghorn Fern', sci: 'Platycerium bifurcatum', tags: 'epiphyte fern, antler fronds, mount, humidity', region: 'fern' },
  { id: 'adiantum_raddianum', common: 'Maidenhair Fern', sci: 'Adiantum raddianum', tags: 'delicate fronds, black stems, humidity, shade', region: 'fern' },
  { id: 'ficus_elastica', common: 'Rubber Plant', sci: 'Ficus elastica', tags: 'large glossy leaves, tree form, indoor, bright light', region: 'houseplant' },
  { id: 'ficus_benjamina', common: 'Weeping Fig', sci: 'Ficus benjamina', tags: 'tree, small leaves, drooping branches, indoor', region: 'houseplant' },
  { id: 'ficus_microcarpa_ginseng', common: 'Ginseng Ficus Bonsai', sci: 'Ficus microcarpa', tags: 'bonsai, thick roots, indoor tree, bright light', region: 'bonsai' },
  { id: 'schefflera_arboricola', common: 'Dwarf Umbrella Tree', sci: 'Schefflera arboricola', tags: 'umbrella leaves, indoor, easy, bright indirect', region: 'houseplant' },
  { id: 'codiaeum_variegatum', common: 'Croton', sci: 'Codiaeum variegatum', tags: 'colorful leaves, tropical, bright light, indoor outdoor', region: 'tropical' },
  { id: 'cordyline_fruticosa', common: 'Ti Plant / Cordyline', sci: 'Cordyline fruticosa', tags: 'pink red leaves, tropical, outdoor patio, humidity', region: 'tropical' },
  { id: 'alocasia_polly', common: 'Alocasia Polly', sci: 'Alocasia × amazonica Polly', tags: 'elephant ear, dark veins, aroid, humidity', region: 'aroid' },
  { id: 'alocasia_zebrina', common: 'Alocasia Zebrina', sci: 'Alocasia zebrina', tags: 'zebra stems, large leaves, aroid, bright indirect', region: 'aroid' },
  { id: 'colocasia_esculenta', common: 'Taro / Elephant Ear', sci: 'Colocasia esculenta', tags: 'large leaves, wetland, edible corm, outdoor tropical', region: 'tropical edible' },
  { id: 'caladium_bicolor', common: 'Caladium / Heart of Jesus', sci: 'Caladium bicolor', tags: 'colorful heart leaves, shade, seasonal bulb', region: 'tropical' },
  { id: 'syngonium_podophyllum', common: 'Arrowhead Plant', sci: 'Syngonium podophyllum', tags: 'arrow leaves, trailing, variegated, easy indoor', region: 'houseplant' },
  { id: 'scindapsus_pictus', common: 'Satin Pothos', sci: 'Scindapsus pictus', tags: 'silver spots, trailing, aroid, low medium light', region: 'houseplant' },
  { id: 'monstera_adansonii', common: 'Swiss Cheese Vine', sci: 'Monstera adansonii', tags: 'holes in leaves, trailing climbing, tropical', region: 'aroid' },
  { id: 'rhaphidophora_tetrasperma', common: 'Mini Monstera', sci: 'Rhaphidophora tetrasperma', tags: 'split leaves, climbing, fast, indoor', region: 'aroid' },
  { id: 'begonia_maculata', common: 'Polka Dot Begonia', sci: 'Begonia maculata', tags: 'angel wing, white spots, red underside, indoor', region: 'houseplant' },
  { id: 'saintpaulia_ionantha', common: 'African Violet', sci: 'Saintpaulia ionantha', tags: 'fuzzy leaves, purple flowers, windowsill, compact', region: 'flowering houseplant' },
  { id: 'spathiphyllum_sensation', common: 'Peace Lily Sensation', sci: 'Spathiphyllum Sensation', tags: 'large peace lily, white spathe, shade, indoor', region: 'houseplant' },
  { id: 'zamioculcas_raven', common: 'Raven ZZ', sci: 'Zamioculcas zamiifolia Raven', tags: 'black leaves, drought, low light, glossy', region: 'houseplant' },
  { id: 'cactus_gymnocalycium', common: 'Chin Cactus', sci: 'Gymnocalycium mihanovichii', tags: 'colorful grafted cactus, small, sun, windowsill', region: 'cactus' },
  { id: 'cactus_echinopsis', common: 'Sea Urchin Cactus', sci: 'Echinopsis oxygona', tags: 'round cactus, night blooms, spines, full sun', region: 'cactus' },
  // Herbs & edibles
  { id: 'mint_spearmint', common: 'Spearmint', sci: 'Mentha spicata', tags: 'herb, aromatic, invasive runners, moist soil, kitchen', region: 'herb' },
  { id: 'rosemary', common: 'Rosemary', sci: 'Salvia rosmarinus', tags: 'herb, needle leaves, woody, full sun, drought tolerant', region: 'herb' },
  { id: 'thyme_common', common: 'Common Thyme', sci: 'Thymus vulgaris', tags: 'herb, tiny leaves, full sun, dry soil, kitchen', region: 'herb' },
  { id: 'oregano', common: 'Oregano', sci: 'Origanum vulgare', tags: 'herb, aromatic, spreading, full sun, kitchen', region: 'herb' },
  { id: 'lemongrass', common: 'Lemongrass', sci: 'Cymbopogon citratus', tags: 'herb, tall grass, citrus scent, tropical outdoor, kitchen', region: 'tropical herb' },
  { id: 'pandan', common: 'Pandan / Lá Dứa', sci: 'Pandanus amaryllifolius', tags: 'long leaves, fragrant, tropical, vietnamese kitchen', region: 'vietnam tropical' },
  { id: 'vietnamese_coriander', common: 'Rau Răm / Vietnamese Coriander', sci: 'Persicaria odorata', tags: 'herb, pointed leaves, spicy aroma, moist, vietnamese', region: 'vietnam herb' },
  { id: 'holy_basil', common: 'Holy Basil / Tulsi', sci: 'Ocimum tenuiflorum', tags: 'herb, aromatic, purple stems, full sun, medicinal culinary', region: 'herb' },
  { id: 'chili_bird_eye', common: 'Bird\'s Eye Chili / Ớt Hiểm', sci: 'Capsicum annuum', tags: 'chili, small peppers, full sun, edible, balcony', region: 'vegetable' },
  { id: 'tomato_cherry', common: 'Cherry Tomato', sci: 'Solanum lycopersicum', tags: 'vegetable, fruiting, full sun, stake, balcony', region: 'vegetable' },
  { id: 'cucumber_vine', common: 'Cucumber', sci: 'Cucumis sativus', tags: 'vegetable, vine, trellis, full sun, moist', region: 'vegetable' },
  { id: 'eggplant_purple', common: 'Eggplant / Cà Tím', sci: 'Solanum melongena', tags: 'vegetable, purple fruit, full sun, tropical', region: 'vegetable' },
  { id: 'kangkong', common: 'Water Spinach / Rau Muống', sci: 'Ipomoea aquatica', tags: 'leafy green, aquatic, fast grow, vietnamese kitchen', region: 'vietnam vegetable' },
  { id: 'malabar_spinach', common: 'Malabar Spinach / Mồng Tơi', sci: 'Basella alba', tags: 'leafy vine, tropical, mucilaginous, vietnamese', region: 'vietnam vegetable' },
  { id: 'bitter_melon', common: 'Bitter Melon / Khổ Qua', sci: 'Momordica charantia', tags: 'vine, warty fruit, trellis, tropical vegetable', region: 'vietnam vegetable' },
  // Trees & outdoor common VN / tropical
  { id: 'plumeria_rubra', common: 'Frangipani / Hoa Sứ', sci: 'Plumeria rubra', tags: 'tree, fragrant flowers, deciduous tropical, full sun', region: 'vietnam ornamental' },
  { id: 'bougainvillea', common: 'Bougainvillea / Hoa Giấy', sci: 'Bougainvillea spectabilis', tags: 'thorny vine, colorful bracts, full sun, outdoor', region: 'vietnam ornamental' },
  { id: 'hibiscus_rosa_sinensis', common: 'Chinese Hibiscus / Dâm Bụt', sci: 'Hibiscus rosa-sinensis', tags: 'shrub, large flowers, full sun, outdoor tropical', region: 'vietnam ornamental' },
  { id: 'ixora_coccinea', common: 'Ixora / Trang', sci: 'Ixora coccinea', tags: 'shrub, flower clusters, full sun, outdoor tropical', region: 'vietnam ornamental' },
  { id: 'jasmine_sambac', common: 'Arabian Jasmine / Hoa Lài', sci: 'Jasminum sambac', tags: 'fragrant white flowers, climbing shrub, outdoor', region: 'vietnam ornamental' },
  { id: 'orchid_dendrobium', common: 'Dendrobium Orchid / Lan Dendro', sci: 'Dendrobium spp.', tags: 'orchid, epiphyte, cane stems, bright light, humidity', region: 'orchid' },
  { id: 'orchid_phalaenopsis', common: 'Moth Orchid / Lan Hồ Điệp', sci: 'Phalaenopsis spp.', tags: 'orchid, long lasting blooms, indoor, medium light', region: 'orchid' },
  { id: 'orchid_vanda', common: 'Vanda Orchid', sci: 'Vanda spp.', tags: 'orchid, aerial roots, full bright light, tropical', region: 'orchid' },
  { id: 'banana_musa', common: 'Banana Plant / Chuối', sci: 'Musa spp.', tags: 'large leaves, tropical, outdoor, fruiting', region: 'tropical outdoor' },
  { id: 'papaya', common: 'Papaya / Đu Đủ', sci: 'Carica papaya', tags: 'tree, large leaves, full sun, fruit, tropical', region: 'tropical outdoor' },
  { id: 'mango_tree_young', common: 'Mango (young plant) / Xoài', sci: 'Mangifera indica', tags: 'tree seedling, full sun, tropical fruit', region: 'tropical outdoor' },
  { id: 'coconut_seedling', common: 'Coconut Seedling / Dừa', sci: 'Cocos nucifera', tags: 'palm seedling, coastal, full sun, tropical', region: 'palm' },
  { id: 'areca_palm', common: 'Areca Palm / Cau Vàng', sci: 'Dypsis lutescens', tags: 'palm, clumping, indoor outdoor, bright light', region: 'palm' },
  { id: 'lady_palm', common: 'Lady Palm', sci: 'Rhapis excelsa', tags: 'palm, fan leaves, shade tolerant, indoor', region: 'palm' },
  { id: 'money_tree_pachira', common: 'Money Tree', sci: 'Pachira aquatica', tags: 'braided trunk, palmate leaves, indoor, bright indirect', region: 'houseplant' },
  { id: 'lucky_bamboo', common: 'Lucky Bamboo', sci: 'Dracaena sanderiana', tags: 'water grown, stalks, indoor, low light', region: 'houseplant' },
  { id: 'ponytail_palm', common: 'Ponytail Palm', sci: 'Beaucarnea recurvata', tags: 'swollen base, long leaves, drought, indoor', region: 'succulent-like' },
  { id: 'adenium_obesum', common: 'Desert Rose / Sứ Thái', sci: 'Adenium obesum', tags: 'caudex, pink flowers, full sun, drought, bonsai', region: 'succulent outdoor' },
  { id: 'portulaca_grandiflora', common: 'Moss Rose / Hoa Mười Giờ', sci: 'Portulaca grandiflora', tags: 'succulent groundcover, bright flowers, full sun', region: 'vietnam ornamental' },
  { id: 'periwinkle_catharanthus', common: 'Madagascar Periwinkle / Dừa Cạn', sci: 'Catharanthus roseus', tags: 'flowers, full sun, heat tolerant, outdoor', region: 'vietnam ornamental' },
  { id: 'marigold_tagetes', common: 'Marigold / Cúc Vạn Thọ', sci: 'Tagetes erecta', tags: 'orange flowers, full sun, annual, outdoor', region: 'flower' },
  { id: 'sunflower', common: 'Sunflower / Hướng Dương', sci: 'Helianthus annuus', tags: 'tall, large flower, full sun, edible seeds', region: 'flower' },
  { id: 'lavender_english', common: 'English Lavender', sci: 'Lavandula angustifolia', tags: 'aromatic, purple spikes, full sun, dry soil', region: 'herb ornamental' },
  { id: 'rose_hybrid_tea', common: 'Hybrid Tea Rose', sci: 'Rosa hybrid', tags: 'shrub, large blooms, full sun, outdoor', region: 'flower' },
  { id: 'geranium_zonal', common: 'Zonal Geranium', sci: 'Pelargonium × hortorum', tags: 'rounded leaves, bright flowers, balcony, sun', region: 'flower' },
  { id: 'impatiens_walleriana', common: 'Busy Lizzie / Impatiens', sci: 'Impatiens walleriana', tags: 'shade flowers, soft leaves, moist, outdoor', region: 'flower' },
  { id: 'coleus', common: 'Coleus / Lá Gấm', sci: 'Plectranthus scutellarioides', tags: 'colorful foliage, shade partial sun, outdoor indoor', region: 'foliage' },
  { id: 'bromeliad_guzmania', common: 'Guzmania Bromeliad', sci: 'Guzmania spp.', tags: 'rosette, colorful bract, epiphyte, humidity', region: 'bromeliad' },
  { id: 'tillandsia_air_plant', common: 'Air Plant / Tillandsia', sci: 'Tillandsia spp.', tags: 'epiphyte, no soil, mist, bright light', region: 'epiphyte' },
  { id: 'venus_flytrap', common: 'Venus Flytrap', sci: 'Dionaea muscipula', tags: 'carnivorous, traps, wet soil, bright light', region: 'carnivorous' },
  { id: 'nepenthes_pitcher', common: 'Tropical Pitcher Plant', sci: 'Nepenthes spp.', tags: 'carnivorous, hanging pitchers, humidity, bright', region: 'carnivorous' },
  { id: 'bamboo_lucky_clumping', common: 'Clumping Bamboo (decorative)', sci: 'Bambusa multiplex', tags: 'bamboo, clumping, outdoor screen, full sun', region: 'outdoor' },
  { id: 'bird_of_paradise', common: 'Bird of Paradise', sci: 'Strelitzia reginae', tags: 'large leaves, orange flower, bright light, indoor outdoor', region: 'tropical' },
  { id: 'heliconia_psittacorum', common: 'Heliconia / Mỏ Két', sci: 'Heliconia psittacorum', tags: 'tropical, colorful bracts, outdoor, full sun partial', region: 'vietnam ornamental' },
  { id: 'ginger_torch', common: 'Torch Ginger', sci: 'Etlingera elatior', tags: 'tropical, tall, red flower, outdoor, humidity', region: 'tropical' },
  { id: 'turmeric', common: 'Turmeric / Nghệ', sci: 'Curcuma longa', tags: 'rhizome, leafy, edible spice, partial sun tropical', region: 'vietnam edible' },
  { id: 'ginger_culinary', common: 'Culinary Ginger / Gừng', sci: 'Zingiber officinale', tags: 'rhizome, leafy shoots, kitchen, partial shade', region: 'vietnam edible' },
  { id: 'lemongrass_citronella', common: 'Citronella Grass', sci: 'Cymbopogon nardus', tags: 'tall grass, mosquito repellent scent, full sun', region: 'tropical herb' },
  { id: 'coffee_arabica_house', common: 'Coffee Plant (house)', sci: 'Coffea arabica', tags: 'glossy leaves, indoor tree, bright indirect, humidity', region: 'houseplant' },
  { id: 'avocado_seedling', common: 'Avocado Seedling / Bơ', sci: 'Persea americana', tags: 'seed grown, large leaves, bright light, young tree', region: 'fruit seedling' },
  { id: 'citrus_calamansi', common: 'Calamansi / Tắc', sci: 'Citrus × microcarpa', tags: 'citrus, small fruit, full sun, balcony pot', region: 'vietnam citrus' },
  { id: 'citrus_kumquat', common: 'Kumquat / Tắc Ngọt', sci: 'Citrus japonica', tags: 'citrus, ornamental fruit, full sun, pot culture', region: 'citrus' },
  { id: 'olive_tree_pot', common: 'Potted Olive', sci: 'Olea europaea', tags: 'silvery leaves, woody, full sun, mediterranean', region: 'mediterranean' },
  { id: 'boxwood_buxus', common: 'Boxwood', sci: 'Buxus sempervirens', tags: 'shrub, small leaves, hedge, outdoor, pruning', region: 'landscape' },
  { id: 'english_ivy', common: 'English Ivy', sci: 'Hedera helix', tags: 'climbing, lobed leaves, trailing, outdoor indoor', region: 'vine' },
  { id: 'pothos_neon', common: 'Neon Pothos', sci: 'Epipremnum aureum Neon', tags: 'chartreuse leaves, trailing, easy, indoor', region: 'houseplant' },
  { id: 'pothos_njoy', common: 'N\'Joy Pothos', sci: 'Epipremnum aureum N\'Joy', tags: 'white green variegation, compact trailing, indoor', region: 'houseplant' },
  { id: 'snake_plant_laurentii', common: 'Snake Plant Laurentii', sci: 'Dracaena trifasciata Laurentii', tags: 'yellow margins, upright, drought, indoor', region: 'succulent' },
  { id: 'monstera_albo', common: 'Monstera Albo (variegated)', sci: 'Monstera deliciosa var. albo-variegata', tags: 'white variegation, fenestrated, climbing, collector', region: 'collector aroid' },
];

const labels = ['bounty', 'bounty: feature', 'data', 'care', 'species-pack', 'photo', 'reward:25-mrg', 'good first issue'];

for (const s of species) {
  const title = `[25 MRG] Species pack: ${s.common} (\`${s.id}\`) — photo + care card`;
  const body = `## Bounty: 25 MRG — species photo pack

Add **${s.common}** (\`${s.id}\`) to the PlantGuide catalog so the identifier and care API can recommend it.

| Field | Value |
| --- | --- |
| **Suggested id** | \`${s.id}\` |
| **Common name** | ${s.common} |
| **Scientific name** | *${s.sci}* |
| **Suggested tags** | ${s.tags} |
| **Region / use** | ${s.region} |

## What to deliver (PR)

1. **Species JSON** — \`data/species/${s.id}.json\`
   - \`id\`, \`common_name\`, \`scientific_name\`
   - \`tags\` (≥5 useful traits for identification)
   - \`care\` object: \`summary\`, \`light\`, \`water\`, \`soil\`, \`humidity\`, \`temperature_c\`, \`fertilizer\`, \`toxicity\`, \`common_issues\` (array), \`tips\` (array)

2. **Trait sample** — \`data/samples/obs_${s.id}.json\`
   - \`tags\` matching the plant
   - \`expected_species\`: \`${s.id}\`

3. **Photos (required evidence)** — attach in the **PR description** (or \`docs/species-photos/${s.id}/\` if small enough / compressed):
   - ≥ **2 original photos** you took (or clearly licensed with source)
   - Prefer: (a) whole plant, (b) close-up leaf / flower / fruit
   - **No stolen web images** without license
   - If files are large, upload to the PR as GitHub images and link them

4. **Verify locally**
   \`\`\`bash
   pip install -e ".[dev]"
   plantguide species list
   plantguide care show --species ${s.id}
   plantguide identify tags --tags "${s.tags.split(', ').slice(0, 4).join(',')}"
   pytest -q
   \`\`\`

## Acceptance

- [ ] Species file + sample file merged
- [ ] \`plantguide care show -s ${s.id}\` works
- [ ] Top match is reasonable for the sample tags
- [ ] Photo evidence linked in PR (original / licensed)
- [ ] No private PII; toxicity disclaimer present if relevant
- [ ] Tests still pass; ruff clean

## Notes

- Educational care only — not medical advice for poisoning.
- Prefer real photos from your balcony / garden / nursery visit.
${footer}`;

  createIssue(title, body, labels);
}

console.log(`Created ${species.length} species photo bounty issues on ${REPO}`);
