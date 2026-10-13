# Thùng rác 4 góc — mẫu CAD thử

**Bản thử gọn hiện tại:** mở [`thung-rac-4-goc-v6.scad`](thung-rac-4-goc-v6.scad); xem [`README-v6.md`](README-v6.md). V6 dùng khóa cầu chìm dưới đáy, tăng dày cục bộ và gân/bo đáy–thành, tổng 16 chi tiết in không vít/ê-cu/keo; STL/ảnh/audit ở `exports/v6/`. Ngàm đàn hồi mới cần thử coupon, chưa xác nhận lực bấm hoặc chịu tải. Script Fusion hiện vẫn là V4. V5/V4 được giữ để đối chiếu. Tài liệu FDM lưu theo [chỉ mục tham khảo](docs/REFERENCES.md). V3 có lỗi đường đưa chốt ngang bị gân chắn; giữ lại cùng bằng chứng tái hiện, không dùng V3 để in đủ thùng. Các phần dưới mô tả V2/V1 dùng vít, giữ để tham khảo.

## Bản V2 gia cường

Mở **`thung-rac-4-goc-v2.scad`**. V1 và exports gốc được giữ nguyên; STL/ảnh/audit V2 nằm trong **`exports/v2/`**.

- Mỗi nửa mặt có 2 gân ngoài, tổng 4 gân trên mỗi mặt hoàn chỉnh. Gân thân dày 3 mm, nhô 10 mm, chân mở rộng và profile bo R1,5; chạy từ đáy tới miệng.
- Đai ngang cao 24 mm, nhô 8 mm, ôm cả góc bo; mặt dưới vát khoảng 45°. Mỗi đường ghép dùng một nẹp rời 48 × 24 × 4 mm, 2 vít M4. Đai không còn phụ thuộc riêng vào thành mỏng tại đường chia.
- Khung dưới đáy gồm 4 phần lưới giống nhau, cao 14 mm. Các thanh đỡ đáy và có mặt dưới đồng phẳng để đặt sàn. Mỗi khung gắn vào góc thùng bằng 6 vít; 3 vít gần tâm xuyên cả nẹp chữ thập phía trong.
- Thành/đáy giữ 3,2/4 mm. Bên trong thành vẫn phẳng, nhưng nẹp và phần cứng đáy còn nhô. Chưa có tay cầm hoặc nắp. Vành miệng giữ kiểu V1, được gân dọc nối vào; chưa đổi thành vành chữ U.

| Chi tiết V2 | Số bản cần in | Kích thước bao mặc định (mm) |
|---|---:|---|
| `corner.stl` | 4 | 210 × 189,8 × 240 |
| `frame.stl` | 4 | 164 × 164 × 14 |
| `bridge.stl` | 4 | 48 × 24 × 4 |
| `base.stl` | 1 | 160 × 160 × 6 |
| `coupon.stl` | thử trước, không tính vào cụm | 2 đoạn mộng của V1; chưa kiểm thử đai |

Tổng cụm 13 chi tiết in, kích thước bao 384 × 384 × 254 mm, tính cả nẹp đai và khung đáy. Khổ in thật chưa được cung cấp; từng chi tiết chỉ được so kích thước bao với khối 256 mm giả định.

**Thứ tự lắp:** ghép bốn góc trước, để góc cuối hạ từ trên xuống khi các vít còn lỏng. Lắp nẹp đai sau; đặt khung dưới từng phần đáy và nẹp chữ thập trong thùng; luồn vít từ dưới lên, sau đó siết đều. Không lắp nẹp đai trước khi đưa góc cuối vào vì có thể chặn đường lắp.

**Phần cứng dự kiến, tổng 40 bộ M4:** 8 vít trên/dưới các đường ghép đứng (M4×20); 8 vít giữa thân xuyên đai/nẹp (M4×30); 12 vít gần tâm xuyên khung–đáy–nẹp (M4×30); 12 vít ngoài xuyên khung–đáy (M4×25). Các chiều dài này phải đối chiếu đầu vít, vòng đệm và ê-cu thực tế, tránh đuôi vít quá dài phía túi. Khung có hốc đầu vít Ø8,5 sâu 4 mm phía dưới; không đặt vòng đệm lớn hơn hốc vào đó, chưa có hốc giữ ê-cu. Không siết quá mức ép hỏng nhựa.

