"""Generate docs/guides/*.md multilingual contributor guides."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "docs" / "guides"
ROOT.mkdir(parents=True, exist_ok=True)

SPECIES_ISSUES = (
    "https://github.com/mergeos-bounties/PlantGuide/issues"
    "?q=is%3Aissue+is%3Aopen+label%3Aspecies-pack"
)

# code -> sections
GUIDES: dict[str, dict[str, str]] = {
    "en": {
        "title": "PlantGuide — How to contribute a species (photo pack)",
        "intro": "Earn **MRG** by adding one plant species with original photos and a care card.",
        "steps_h": "Steps",
        "steps": """1. **Star** [PlantGuide](https://github.com/mergeos-bounties/PlantGuide) and [mergeos](https://github.com/mergeos-bounties/mergeos).
2. Open a **species-pack** issue: {issues}
3. Comment on that issue: `I claim this bounty`
4. Also comment on MergeOS [Claim Token #1](https://github.com/mergeos-bounties/mergeos/issues/1) with the issue link.
5. Take **≥2 original photos** (whole plant + leaf/flower close-up). No stolen web images.
6. Add files in a PR to **PlantGuide** `master`:
   - `data/species/<id>.json` (tags + full care object)
   - `data/samples/obs_<id>.json` (`expected_species`, tags)
7. PR body: `Fixes #<issue>` + link photos + consent note.
8. Locally: `pip install -e ".[dev]"` then `plantguide care show -s <id>` and `pytest -q` and `ruff check src tests`""".format(
            issues=SPECIES_ISSUES
        ),
        "accept_h": "Acceptance",
        "accept": "- Species + sample JSON merged\n- `plantguide care show` works\n- Photo evidence in PR\n- Tests and ruff pass\n- Toxicity disclaimer when relevant",
        "pay_h": "Payout",
        "pay": "Maintainer merges → ledger credit **25 MRG** typical for one species (scale 25/50/100/200).",
        "ethics_h": "Ethics",
        "ethics": "Educational care only. Not medical advice for poisoning. Prefer photos of plants you own or gardens that allow photography.",
    },
    "vi": {
        "title": "PlantGuide — Hướng dẫn đóng góp loài cây (gói ảnh)",
        "intro": "Nhận **MRG** khi thêm **một loài** kèm ảnh gốc và thẻ chăm sóc.",
        "steps_h": "Các bước",
        "steps": f"""1. **Star** [PlantGuide](https://github.com/mergeos-bounties/PlantGuide) và [mergeos](https://github.com/mergeos-bounties/mergeos).
2. Chọn issue **species-pack**: {SPECIES_ISSUES}
3. Comment trên issue: `I claim this bounty`
4. Comment thêm trên MergeOS [Claim Token #1](https://github.com/mergeos-bounties/mergeos/issues/1) kèm link issue.
5. Chụp **≥2 ảnh gốc** (toàn cây + cận lá/hoa). Không lấy ảnh web không bản quyền.
6. Mở PR vào **PlantGuide** `master`:
   - `data/species/<id>.json`
   - `data/samples/obs_<id>.json`
7. PR ghi `Fixes #<issue>` + đính ảnh + ghi chú đồng ý chụp.
8. Chạy: `pip install -e ".[dev]"` rồi `plantguide care show -s <id>`, `pytest -q`, `ruff check src tests`""",
        "accept_h": "Điều kiện chấp nhận",
        "accept": "- JSON loài + sample\n- Lệnh care show chạy được\n- Có ảnh minh chứng trong PR\n- Tests + ruff pass\n- Cảnh báo độc tính nếu cần",
        "pay_h": "Thanh toán",
        "pay": "Maintainer merge → credit **25 MRG** (thường) theo thang 25/50/100/200.",
        "ethics_h": "Đạo đức",
        "ethics": "Nội dung chăm sóc mang tính giáo dục. Không thay lời khuyên y tế khi ngộ độc.",
    },
    "zh": {
        "title": "PlantGuide — 如何贡献一个物种（照片包）",
        "intro": "通过原创照片和养护卡片添加一个植物物种，获得 **MRG**。",
        "steps_h": "步骤",
        "steps": f"""1. **Star** PlantGuide 与 mergeos。
2. 选择 **species-pack** issue：{SPECIES_ISSUES}
3. 评论：`I claim this bounty`
4. 在 MergeOS Claim Token #1 评论并附 issue 链接。
5. 拍摄 **≥2 张原创照片**（整株 + 叶/花特写）。
6. PR 添加 `data/species/<id>.json` 与 `data/samples/obs_<id>.json`。
7. 写 `Fixes #<issue>` 并附照片。
8. 本地运行测试与 ruff。""",
        "accept_h": "验收标准",
        "accept": "JSON、care 命令、照片证据、测试/ruff、毒性说明（如需）。",
        "pay_h": "奖励",
        "pay": "合并后通常 **25 MRG**（档位 25/50/100/200）。",
        "ethics_h": "伦理",
        "ethics": "养护内容仅供学习，非医疗建议。",
    },
    "ja": {
        "title": "PlantGuide — 種の貢献ガイド（写真パック）",
        "intro": "オリジナル写真とケアカードで植物種を追加し **MRG** を獲得します。",
        "steps_h": "手順",
        "steps": f"""1. PlantGuide と mergeos を Star。
2. species-pack issue を選ぶ: {SPECIES_ISSUES}
3. コメント: `I claim this bounty`
4. MergeOS #1 に issue リンク。
5. オリジナル写真 2 枚以上。
6. species と sample の JSON を PR。
7. `Fixes #<issue>` と写真。
8. ローカルでテスト。""",
        "accept_h": "合格条件",
        "accept": "JSON・care・写真・tests/ruff。",
        "pay_h": "報酬",
        "pay": "マージ後 標準 **25 MRG**。",
        "ethics_h": "倫理",
        "ethics": "教育目的。医療助言ではありません。",
    },
    "ko": {
        "title": "PlantGuide — 종 기여 가이드 (사진 팩)",
        "intro": "원본 사진과 관리 카드로 식물 종을 추가해 **MRG**를 받습니다.",
        "steps_h": "단계",
        "steps": f"""1. PlantGuide, mergeos Star.
2. species-pack 이슈: {SPECIES_ISSUES}
3. 댓글: `I claim this bounty`
4. MergeOS #1에 링크.
5. 원본 사진 2장 이상.
6. species + sample JSON PR.
7. `Fixes #<issue>` + 사진.
8. 로컬 테스트.""",
        "accept_h": "수락 기준",
        "accept": "JSON, care, 사진, tests/ruff.",
        "pay_h": "보상",
        "pay": "머지 후 보통 **25 MRG**.",
        "ethics_h": "윤리",
        "ethics": "교육용. 의료 조언 아님.",
    },
    "es": {
        "title": "PlantGuide — Cómo contribuir una especie (fotos)",
        "intro": "Gana **MRG** añadiendo una especie con fotos originales y ficha de cuidados.",
        "steps_h": "Pasos",
        "steps": f"""1. Star PlantGuide y mergeos.
2. Issue species-pack: {SPECIES_ISSUES}
3. Comenta: `I claim this bounty`
4. También MergeOS #1 con el enlace.
5. ≥2 fotos originales.
6. PR con species + sample JSON.
7. `Fixes #<issue>` + fotos.
8. Tests locales.""",
        "accept_h": "Aceptación",
        "accept": "JSON, care, fotos, tests/ruff.",
        "pay_h": "Pago",
        "pay": "Tras el merge, típicamente **25 MRG**.",
        "ethics_h": "Ética",
        "ethics": "Cuidados educativos, no consejo médico.",
    },
    "fr": {
        "title": "PlantGuide — Contribuer une espèce (pack photo)",
        "intro": "Gagnez des **MRG** en ajoutant une espèce avec photos originales.",
        "steps_h": "Étapes",
        "steps": f"""1. Star PlantGuide et mergeos.
2. Issue species-pack: {SPECIES_ISSUES}
3. Commenter: `I claim this bounty`
4. Aussi MergeOS #1.
5. ≥2 photos originales.
6. PR species + sample.
7. `Fixes #<issue>` + photos.
8. Tests locaux.""",
        "accept_h": "Acceptation",
        "accept": "JSON, care, photos, tests/ruff.",
        "pay_h": "Paiement",
        "pay": "Après merge, souvent **25 MRG**.",
        "ethics_h": "Éthique",
        "ethics": "Contenu éducatif uniquement.",
    },
    "de": {
        "title": "PlantGuide — Art beitragen (Foto-Paket)",
        "intro": "Verdiene **MRG** mit Originalfotos und Pflegekarte.",
        "steps_h": "Schritte",
        "steps": f"""1. Star PlantGuide und mergeos.
2. species-pack Issue: {SPECIES_ISSUES}
3. Kommentar: `I claim this bounty`
4. Auch MergeOS #1.
5. ≥2 Originalfotos.
6. PR species + sample.
7. `Fixes #<issue>` + Fotos.
8. Tests lokal.""",
        "accept_h": "Akzeptanz",
        "accept": "JSON, care, Fotos, tests/ruff.",
        "pay_h": "Auszahlung",
        "pay": "Nach Merge typisch **25 MRG**.",
        "ethics_h": "Ethik",
        "ethics": "Nur Bildung, keine medizinische Beratung.",
    },
    "pt": {
        "title": "PlantGuide — Contribuir uma espécie (pacote de fotos)",
        "intro": "Ganhe **MRG** com fotos originais e cartão de cuidados.",
        "steps_h": "Passos",
        "steps": f"""1. Star PlantGuide e mergeos.
2. Issue species-pack: {SPECIES_ISSUES}
3. Comente: `I claim this bounty`
4. Também MergeOS #1.
5. ≥2 fotos originais.
6. PR species + sample.
7. `Fixes #<issue>` + fotos.
8. Testes locais.""",
        "accept_h": "Aceitação",
        "accept": "JSON, care, fotos, tests/ruff.",
        "pay_h": "Pagamento",
        "pay": "Após merge, tipicamente **25 MRG**.",
        "ethics_h": "Ética",
        "ethics": "Conteúdo educativo, não conselho médico.",
    },
    "id": {
        "title": "PlantGuide — Panduan kontribusi spesies (paket foto)",
        "intro": "Dapatkan **MRG** dengan foto asli dan kartu perawatan.",
        "steps_h": "Langkah",
        "steps": f"""1. Star PlantGuide dan mergeos.
2. Issue species-pack: {SPECIES_ISSUES}
3. Komentar: `I claim this bounty`
4. Juga MergeOS #1.
5. ≥2 foto asli.
6. PR species + sample.
7. `Fixes #<issue>` + foto.
8. Tes lokal.""",
        "accept_h": "Penerimaan",
        "accept": "JSON, care, foto, tests/ruff.",
        "pay_h": "Pembayaran",
        "pay": "Setelah merge biasanya **25 MRG**.",
        "ethics_h": "Etika",
        "ethics": "Hanya edukasi, bukan saran medis.",
    },
    "th": {
        "title": "PlantGuide — คู่มือส่งชนิดพืช (แพ็กภาพ)",
        "intro": "รับ **MRG** ด้วยรูปต้นฉบับและบัตรดูแล",
        "steps_h": "ขั้นตอน",
        "steps": f"""1. Star PlantGuide และ mergeos
2. Issue species-pack: {SPECIES_ISSUES}
3. คอมเมนต์: `I claim this bounty`
4. MergeOS #1 ด้วย
5. ≥2 รูปต้นฉบับ
6. PR species + sample
7. `Fixes #<issue>` + รูป
8. รันเทสต์""",
        "accept_h": "เกณฑ์รับ",
        "accept": "JSON, care, รูป, tests/ruff",
        "pay_h": "รางวัล",
        "pay": "หลัง merge มักได้ **25 MRG**",
        "ethics_h": "จริยธรรม",
        "ethics": "เพื่อการศึกษา ไม่ใช่คำแนะนำทางการแพทย์",
    },
    "hi": {
        "title": "PlantGuide — प्रजाति योगदान गाइड",
        "intro": "मूल फ़ोटो और देखभाल कार्ड से **MRG** कमाएँ।",
        "steps_h": "कदम",
        "steps": f"""1. PlantGuide और mergeos Star करें।
2. species-pack issue: {SPECIES_ISSUES}
3. कमेंट: `I claim this bounty`
4. MergeOS #1 पर लिंक।
5. ≥2 मूल फ़ोटो।
6. PR: species + sample.
7. `Fixes #<issue>` + फ़ोटो।
8. लोकल टेस्ट।""",
        "accept_h": "स्वीकृति",
        "accept": "JSON, care, फ़ोटो, tests/ruff.",
        "pay_h": "भुगतान",
        "pay": "मर्ज के बाद आमतौर पर **25 MRG**।",
        "ethics_h": "नैतिकता",
        "ethics": "केवल शैक्षिक; चिकित्सा सलाह नहीं।",
    },
    "ar": {
        "title": "PlantGuide — دليل المساهمة بنوع نبات",
        "intro": "احصل على **MRG** بصور أصلية وبطاقة عناية.",
        "steps_h": "الخطوات",
        "steps": f"""1. Star لـ PlantGuide و mergeos.
2. Issue species-pack: {SPECIES_ISSUES}
3. علّق: `I claim this bounty`
4. أيضاً MergeOS #1.
5. صورتان أصليتان على الأقل.
6. PR: species + sample.
7. `Fixes #<issue>` مع الصور.
8. الاختبارات محلياً.""",
        "accept_h": "القبول",
        "accept": "JSON والعناية والصور والاختبارات.",
        "pay_h": "المكافأة",
        "pay": "بعد الدمج عادةً **25 MRG**.",
        "ethics_h": "الأخلاق",
        "ethics": "محتوى تعليمي فقط وليس نصيحة طبية.",
    },
    "ru": {
        "title": "PlantGuide — Как добавить вид (фото-пакет)",
        "intro": "Заработайте **MRG** с оригинальными фото и карточкой ухода.",
        "steps_h": "Шаги",
        "steps": f"""1. Star PlantGuide и mergeos.
2. Issue species-pack: {SPECIES_ISSUES}
3. Комментарий: `I claim this bounty`
4. Также MergeOS #1.
5. ≥2 оригинальных фото.
6. PR: species + sample.
7. `Fixes #<issue>` + фото.
8. Локальные тесты.""",
        "accept_h": "Приёмка",
        "accept": "JSON, care, фото, tests/ruff.",
        "pay_h": "Выплата",
        "pay": "После merge обычно **25 MRG**.",
        "ethics_h": "Этика",
        "ethics": "Только образование, не медсовет.",
    },
}


def render(code: str, g: dict[str, str]) -> str:
    return f"""# {g['title']}

{g['intro']}

**Repository:** https://github.com/mergeos-bounties/PlantGuide  
**All languages:** [README.md](README.md)  
**Species issues:** {SPECIES_ISSUES}

## {g['steps_h']}

{g['steps']}

## {g['accept_h']}

{g['accept']}

## {g['pay_h']}

{g['pay']}

## {g['ethics_h']}

{g['ethics']}

---
Policy: [BOUNTY.md](../BOUNTY.md) · MergeOS: https://mergeos.shop · Lang: `{code}`
"""


def main() -> None:
    for code, g in GUIDES.items():
        path = ROOT / f"{code}.md"
        path.write_text(render(code, g), encoding="utf-8")
        print("wrote", path.name)
    print("total", len(GUIDES))


if __name__ == "__main__":
    main()
