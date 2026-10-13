# V5 — gia cường liên kết đáy và thành

Mở **`thung-rac-4-goc-v5.scad`**. STL, ảnh và báo cáo mặc định ở **`exports/v5/`**.
V5 là bản OpenSCAD mới; script Fusion trong `fusion/` vẫn là V4, chưa có các chi tiết V5.
Giữ nguyên V4 để đối chiếu. Không dùng lẫn thân V4 với khóa đáy V5.

## Gia cường

- **Đáy–đáy:** bốn khóa nơ đôi rời dài 40 mm trượt từ vùng tâm ra ngoài. Mỗi khóa ăn
  vào hai nửa ray thuộc hai thân góc khác nhau, giữ chúng trước dịch chuyển ngang
  và chênh cao. Ray nằm trên đáy, tại khoảng cách 30..74 mm từ tâm, nối với gân đáy
  thứ nhất. Mỗi khóa có một chốt giữ lắp từ trên; hình học chốt dùng chung với V4.
  Khóa đáy vẫn trượt được theo trục ray nếu tách khỏi cụm: khóa thành giữ vị trí
  các thân theo phương đó. Cần lắp đầy đủ cả hệ khóa thành và khóa đáy.
- **Đáy–thành:** bốn gân tam giác trên mỗi góc (16 gân/cụm), chân 16 mm, cao 24 mm,
  dày bằng gân đáy 4 mm. Gân nối tiếp các gân đáy tại 1/3 và 2/3 nửa cạnh lên thành.
  Góc trong đáy–thành có chuyển tiếp bán kính 3 mm, xấp xỉ bởi 8 đoạn cung trong
  mặt cắt; đây là hình học SCAD, không phải native fillet của Fusion.
- **Thành–thành:** tiếp tục dùng bốn khóa đứng dài theo thành và chốt V4. Hệ mới
  bổ sung liên kết dưới đáy, không thay hoặc tăng số khóa thành.

Các khóa đáy nằm phía trên mặt đáy, không nhô xuống dưới; mặt đặt sàn giữ phẳng.
Đáy được nối tại bốn vị trí gần tâm, không phải một thanh liền chạy hết mỗi đường ráp.
Chưa có tải cho phép hoặc kết quả in/thử tải; nguyên lý gia cường không phải bằng chứng
cho mức tăng độ bền cụ thể. Không kín nước.

## Chi tiết cần in

| STL | Số bản | Kích thước bao theo hướng xuất (mm) |
|---|---:|---:|
| `corner.stl` | 4 | 204 ×195,8 ×240 |
| `key.stl` — khóa thành | 4 | 236 ×12 ×32 |
| `floor_key.stl` — khóa đáy | 4 | 12 ×44 ×32 |
| `pin.stl` — chốt dùng chung | 8 | 8 ×17 ×4 |

Tổng **20 chi tiết in**, không vít/ê-cu/keo. Mọi part mặc định có footprint XY dưới
250 ×250 mm; thân cần Z 240 mm. Khóa thành dài 236 mm, brim 5 mm có bao 246 mm;
vẫn phải kiểm tra vùng in hữu dụng, skirt/support và hướng đường đùn trong slicer.
Hướng xuất STL là hướng kiểm tra kích thước, chưa phải xác nhận in không support.

`floor_coupon.stl` là hai nửa mối nối đáy (50 ×51 ×20 mm), cần tách thành hai object
trong slicer. In thêm một `floor_key.stl` và một `pin.stl` để thử.
`coupon.stl`, `coupon_key.stl` và `pin.stl` dùng cho mối nối thành như V4.
**`floor_key_sweep.stl` chỉ là thể tích quét cho audit, không phải chi tiết để in.**

## Thứ tự lắp/tháo

1. Thử coupon đáy và coupon thành trước. Khóa phải trượt được, chốt có thể rút bằng
   tay; không đóng búa. Chỉnh khe rồi xuất lại cả thân/coupon và khóa tương ứng.
2. Ghép bốn góc trên mặt phẳng ở cùng cao độ; góc cuối tiến chéo theo XY vào bậc đáy.
   Chưa lắp bất kỳ khóa/chốt nào trong bước ghép thân này.
3. Luồn bốn khóa thành từ trên xuống đến vai, lắp bốn chốt thành từ ngoài vào.
4. Đặt từng khóa đáy vào vùng trống giữa tâm, đúng cao độ rãnh. Trượt hướng ra thành
   đến khi vai chạm đầu ray. Bốn khóa giống nhau và quay 90° theo bốn đường ráp.
5. Đưa bốn chốt còn lại từ trên xuống lỗ trên ray/khóa đáy. Mỗi đường ráp chỉ có một
   lỗ chốt, ở nửa ray bên phải khi nhìn từ tâm ra thành.
6. Tháo theo thứ tự ngược: rút chốt đáy, kéo khóa về tâm, tháo chốt/khóa thành,
   sau đó mới tách thân.

