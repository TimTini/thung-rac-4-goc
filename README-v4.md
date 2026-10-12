# V4 — sửa đường lắp chốt, tham khảo nguồn công khai

Mở `thung-rac-4-goc-v4.scad`. STL/ảnh/báo cáo ở `exports/v4/`. Không dùng lẫn khóa hoặc chốt V3/V4 vì hướng lỗ chốt khác nhau. Bản này vẫn không dùng vít/ê-cu/keo.

## Nguồn đã đọc

1. Robert Meisner, **3D Printed Case (Modular!) for your DIY Project**: https://catchit.pl/blog/modular-3d-printed-case-diy-project/ . Tác giả trình bày đầu nối rời gồm hai đuôi én đối nhau, rãnh để trượt đầu nối và khe hở lắp; có ảnh của hộp in thực. Đây là nguồn tham khảo cho nguyên lý đầu nối rời. Hộp điện tử của tác giả có chi tiết bắt vít ở phần khác, không phải mẫu thùng rác không vít tương đương. Bài cũng nói các đoạn code là trích đoạn, không phải source hoàn chỉnh.
2. Luc Milland, **Diabolobox**: https://github.com/ptitluc/diabolobox . Thư viện OpenSCAD công bố hộp không vít/keo, các tấm có ray và mối nối dạng diabolo, có source và chế độ tách/lắp. Đã đọc README và các module `diabolize_bt`, `diabolize_lr`, `diabolize_fb`. Đây là nguồn đối chiếu cách thiết kế hệ ray theo chiều lắp; không lấy nguyên thiết kế tấm phẳng để thay bốn góc chữ L.

**V4 vẫn là hình học tự triển khai cho thùng này.** Không sao chép source hai tác giả, không tuyên bố họ đã thử nghiệm mẫu thùng này hoặc thông số chịu tải của nó. Kích thước khóa dài và chốt nêm V4 vẫn cần in thử.

## Lỗi V3 đã tái hiện

V3 đưa chốt dài 51 mm theo phương tiếp tuyến mặt thùng. Đường vào đi qua gân dọc tại X khoảng -61 mm. Ở các vị trí cách trạng thái lắp xong 35/45/60 mm, chốt giao thể tích với gân khoảng 88–106 mm³. Kiểm tra V3 trước chỉ xét chốt ở vị trí cuối và bỏ sót hành trình này.

Lệnh tái hiện: `audit-v3-pin-path.py`; kết quả: `exports/v3/pin-path-failure.json`. Đây là bằng chứng đường lắp thẳng đã hướng dẫn bị chắn, không phải chỉ là cảnh báo dung sai/co ngót.

## Thay đổi V4

- Khóa đuôi én đôi vẫn luồn Z từ trên sau khi ghép bốn góc.
- Chốt ngắn 17 mm đưa **từ ngoài thẳng vào mặt thùng**, theo phương pháp tuyến. Không chạy ngang qua các gân bên cạnh.
- Lỗ chốt trên cả ray và khóa đổi hướng tương ứng. Đầu chốt nhô phía ngoài để kéo ra; lỗ kết thúc trong khối ray, không xuyên vào lòng thùng.
- Giữ gân ngoài, đai thân, gân đáy bên trong và bậc ghép đáy. Tổng 4 thân + 4 khóa + 4 chốt = 12 chi tiết in.

| STL trong exports/v4 | Số bản | Kích thước bao mặc định (mm) |
|---|---:|---|
| corner.stl | 4 | 204 × 195,8 × 240 |
| key.stl | 4 | 236 × 12 × 32, nằm ngang khi in |
| pin.stl | 4 | 8 × 17 × 4, nằm phẳng khi in |

Kích thước thân danh nghĩa 360 × 360 × 240; toàn cụm tính đầu chốt ngoài và đầu khóa: 398 × 398 × 244 mm. Người dùng xác nhận bàn in 250 mm; audit hiện đối chiếu XY từng part với 250 × 250 mm. Chưa biết giới hạn Z của máy; thân cần Z ít nhất 240 mm.

