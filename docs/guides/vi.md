# PlantGuide — Hướng dẫn đóng góp loài cây (gói ảnh)

Nhận **MRG** khi thêm **một loài** kèm ảnh gốc và thẻ chăm sóc.

**Repository:** https://github.com/mergeos-bounties/PlantGuide  
**All languages:** [README.md](README.md)  
**Species issues:** https://github.com/mergeos-bounties/PlantGuide/issues?q=is%3Aissue+is%3Aopen+label%3Aspecies-pack

## Các bước

1. **Star** [PlantGuide](https://github.com/mergeos-bounties/PlantGuide) và [mergeos](https://github.com/mergeos-bounties/mergeos).
2. Chọn issue **species-pack**: https://github.com/mergeos-bounties/PlantGuide/issues?q=is%3Aissue+is%3Aopen+label%3Aspecies-pack
3. Comment trên issue: `I claim this bounty`
4. Comment thêm trên MergeOS [Claim Token #1](https://github.com/mergeos-bounties/mergeos/issues/1) kèm link issue.
5. Chụp **≥2 ảnh gốc** (toàn cây + cận lá/hoa). Không lấy ảnh web không bản quyền.
6. Mở PR vào **PlantGuide** `master`:
   - `data/species/<id>.json`
   - `data/samples/obs_<id>.json`
7. PR ghi `Fixes #<issue>` + đính ảnh + ghi chú đồng ý chụp.
8. Chạy: `pip install -e ".[dev]"` rồi `plantguide care show -s <id>`, `pytest -q`, `ruff check src tests`

## Điều kiện chấp nhận

- JSON loài + sample
- Lệnh care show chạy được
- Có ảnh minh chứng trong PR
- Tests + ruff pass
- Cảnh báo độc tính nếu cần

## Thanh toán

Maintainer merge → credit **25 MRG** (thường) theo thang 25/50/100/200.

## Đạo đức

Nội dung chăm sóc mang tính giáo dục. Không thay lời khuyên y tế khi ngộ độc.

---
Policy: [BOUNTY.md](../BOUNTY.md) · MergeOS: https://mergeos.shop · Lang: `vi`
