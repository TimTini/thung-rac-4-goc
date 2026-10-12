# V3 — nối hoàn toàn bằng chi tiết in

**Đã phát hiện lỗi đường lắp chốt:** đường đưa chốt tiếp tuyến bị gân dọc chắn; kiểm tra vị trí cuối trước đây không phát hiện. Xem `exports/v3/pin-path-failure.json`, chuyển sang V4/README-v4. Giữ V3 để tái hiện, không dùng làm mẫu lắp đã được xác nhận.

Mở `thung-rac-4-goc-v3.scad`. Bản này không có bulông, ê-cu, vít tự ren hoặc keo. V1/V2 được giữ riêng để tham khảo, không dùng STL cũ để lắp V3.

## Cấu tạo

- Bốn góc chữ L giống nhau, xoay 0/90/180/270 độ khi lắp. Giữ gân dọc và đai giữa thân. Mỗi đường ghép có hai nửa rãnh khóa hình nơ/đuôi én đôi.
- Bốn khóa trượt nhựa dài luồn từ trên xuống. Hai đầu rộng của tiết diện giữ hai nửa rãnh chống tách; vai ở đầu khóa và đáy rãnh giới hạn chiều trượt.
- Bốn chốt nêm nhựa luồn ngang gần miệng, xuyên hai nửa ray và khóa, chặn khóa bị nhấc lên. Chốt chỉ giữ khóa theo chiều đứng; không thay khóa dài để chịu lực kéo tách thành.
- Đáy mỗi góc có mép chồng thấp và mép nhận cao. Gân đáy cao 8 mm tích hợp ở mặt trong. Khung/nẹp đáy dùng vít của V2 đã bỏ; mặt dưới thân vẫn phẳng. Gân trong đáy có thể giữ bụi/cọ túi, không phải lòng thùng trơn hoàn toàn.

## File cần in

Tất cả STL ở `exports/v3/`, đã đặt mặt in tại Z=0.

| File | Số bản | Kích thước bao mặc định (mm) |
|---|---:|---|
| `corner.stl` | 4 | 204 × 195,8 × 240 |
| `key.stl` | 4 | 236 × 12 × 32, đặt khóa nằm ngang |
| `pin.stl` | 4 | 51 × 8 × 4, đặt nằm phẳng |

Tổng 12 chi tiết in. Thân danh nghĩa 360 × 360 × 240 mm; kể cả ray và đầu khóa: 392 × 392 × 244 mm. Khổ in thật chưa được cung cấp; audit chỉ đối chiếu bounding box từng chi tiết với khối 256 mm giả định, không xác nhận bàn in hoặc G-code.

Các `view`: `assembled`, `exploded`, `corner`, `key`, `pin`, `coupon`, `coupon_key`, `coupon_pin`. F5 xem nhanh, F6 render rồi Export STL. Không có chế độ frame/bridge/base bắt vít trong V3.

## In thử mối nối trước

1. In `coupon.stl`: tách thành hai object trong slicer, giữ đứng như hai nửa ray thật. In thêm một `coupon_key.stl` và một `coupon_pin.stl` theo hướng đã xuất.
2. Ghép hai nửa coupon, luồn khóa ngắn từ trên xuống đến vai tựa, sau đó đưa chốt nêm ngang qua lỗ. Thử kéo hai nửa tách nhau, thử nhấc khóa, rút chốt rồi tháo khóa.
3. `key_clearance=0.25` mm **mỗi mặt** (offset pháp tuyến tiết diện); `floor_clearance=0.3` mm **tổng** khe giữa hai mặt bậc đáy. Chỉnh sau khi thử, không ép khóa kẹt.
4. `pin_interference=0.1` mm là phần chiều rộng nêm lớn hơn lỗ tại đầu vào, **tổng chiều rộng**, tức khoảng 0,05 mm mỗi phía. Đây là ép nhẹ có chủ đích. Nếu khó vào, giảm giá trị và xuất lại cả bộ liên quan; không đóng búa. Độ giữ do ma sát/ép, chưa có ngàm đàn hồi chống tuột. Có thể phải chỉnh dung sai để chốt không quá lỏng sau dùng lâu.