Thanh khóa **đã đặt nằm ngang trong key.stl**, chiếm XY 236 × 12 mm, cao 32 mm. Đặt giữa bàn 250 mm chừa 7 mm mỗi đầu; brim 5 mm cho bao XY 246 × 22 mm, còn 2 mm mỗi đầu tới mép. Đối chiếu vùng cấm/kẹp bàn/skirt/support trong slicer thực trước khi in. `key-bed-250-preview.scad` và ảnh `exports/v4/key-bed-250.png` chỉ minh họa footprint, không phải G-code. Không xuất/in cảnh preview có cả bàn giả và chữ.

## Lắp thử

1. In `coupon.stl` (tách thành hai object), `coupon_key.stl`, `coupon_pin.stl` của **V4** trước.
2. Ghép hai nửa ray, luồn khóa ngắn từ trên xuống đến vai. Đưa chốt ngắn **từ mặt ngoài vào**, không từ cạnh bên. Thử kéo hai nửa tách nhau, nhấc khóa, rút chốt rồi rút khóa.
3. `key_clearance=0.25` mm mỗi mặt; `pin_interference=0.1` mm tổng bề rộng tại gốc nêm. Nêm có ép nhẹ chủ đích; không đóng búa. Coupon chưa kiểm chứng độ thẳng của khóa/ray dài hoặc chịu tải.
4. Với thùng đủ kích thước, ghép thân trên mặt phẳng cùng cao độ; góc cuối tiến chéo nằm ngang vào bậc đáy. Luồn 4 khóa, sau đó đưa 4 chốt ngắn từ ngoài vào. Tháo theo thứ tự ngược lại.

Gân đáy phía trong có thể cọ túi/giữ bụi. Bậc nhận dưới đáy nhô khoảng 8 mm, vành miệng và lỗ chốt ngang cần kiểm tra support trong slicer. Chưa xác nhận in không support. Không kín nước; chưa có tải cho phép hoặc bằng chứng xách thùng đầy.

## Kiểm chứng và giới hạn

- OpenSCAD Manifold render không warning/error; STL kín, coupon hai component, các chi tiết khác một component; STL đã bỏ tam giác diện tích 0 và nạp lại kiểm tra.
- 28 cặp thân/khóa không lấn thể tích. Chốt có phần ép nêm chủ đích ~0,664 mm³/seam, báo riêng, không gọi toàn cụm là zero interference.
- Đã kiểm tra vị trí chốt ở 10 độ dịch và **thể tích quét liên tục của hai khối lồi tạo thành chốt** trên đường tiến từ cách vị trí cuối 60 mm tới 2 mm: không chạm thân/khóa. Hai mm cuối là vùng nêm ép vào lỗ, cần in thử để xác nhận lực lắp.
- Kiểm tra khóa bị chặn khi nhấc 1 mm và dịch XY 1 mm; coupon có kiểm tra chốt/khóa tương ứng.
- Đường ghép thân và luồn khóa dài vẫn chỉ kiểm tra các vị trí mẫu, chưa phải mô phỏng liên tục toàn bộ các bước. Chưa có in thực, slicer, đo lực lắp hoặc thử tải. Sửa được lỗi đường chốt đã tìm thấy không đồng nghĩa xác nhận toàn bộ cụm lắp được ngoài thực tế.

Chạy lại:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:OPENSCAD = (Get-Command openscad).Source
python audit-v3-pin-path.py
python build-v4.py
```

Script audit dùng một số contract số giống SCAD (tiết diện khóa, pin dài14+đầu3, coupon42); các thay đổi contract đi cùng cập nhật script. Trimesh có thể cảnh báo khi tính mass-properties trên mặt tiếp xúc zero volume; log OpenSCAD và audit là các bằng chứng riêng. Source, exports và script kiểm chứng được quản lý trong repo.

## Fusion native

Script Fusion parametric V4: `fusion/ThungRac4Goc/ThungRac4Goc.py`; manifest và
giới hạn: `fusion/ThungRac4Goc/README.md`. Script tạo 4 thân góc, 4 khóa và
4 chốt bằng sketch/feature native; runtime Fusion vẫn cần chạy trực tiếp để
xác minh health, bounds và các biến thể `VERIFY_VARIANTS`.
