# V6 thử nghiệm — khóa cầu chìm dưới đáy

Mở **`thung-rac-4-goc-v6.scad`**; STL/ảnh/audit ở **`exports/v6/`**.
Giữ V5 để đối chiếu. Script Fusion hiện vẫn là V4, chưa có hình học V6.

## Thay đổi so với V5

- Bỏ ray nhô 16 mm và bốn chốt đáy. Mỗi đường ráp dùng một khóa cầu **28 ×12 ×6 mm**,
  có hai đầu chữ T ăn vào hai miếng đáy. Đế khóa nằm ngang mặt đặt sàn, không cần chân.
- Nền quanh hốc tăng cục bộ từ 4 lên **8 mm**: nhô 4 mm vào lòng thùng, thấp hơn gân
  đáy cũ (đỉnh Z 12). Pad có phần đỉnh 34 ×30 mm, chân ramp rộng hơn, tại bốn seam.
- Gân tam giác đáy–thành giảm chân 16/cao 24 thành **chân 12/cao 16 mm**; giữ bo R3.
- Tổng **16 part**, giảm từ 20: 4 thân, 4 khóa thành, 4 chốt thành, 4 khóa đáy.
- Ưu tiên FDM ít support: vai khóa vát 45°, lưỡi ngàm bắt đầu ngay trên bàn,
  đế khóa dạng thanh hẹp thay tấm đặc. Bỏ môi/bậc chồng đáy V4/V5 và vát mặt
  dưới vành miệng 45°; các khóa đáy mới giữ hai mép phẳng với nhau.

Đây là prototype để thử coupon. Đầu T chịu giữ chênh cao và lực tách ngang;
lưỡi đàn hồi nhỏ chỉ chống khóa trượt ngược theo ray. Mối khóa thành giữ vị trí
các thân theo phương XY. Không coi ngàm nhỏ là chi tiết chịu tải chính.

## Chi tiết in

| STL | Số bản | Hướng xuất/kích thước bao mặc định (mm) |
|---|---:|---|
| `corner.stl` | 4 | Đáy xuống bàn; 195,8 ×195,8 ×240 |
| `key.stl` | 4 | Nằm ngang; 236 ×12 ×32 |
| `pin.stl` | 4 | Nằm phẳng; 8 ×17 ×4 |
| `floor_key.stl` | 4 | Đế xuống bàn; 28 ×12 ×6 |
| `floor_coupon.stl` | Thử trước | Hai nửa mối nối; 48 ×40 ×12 |

In thử `floor_coupon.stl` (tách thành hai object) + một `floor_key.stl` trước.
Thử coupon thành bằng `coupon.stl`, `coupon_key.stl` và `pin.stl` như V4/V5.
Các STL trong **`exports/v6/audit/` chỉ là thể tích quét/hình ngàm đang ép, không in**.

Footprint CAD từng part nằm trong XY 250 mm; thân cần Z 240 mm. Khóa thành 236 mm
với brim 5 mm chiếm 246 mm. Chưa kiểm tra vùng cấm/skirt/support của thân đầy đủ.
Vai đầu khóa vát 45° và lớp đầu liền mạch. Hốc dưới đáy vẫn có trần bridge:
nhịp danh nghĩa mặc định khoảng 7,5 mm tại đầu khóa và 11,5 mm tại thanh nối;
không còn hốc đế rộng 28 ×22,5 mm của bản thử ban đầu. Chọn hướng bridge qua
bề ngang ngắn trong slicer và xem preview từng lớp. Mục tiêu thử coupon với
support tắt trước, không coi đây là xác nhận in không support. Nếu bridge võng
hoặc lắp kẹt, phải kiểm tra coupon/profile trước khi in thân đầy đủ. Nhiệt độ,
hướng đường đùn, vật liệu và co ngót ảnh hưởng cả bridge và ngàm.

## Lắp/tháo