Coupon dùng đúng tiết diện khóa/ray và lỗ chốt, chỉ rút ngắn chiều đứng còn 42 mm. Nó không kiểm chứng độ thẳng/co ngót của ray dài 240 mm, độ chịu tải của đáy hoặc mộng đáy đầy đủ. Cần tiếp tục thử ray dài trước khi in đủ thùng nếu coupon vừa nhưng khóa dài kẹt.

## Lắp và tháo

1. Đặt các góc trên mặt phẳng cùng cao độ. Ghép mép thấp vào bậc nhận, đưa góc cuối theo đường chéo **nằm ngang** vào giữa hai góc bên cạnh. Không hạ góc cuối từ trên xuống như V2 vì có bậc đáy đối chiều.
2. Khi đủ bốn góc, chỉnh các ray thẳng hàng rồi luồn từng khóa dài từ trên xuống. Cần khoảng trống phía trên thùng để đưa khóa dài vào.
3. Luồn bốn chốt nêm từ phía có đầu chốt trong ảnh, siết bằng tay đến khi vừa giữ. Đầu lớn nằm ngoài ray để cầm rút. Thử nhẹ xem khóa còn nhấc được không.
4. Tháo theo thứ tự chốt → khóa → góc thân. Nếu chốt chặt, đẩy từ đầu nhỏ; không cạy bẻ thành mỏng.

## In và giới hạn

PETG dự kiến, cần xác nhận bằng coupon. Góc thân đáy xuống bàn; khóa dài nằm ngang như STL để đường sợi chạy dọc khóa. Kiểm tra support cục bộ tại bậc nhận dưới đáy (phần nhô khoảng 8 mm), vành miệng và lỗ chốt ngang. Chưa chạy slicer hoặc in thực. Không khẳng định in toàn bộ không support.

Ray và khóa dài có thể kẹt do cong/co ngót hoặc elephant foot. Nêm ma sát có thể lỏng theo thời gian; khả năng chịu va đập, xách thùng đầy và tháo/lắp nhiều lần chưa được kiểm chứng. Không kín nước, dùng túi lót. Đây là mẫu CAD thử, chưa có tải cho phép theo kg.

## Kiểm chứng đã chạy

`build-v3.py` dùng OpenSCAD Manifold và trimesh/manifold3d hiện có. Các STL kín, mỗi chi tiết một component (coupon hai). 28 cặp thân/khóa không giao thể tích. Kiểm tra lấy mẫu góc cuối tiến chéo XY tại 0,5/2/5/10/20/40 mm và khóa tiến Z tại 1/8/30/120/245 mm không vướng; chưa mô phỏng đường liên tục hoặc thao tác tay.

Khóa dịch 1 mm theo bốn hướng XY bị rãnh chặn; khóa nhấc 1 mm bị chốt chặn trong mô hình. Coupon cũng kiểm tra khóa không lấn ray, chốt lọt qua khóa và chặn nhấc. Nêm có giao thể tích có chủ đích khoảng 0,799 mm³ với một nửa ray tại mỗi seam; audit tách riêng phần này, không gọi toàn cụm là không giao thể tích. Phép kiểm tra CAD không xác nhận ma sát, độ đàn hồi hoặc độ bền thực.

Script bỏ tam giác diện tích 0 khi xuất STL rồi nạp lại kiểm tra kín; không vá lỗ. Runtime trimesh có thể cảnh báo mass-properties ở mặt tiếp xúc không có thể tích; OpenSCAD render không warning/error. Log và báo cáo ở `exports/v3/` và `exports/v3-build.log`.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:OPENSCAD = (Get-Command openscad).Source
python build-v3.py
```

Script đọc các tham số số chính và dùng các hằng hình học chung với SCAD (tiết diện khóa, chiều cao coupon 42, lỗ cách đỉnh 12). Các thay đổi contract hình học đi cùng cập nhật script. Source và công cụ được quản lý trong repo; checkpoint local nằm ngoài bộ file phát hành.