**In:** góc thùng đáy phẳng xuống bàn; khung đặt mặt có hốc đầu vít xuống bàn; nẹp đai nằm phẳng. Xem slicer tại vành miệng, lỗ ngang và phần đóng trên hốc vít khung; chưa xác nhận support hoặc G-code. Gân/đai làm tăng vùng chiếm chỗ và thời gian in. Thể tích hình học toàn V2 khoảng 3,066 lít nhựa đặc so với 1,988 lít V1, tăng khoảng 54%; đây không phải lượng filament sau slicing và không chứng minh tăng độ bền tương ứng.

**Kiểm chứng V2:** build Manifold không warning/error; STL từng loại kín và một component, coupon hai component; 78 cặp trong 13 chi tiết không giao thể tích; 8 đường lỗ mẫu (2 trên đai + 6 dưới một góc, đối xứng quay cho các góc khác) thông suốt. Kiểm tra hạ góc cuối chỉ lấy mẫu 5 độ cao, chưa phải mô phỏng chuyển động liên tục hoặc thao tác tay/cờ lê. Không thử tải/in thực và không kín nước.

Chạy lại bằng runtime hiện có:

```powershell
python build-v2.py
```

Script V2 đọc các tham số số chính từ source để dựng lại vị trí audit. `frame_start=10`, mẫu lỗ gần tâm `[20,20]/[60,20]/[20,60]` và góc vuông vẫn là contract của mẫu, không phải script tổng quát cho mọi layout. Khi đổi layout cần đồng bộ audit. Kết quả chỉ có giá trị cho cấu hình vừa build.

---

Phần bên dưới mô tả **V1**.

Mở `thung-rac-4-goc.scad` bằng OpenSCAD. Đây là mẫu kết cấu để xem/thử ghép, chưa thử tải thực tế hoặc xác nhận kín nước.

## Kích thước mặc định

- Thân vuông 360 × 360 × 240 mm; kể cả vành miệng: 368 × 368 × 240 mm.
- Thành 3,2 mm, đáy 4 mm, góc bo R18; vùng mép ghép dày tổng 8 mm.
- Bốn góc giống hệt nhau: mỗi góc khoảng 204 × 183,8 × 240 mm (bao gồm mộng và vành). Khổ in 256 mm mỗi chiều chỉ là giả định kiểm tra, chưa biết máy thực tế.
- Một nẹp chữ thập đặt trên mặt trong đáy: 160 × 160 × 6 mm.
- Khe giữa các phần 0,4 mm, khe giữa hai mặt mộng 0,4 mm. In coupon để chỉnh theo máy/nhựa.

## Xem và xuất

Chỉnh `view` đầu file, F5 để xem nhanh, F6 để render, sau đó Export STL:

| view | Nội dung |
|---|---|
| `assembled` | Lắp hoàn chỉnh, màu phân biệt bốn góc |
| `exploded` | Các góc tách ra để xem mép ghép và nẹp đáy |
| `corner` | Một góc đặt đáy phẳng ở Z=0; in 4 bản |
| `base` | Nẹp đáy đặt ở Z=0; in 1 bản |
| `coupon` | Hai đoạn mộng ghép cao 30 mm; tách thành hai object trong slicer rồi đặt từng phần lên bàn |

STL đã xuất nằm trong `exports/`: `corner.stl`, `base.stl`, `coupon.stl`. Không dùng `assembly.off` để in nguyên thùng: file đó là union phục vụ audit, không giữ object riêng.

## Mối nối và lắp ráp

