# Thùng rác bốn góc V4 — Autodesk Fusion

## Chạy và chỉnh kích thước

1. Trong Fusion vào **Utilities > Add-Ins > Scripts and Add-Ins > Scripts > +**.
2. Chọn thư mục `ThungRac4Goc` chứa `ThungRac4Goc.py` và `ThungRac4Goc.manifest`, rồi **Run**. Không cần Python/thư viện bên ngoài Fusion.
3. Mỗi Run tạo document Parametric mới với một component `FourCornerBinV4`; mục tiêu source là 4 thân góc, 4 khóa đuôi én đôi và 4 chốt nêm. Bố trí ở trạng thái lắp; chọn riêng body để xuất/in, không in nguyên cụm. Số solid thực tế phải kiểm tra trong Fusion.
4. Vào **Modify > Change Parameters**. Hình học sketch, cao độ, chiều dài và vị trí ray/chốt dùng expression; không cần Run lại khi đổi kích thước. Giữ công thức của nhóm tự tính. Script không chạy nền; sau chỉnh tham số cần kiểm tra timeline và miền hợp lệ.

Theo [hướng dẫn chạy script Autodesk](https://help.autodesk.com/cloudhelp/ENU/Fusion-Model/files/SLD-MANAGE-SCRIPTS-ADD-INS.htm).

## Tham số chính

Tất cả đơn vị mm. Mỗi User Parameter có comment Việt ghi ý nghĩa/ảnh hưởng.

| Tham số | Mặc định | Ý nghĩa / giới hạn |
|---|---:|---|
| `body_size`, `body_height` | 360, 240 | Cạnh ≥320; cao ≥120 |
| `wall`, `floor_thickness` | 3,2; 4 | Thành 3..8, nhỏ hơn R góc; đáy ≥4 |
| `corner_radius` | 18 | Lớn hơn thành, nhỏ hơn body_size/4 |
| `rib_projection`, `rib_thickness` | 10, 3 | Gân ngoài |
| `band_projection`, `band_height` | 8, 24 | Đai ngoài; cao > nhô và < nửa cao thân |
| `floor_rib_height`, `floor_rib_width` | 8, 4 | Gân trong đáy, không lên vùng chốt |
| `rib_fillet` | 1,5 | Bán kính offset native biên dạng gân |
| `seam_gap` | 0,4 | Khe ráp thân/ray; 0..1 |
| `key_clearance` | 0,25 | Khe vuông góc mỗi mặt khóa; 0,15..0,5 |
| `rail_width`, `rail_projection` | 48, 16 | Rộng tổng hai nửa ray ≥44, <body_size/3; nhô ≥16 |
| `key_stop` | 8 | Cao vai chặn khóa; nhỏ hơn body_height−18,25 |
| `floor_lap`, `floor_clearance` | 8; 0,3 | Môi ≥8, <body_size/8; khe 0..0,6 |
| `pin_interference` | 0,1 | Ép nêm chủ đích; 0..0,2 |

Công thức: `half_body = body_size/2`, `rail_y = half_body + rail_projection/2`, `key_length = body_height-key_stop`, `pin_z = body_height-12 mm`. Parent bowtie dùng cùng sketch cho khóa và slot, bo tròn native bán kính 0,6 mm như SCAD; slot dùng `Sketch Offset2` associative với `key_clearance` theo pháp tuyến. Slot Y dùng `+key_clearance` theo chiều phải của chuỗi CCW; slot X dùng `-key_clearance` vì winding bị đảo khi mirror. Các tọa độ lỗ của ray và khóa dùng cùng biểu thức. Tiết diện khóa ±16/±6 × ±4/±2, vai 32×12×4, chốt dài14+đầu3, cao4 và lỗ4,6×4,5 là contract cố định của SCAD V4; không tự scale theo kích thước thùng.

## Timeline và điều chỉnh so với SCAD

Timeline dựng sàn/góc thành → vành/đai → nhóm gân ngoài/gân đáy → môi và bậc nhận → hai ray, slot và lỗ chốt → khóa/vai/lỗ → chốt → Circular Pattern ba body thành bốn bộ. Nhóm gân ngoài dùng một Extrude tạo bốn tool body, một Fillet và một Combine; nhóm gân đáy dùng một Extrude Join. Đầu khóa và đầu chốt dùng NewBody rồi Combine vào body đích để không auto-join với ray/thân đang tiếp xúc; các phần Join vào `corner` được dựng khi chỉ có body thân. Không có STL/import hình học.

- Bo góc tròn dùng cung sketch native qua cùng tâm và bán kính biểu thức; toàn bộ điểm đầu mút có driving expressions theo kích thước/R.
- Đai giữa giữ đúng hai đoạn theo SCAD: loft ramp cao `band_projection`, sau đó extrusion thẳng với biên dạng đã mở rộng cao `band_height-band_projection`. Có thể cần support khi in.
- Bốn gân ngoài dùng một sketch/NewBody tool, `Sketch Offset2` associative theo `rib_fillet`, một native `FilletFeatures` trên các cạnh đứng của cả nhóm rồi một `Combine` vào thân. Bốn gân đáy dùng một sketch/Join cùng cao độ; bốn hình chữ nhật cắt nhau nên Fusion có thể trả về toàn bộ planar arrangement (mặc định 16 profile), và builder truyền tất cả profile đó cho cùng Extrude Join. Khóa Fusion giữ parent bowtie bo0,6, khe pháp tuyến và phạm vi gân, không thay khóa bằng hình chữ nhật. Khóa Fusion không được coi là đã thử lắp lẫn với STL V4; in coupon theo bộ tương ứng trước.
- Giữ môi/bậc đáy, khe seam, lỗ chốt theo pháp tuyến mặt thùng. Khóa đưa từ trên xuống; chốt từ ngoài vào; không quay về đường chốt tiếp tuyến bị chắn của V3.

## Kiểm chứng

`VERIFY_VARIANTS = True` bật ba ca đổi cạnh/cao, dày thành/đáy và ray/khe/ép nêm. Trong Fusion kiểm tra recompute, feature health, sketch đủ ràng buộc, số `bRepBodies`/solid mục tiêu 12, kích thước từng part và kích thước bao theo tham số hiện tại; `finally` phục hồi expression gốc rồi kiểm tra lại. Khi lỗi, hộp thoại nêu giai đoạn/feature; giữ document lỗi để xem timeline. Có thể gọi `check_model(design)` từ môi trường API/debug để kiểm tra sau chỉnh tay.

Offline:

```powershell
python -B -m unittest discover -s tests -p test_fusion_bin.py -v
```

Ngày2026-10-12: bộ test hình học/API contract hiện tại kiểm tra đúng các profile expressions mà builder dùng: floor/seam/góc, cung tròn native, bowtie parent bo0,6 và offset associative theo winding, band ramp + straight, offset trapezoid gân, planar union gân đáy, pin/bore chung tọa độ, môi/bậc và đổi kích thước. `layout()` giữ contract source 12 body và bounds danh nghĩa398×398×244; số solid thực tế vẫn cần Fusion runtime. Các số audit Manifold 4 bộ tham số, thể tích pin và kiểm tra lấn dưới đây thuộc snapshot polygon trước refactor native này; chúng không phải bằng chứng cho geometry kernel hiện tại. Phần đầu chốt có chồng0,02 mm theo epsilon nguồn, nên đặt `pin_interference=0` không đồng nghĩa toàn cụm tuyệt đối không giao thể tích.

**Trạng thái hiện tại:** 20 test offline + `py_compile` đạt sau refactor native. Theo builder source, kế hoạch có 20 bước, 21 sketch/profile plane (band loft dùng hai section), 19 extrusion, một loft, một nhóm fillet rib, ba Combine (gân ngoài, đầu khóa, đầu chốt) và một Circular Pattern; đây là số lượng được suy ra từ source, chưa phải timeline runtime. Chưa chạy ứng dụng Fusion cho bản này: chưa xác nhận solver sketch, `SketchArcs.addFillet`, `Sketch Offset2`, BRep/kernel, số solid thực tế, feature health hoặc `VERIFY_VARIANTS` thực tế. Test offline không chứng minh API dựng thành công, đường lắp liên tục, lực lắp, slicer, tải hoặc in thực. Cần Run script và kiểm tra biến thể trong Fusion, sau đó in coupon/kiểm tra đường lắp và mẫu trước khi in đủ bộ.

API đối chiếu: [SketchPoints.add](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_SketchPoints_add.htm), [SketchDimensions.addDistanceDimension](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_SketchDimensions_addDistanceDimension.htm), [Extrude.setOneSideExtent](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_ExtrudeFeatureInput_setOneSideExtent.htm), [CombineFeatures.createInput](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_CombineFeatures_createInput.htm), [CircularPatternFeatures.createInput](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_CircularPatternFeatures_createInput.htm). Đã đối chiếu thêm wrapper API Fusion cài trên máy bản2705.1.30; đó là kiểm tra chữ ký API, không phải runtime proof.

Audit polygon cũ cũng lấy mẫu đường chốt ở các độ dịch2/5/10/20/40/60 mm và không thấy va chạm với thân/khóa. Đây là bằng chứng của snapshot cũ, không phải xác nhận swept-volume của refactor native; bản thân phép kiểm tra cũng chưa phải swept-volume liên tục hoặc kiểm tra lực lắp thực tế.

### Lịch sử chẩn đoán runtime trước refactor native

Lần chạy trước refactor native thất bại tại `Corner floor` với `VCS_SKETCH_OVER_CONSTRAINTS`. Các mốc 10/11 test dưới đây là lịch sử chẩn đoán solver của bản trước; không dùng chúng làm kết quả kiểm chứng bản hiện tại.

### Bản sửa sau log chi tiết (lịch sử)

Log xác định đỉnh 2, trục Y, điểm `(180, 0.2) mm` không fixed/reference và không có geometric constraint. Đã thay dimension tọa độ điểm–gốc bằng `addOffsetDimension` từ hai trục dựng cố định: khoảng cách tới trục Y điều khiển X, tới trục X điều khiển Y. Giữ nguyên expression liên kết tham số, hình học và các kiểm tra fully constrained/profile. Không đổi sang driven dimension và không fix điểm model. **11 test offline + compile đạt ở bản cũ**; chưa kết luận nguyên nhân nội bộ của solver Autodesk.

### Sửa đầu mút trục dựng

Lần Run tiếp theo qua offset dimensions nhưng `Corner floor profile` vẫn chưa fully constrained. Bản trước fix đường datum, chưa fix riêng các đầu mút có thể trượt dọc đường trong solver Fusion. Đã fix start/endSketchPoint của cả hai trục construction; model points vẫn driving theo tham số và kiểm tra fully constrained được giữ. Regression offline xác nhận bốn đầu mút phải fixed trước khi thêm offset; 11 test đạt ở bản cũ. Refactor native hiện tại vẫn cần runtime Fusion mới để xác nhận.

## Bài học sketch Fusion

Các quy tắc dưới đây rút từ phiên sửa runtime/API của ThungRac4Goc (2026-10-12). Chúng mô tả cách dựng sketch parametric qua API và các mốc kiểm chứng của script.

1. **Cung tròn (`Corner floor` / tường bo góc):** mỗi arc tạo bằng `addByCenterStartEnd` mang thêm `addRadialDimension` driving với expression bán kính. Chỉ drive tâm và hai đầu mút vẫn để cung thiếu ràng buộc.
2. **Hình chữ nhật (`Floor ribs`):** drive cả bốn góc bằng `addOffsetDimension` từ hai trục construction đã fix đầu mút, rồi nối bốn cạnh. Pattern một neo + chiều rộng/cao (kiểu TimetableBoard / `addTwoPointRectangle`) không đủ tin cậy trên API: khóa đường chéo vẫn để hai góc còn lại shear. Nhóm nhiều rectangle (Outer ribs / Floor ribs) dùng cùng chiến lược đa góc như `_polygon_sketch`.
3. **Mock offline:** `isFullyConstrained=True` trên mock không chứng minh DOF thật. Regression phải đếm số điểm, số offset và số cạnh (ví dụ 4 góc → 8 offset khi cách gốc).
4. **Gân gia cường vs SCAD:** Outer ribs, Floor ribs và `rib_fillet` (offset + fillet native) đã đối chiếu MATCH với `thung-rac-4-goc-v4.scad` theo contract expressions/tests hiện tại. Vẫn cần Run trong Fusion để xác nhận solver và feature health.