1. Trên coupon, nhận diện hai cửa nạp lớn phía mặt dưới và hai hốc giữ đầu T.
2. Đặt khóa lệch về tâm **8 mm** so với vị trí cuối. Đưa hai đầu T từ dưới lên qua
   cửa nạp tới khi đế khóa ngang mặt đáy. Lưỡi đàn hồi lúc này ở cửa nạp riêng.
3. Nhấn lưỡi nhỏ xuống phía mặt dưới, trượt khóa **ra phía thành 8 mm**, rồi thả để
   răng ngàm vào hốc giữ. Hai đầu T nằm sau phần nhựa giữ của mỗi miếng đáy.
4. Thử tách ngang/chênh cao hai nửa coupon; kiểm tra ngàm chặn khóa trượt về tâm.
5. Để tháo: nhấn lưỡi từ phía dưới, kéo khóa về tâm 8 mm, rồi hạ qua cửa nạp.
   Không bẻ hai đầu T qua mép hốc và không đóng búa.
6. Với cả thùng: ghép bốn thân và lắp khóa/chốt thành trước; lật thùng rỗng để
   tiếp cận mặt dưới, lắp bốn khóa đáy theo các bước trên. Tháo khóa đáy trước khi
   tháo khóa thành và tách thân.

Ngàm cần chuyển động xuống dưới mặt đặt sàn khi bấm; thao tác trên thùng/coupon
được kê hoặc lật để có khoảng trống, không ép ngàm trên bàn phẳng. Thùng không
kín nước: cửa nạp/hốc và đường ráp vẫn có khe. Phần tăng dày bên trong được giữ
kín ở vùng trần đầu T, không có lỗ chốt xuyên mặt trên.

## Giới hạn ngàm đàn hồi

Lưỡi ngàm rộng 3 mm, dày 1,2 mm, dài tự do 9 mm, có răng cao tới Z 2,6. Audit dùng
chuyển vị đầu lưỡi 0,9 mm, mô tả bằng đường cong cantilever để kiểm tra khoảng hở.
**Đây là hình học giả định khi bấm, không phải kết quả giải lực/ứng suất/biến dạng**.
Chưa xác nhận ngàm có bấm được với filament cụ thể, có nứt/tách lớp, hoặc chịu
được bao nhiêu chu kỳ. Coupon có thể cần đổi chiều dài/dày lưỡi, khe hoặc vật liệu.

Đầu T và pad cũng chưa thử tải. Trần hốc mặc định còn **khoảng 1,7 mm**; không suy ra tải
cho phép từ giá trị này. Lắp vừa coupon chưa chứng minh thùng lớn chịu tải tốt.

## Tham số và audit

| Tham số | Mặc định (mm) | Ý nghĩa |
|---|---:|---|
| `floor_clip_y` | 50 | Đầu đế khóa tại vị trí cuối cách tâm |
| `floor_clip_travel` | 8 | Hành trình từ cửa nạp tới vị trí giữ |
| `floor_clip_clearance` | 0,25 | Khe mỗi mặt của hốc/khóa |
| `floor_pad_height` | 8 | Cao độ đỉnh pad, tính từ mặt đặt sàn |
| `floor_latch_press` | 0,9 | Chuyển vị giả định để audit khoảng hở khi bấm |

Kích thước khóa và ngàm là contract cố định trong source, không tự scale theo
thùng. Pad phải giao gân đáy đầu tiên, còn trần đầu T ít nhất 1,5 mm và có khoảng
trống gần tâm; assert từ chối một số cấu hình sai, không bao quát mọi tổ hợp.

```powershell
$env:OPENSCAD = (Get-Command openscad).Source
python -B build-v6.py
python -B verify-v6-variants.py
```

Trên workspace hiện tại dùng OpenSCAD nightly tại
`H:\OpenSCAD\portable\OpenSCAD-2026.09.29-x86-64\openscad.com` và Python tại
`H:\OpenSCAD\work\toothbrush-tools\Scripts\python.exe` (dependency theo requirements.txt).