1. In/thử `coupon.stl` trước. Hai mép chồng theo bậc, dùng vít xuyên để giữ; không phải ngàm bấm hoặc khóa đuôi én.
2. In 4 bản `corner.stl`, xoay lần lượt 0°, 90°, 180°, 270° khi lắp. Mỗi góc có một mép đưa ra và một mép nhận.
3. Lắp lỏng ba góc; hạ góc cuối từ trên xuống theo phương Z để hai mép vào đúng bậc. Chưa siết vít trước khi đủ bốn góc.
4. Dùng 3 vít M4 tại mỗi đường nối đứng: tổng 12 vít. Lỗ danh nghĩa Ø4,5 mm; dùng vòng đệm hai phía và ê-cu. M4×20 là chiều dài dự kiến, cần đối chiếu vòng đệm/ê-cu thực tế. Giữ ê-cu bằng cờ lê: bản thử chưa có hốc giữ ê-cu hoặc hốc chìm đầu vít.
5. Đặt nẹp chữ thập vào trong đáy; bắt thêm 12 vít M4 xuyên đáy/nẹp, mỗi góc 3 vít. Nên dùng đầu tròn thấp phía trong; đầu vít/nẹp vẫn nhô và có thể cọ túi.
6. Siết vừa đủ áp mặt, không siết đến mức nhựa trắng/nứt. Kiểm tra lại sau sử dụng.

Đáy vẫn có đường ghép, cần túi lót. Nẹp giữ đáy và chống các góc tách nhau, không làm đáy kín nước. Chưa có tay cầm/nắp/gân chịu tải cho đáy lớn; không mặc định rằng có thể xách thùng đầy bằng vành miệng.

## In thử

PETG dự kiến. Đặt đáy xuống bàn, xem preview slicer cho vành miệng nhô 4 mm, lỗ vít ngang và cầu ngắn tại mép nhận sát đáy; có thể cần hỗ trợ cục bộ tùy máy. Chưa kiểm tra slicer/G-code, chưa in vật lý. Kiểm tra độ bám lớp và coupon trước khi in 4 góc.

## Build và kiểm chứng lại

Script dùng Python với `numpy`, `trimesh`, `manifold3d` và OpenSCAD có backend Manifold. Tạo môi trường Python trong thư mục dự án rồi cài dependency:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Trỏ `OPENSCAD` tới executable OpenSCAD. Khi lệnh `openscad` có trong `PATH`, dùng `$env:OPENSCAD = (Get-Command openscad).Source`; với bản portable, đặt biến này tới file `openscad.com` hoặc `openscad.exe`.

Chạy V1 từ thư mục dự án:

```powershell
python build.py
```

Build xuất STL, ảnh, log OpenSCAD và `exports/audit.json`. Audit kiểm tra mesh kín, số thành phần, bounds, giao thể tích giữa 5 chi tiết và 5 vị trí hạ góc cuối. STL qua bước bỏ tam giác diện tích bằng 0 do tessellation các mặt đồng phẳng; không vá lỗ. Union lắp hoàn chỉnh có 1 component do nẹp tiếp xúc đáy, còn các file in vẫn riêng biệt.

**Giới hạn script:** phép dựng lại vị trí để kiểm tra va chạm hiện dùng kích thước mặc định (`lap_length=20`, `base_span=160`, `floor_thickness=4`); nếu đổi các tham số này cần cập nhật phép dịch trong `build.py`. Khẳng định khổ in 256 mm cũng chỉ dành cho mẫu mặc định. Có thể có cảnh báo NumPy khi phân tích mặt tiếp xúc có thể tích bằng 0; không phải cảnh báo OpenSCAD.

## Autodesk Fusion V4

Bộ [script Fusion native parametric V4](fusion/README.md) dựng 4 góc, 4 khóa và 4 chốt; xem tài liệu về tham số, cách chạy và giới hạn kiểm chứng.

## Bộ tài liệu agent tự học.

[Cẩm nang dùng chung](https://github.com/TimTini/snaplock-storage-box/blob/main/docs/agent-learning.md) tổng hợp quy trình SCAD trước rồi Fusion Python sau. [Sổ lỗi và cách sửa](https://github.com/TimTini/snaplock-storage-box/blob/main/docs/error-cookbook.md) ghi các ca kỹ thuật cùng phạm vi kiểm chứng. [Mẫu giao việc](https://github.com/TimTini/snaplock-storage-box/blob/main/docs/scad-to-fusion-task.md) áp dụng quy trình cho model mới.