Chốt giữ bằng ép nêm, không có ngàm snap giữ chốt. Độ giữ chốt, độ rão nhựa,
khoảng đưa tay vào thùng và lực lắp/rút cần thử thực tế. Bo/gân/khóa nhô trong lòng
thùng có thể cọ túi và giữ bụi; chưa có nắp che chúng.

## Tham số mới

| Tham số | Mặc định (mm) | Tác dụng |
|---|---:|---|
| `floor_fillet` | 3 | Bán kính chuyển tiếp đáy–thành |
| `gusset_run`, `gusset_height` | 16;24 | Chân và chiều cao gân tam giác |
| `floor_lock_start` | 30 | Đầu ray cách tâm |
| `floor_lock_length` | 40 | Chiều dài phần nơ đôi của khóa |
| `floor_lock_height` | 16 | Chiều cao ray trên đáy |
| `floor_key_clearance` | 0,15 | Khe mỗi mặt theo pháp tuyến, riêng khóa đáy |

Khe thành vẫn `key_clearance=0.25`; khe chồng đáy vẫn `floor_clearance=0.3`.
Ba giá trị này phục vụ ba tiếp xúc khác nhau. Khe khóa đáy được chọn 0,15 mm để
chặn dịch chuyển thử 1 mm theo X/Z trong audit mặc định. Tăng khe có thể giúp lắp
dễ hơn nhưng tăng độ rơ; cần kiểm tra lại và in coupon. `pin_interference=0.1`
là ép nêm chủ đích. Ngay cả khi đặt0, đầu chốt vẫn chồng 0,02 mm theo epsilon V4.
Ray phải giao với gân đáy đầu tiên và cách xa gân tam giác ở thành; assert sẽ từ
chối một số tổ hợp không phù hợp. Đây không phải bộ kiểm tra tổng quát mọi tham số.

## Kiểm chứng tái lập

Môi trường Python cần các dependency trong `requirements.txt`; OpenSCAD cần backend
Manifold. Dùng môi trường đã cài hoặc tạo môi trường riêng trên host của bạn.

```powershell
$env:OPENSCAD = (Get-Command openscad).Source
python -B build-v5.py
python -B verify-v5-variants.py
```

Trên workspace hiện tại dùng:

```powershell
$env:OPENSCAD = 'H:\OpenSCAD\portable\OpenSCAD-2026.09.29-x86-64\openscad.com'
& 'H:\OpenSCAD\work\toothbrush-tools\Scripts\python.exe' -B build-v5.py
& 'H:\OpenSCAD\work\toothbrush-tools\Scripts\python.exe' -B verify-v5-variants.py
```

`build-v5.py` xuất STL và kiểm tra kín mesh/số component/đặt trên bàn/XY250;
kiểm tra 190 cặp chi tiết của cụm 20 part, tách giao thể tích ép chốt khỏi các va chạm.
Kiểm tra khóa đáy chặn dịch chuyển 1 mm theo ±X và±Z của cả hai miếng, chốt chặn rút
khóa 1 mm, cùng khả năng dùng khóa/chốt thật trên coupon đáy. Kiểm tra riêng khóa
thành chặn từng thân dịch 1 mm theo ±X/±Y, bao gồm phương dọc ray đáy.

Đường khóa đáy được kiểm tra bằng **thể tích quét liên tục** của bao hình khóa
(lấp kín lỗ chốt, nên bảo thủ), từ cách vị trí cuối 44 mm tới vị trí cuối, với ba
khóa/chốt đáy còn lại đã ở vị trí lắp. Đường chốt thành/đáy kiểm tra quét liên tục
hai khối lồi của chốt từ 60 mm tới 2 mm trước vị trí cuối; phần ép nêm cuối kiểm tra
riêng bằng mẫu vị trí và giao thể tích. Ghép góc cuối và luồn khóa thành vẫn chỉ
kiểm tra các vị trí mẫu, không khẳng định quét liên tục toàn bộ quá trình.

`verify-v5-variants.py` chạy lại toàn bộ audit cho ba cấu hình: thân 320/cao 200;
thân 390/cao 230/thành 4/đáy 5/gân tam giác 20×30/ray cao 18; và chốt không ép nêm
với khe khóa thành 0,15. Có thêm ca ray không giao gân đáy phải bị từ chối.
Kết quả riêng lưu trong `work/v5-variants/`, không ghi đè exports mặc định.
Audit từ chối chạy với `python -O` hoặc `PYTHONOPTIMIZE` để tránh bỏ các assert.

Các Boolean chỉ tiếp xúc mặt có thể phát cảnh báo mass-properties thể tích 0 của
trimesh; log render OpenSCAD được lưu riêng cho mỗi artifact. Thể tích nhựa đặc
hình học mặc định khoảng 2,98 lít, không phải lượng filament sau slice.

Chưa kiểm chứng slicer/G-code, in thực, dung sai/co ngót, tải lâu dài/va đập,
độ giữ chốt, hoặc Fusion V5. Báo cáo `audit.json` chỉ xác nhận hình học của cấu hình
vừa build, không phải mô phỏng ứng suất hay chứng nhận tải.