Audit kiểm tra mesh kín/số component, mặt đặt bàn, XY 250, 120 cặp của 16 part,
giao thể tích ép chốt thành báo riêng. Kiểm tra từng đầu T chặn hai miếng theo
±X/±Z 1 mm; khóa thành chặn từng thân theo ±X/±Y 1 mm; ngàm nghỉ chặn kéo khóa 1 mm.
Có probe solid để kiểm tra trần hốc và phần nhựa tì dưới đầu T thực sự tồn tại.
Audit mesh khóa yêu cầu không có mặt dưới vượt ngưỡng 45° phía trên mặt bàn
(diện tích 0 mm²), lớp đầu tại Z 0,1 mm liền mạch, nhịp bridge hốc mới danh nghĩa
không quá 14 mm. Đây là kiểm tra hình học; bằng chứng slice offline được tách riêng dưới đây.

Đường đưa khóa lên 15 mm, trượt 8 mm khi giữ ngàm ép, và nhấn ngàm tại vị trí cuối
được kiểm tra bằng bao thể tích quét bảo thủ, gồm cả trường hợp ba khóa khác đã
lắp. Hình ngàm ép được kiểm tra thêm 17 vị trí trượt. Chưa giải chuyển động đàn hồi
khi tự trượt răng qua mép hốc. Góc cuối và khóa thành vẫn là đường lắp lấy mẫu;
chốt thành có quét liên tục 60..2 mm và lấy mẫu phần ép nêm cuối như V5.

`verify-v6-variants.py` chạy cấu hình thân nhỏ 320/cao 200, thân 390/cao 230/thành 4/
đáy 5/pad 9, khe chặt 0,15 và khe rộng 0,35/hành trình 10. Các ca trần quá mỏng,
hành trình quá ngắn hoặc pad không giao gân phải bị từ chối. Không chạy audit với
Python -O/PYTHONOPTIMIZE. File kết quả biến thể nằm trong `work/v6-variants/`.

Chưa có in thực, tải, lực lắp hoặc kiểm chứng Fusion V6. Xem ảnh
`floor_detail.png` (trên), `underside_detail.png` (dưới), `floor_joint_section.png`
(mặt cắt qua đầu T) và `floor_joint_exploded.png` (vị trí đưa khóa từ dưới).

## Slice offline — 2026-10-13

Đã chạy Bambu Studio 02.08.02.61 bằng CLI cho coupon và khóa, giữ hướng STL, support
tắt. Fixture từ profile bundled Prusa MK3S nozzle 0,4 mm, lớp 0,20 mm, Generic PLA,
bàn 250 ×210 mm; đây không phải profile máy in đã xác nhận của người dùng.

- Cả hai lệnh exit 0, 3MF có G-code và cấu hình `enable_support=0`, metadata
  `support_used=false`; không có feature/path support trong G-code.
- Khóa nhỏ không có warning, nhưng vẫn có đường bridge trong toolpath.
- **Coupon có cảnh báo floating cantilever**. Slice thành công khi tắt support
  không chứng minh mẫu sẽ in tốt; chưa chốt coupon hoặc cả thùng là không cần support.
  Cần xem preview và in coupon trước, kiểm tra bridge võng/độ khít, rồi mới quyết
  định có support cục bộ hoặc phải sửa hình học.

Tóm tắt được kiểm tra độc lập nằm ở `exports/v6/slice-audit.json` (hash artifact,
hash STL tại lúc kiểm tra, warning và kiểm tra support). Cấu hình fixture, lệnh
đầy đủ, kết quả thô và 3MF/G-code giữ local tại `work/v6-slice/`; không gửi máy in.
Các 3MF này là dữ liệu kiểm chứng profile mẫu, không phải file in đã chốt cho máy thật.
Lệnh CLI đối chiếu [tài liệu chính thức Bambu Studio](https://github.com/bambulab/BambuStudio/wiki/Command-Line-Usage).

## Tài liệu tham khảo

Xem [chỉ mục tài liệu FDM](docs/REFERENCES.md). PDF hãng và ghi chú đã lưu offline
trong thư viện chung `H:\OpenSCAD\docs\references\`; không đăng lại PDF hãng vào repo.
