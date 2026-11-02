# Milestones — bản chi tiết đã duyệt

Trạng thái: **HUMAN APPROVED 2026-11-02**, khớp [Plan](./IMPLEMENTATION_PLAN.md) và [Technical Proposal](./TECHNICAL_PROPOSAL.md). Milestones chỉ sắp xếp deliverable từ Plan; M1/M3 là bước trung gian, không thay các kết quả sản phẩm G-01/G-08. Thứ tự không phải ước tính ngày hoặc tự động cấp quyền thực thi.

## M1 — Bước chuyển tiếp: Concept cũ được gỡ, trang tạm minh bạch (G-06)

**Đã thực hiện / bằng chứng:** TASK-06 và TASK-07; xem [bằng chứng UI](./reports/task-06-evidence.md) và [bằng chứng cleanup](./reports/task-07-evidence.md). 26 kiểm tra backend sau cleanup, build và test Chrome đã đạt; đọc bản sao 3 project, 4 job Batch, 6 revision records và project gốc không đổi. Đây không phải inference thật mới. Task-07 đang ACTIVE trong harness cho kiểm tra bàn giao.

**Không gồm:** engine render, clipboard, plugin, workflow Concept mới. M1 không chứng minh G-08 đã hoàn thành. Dữ liệu cũ vẫn trên đĩa; job Concept cũ không còn hiện qua Batch.

## M2 — GOAL: Batch dùng project theo tên, dữ liệu cũ nguyên vẹn (G-05, G-01)

**Kết quả:** tạo project mới có tên hoặc chọn project cũ theo tên; ID là nội bộ, output vẫn ở mặc định. Batch, gallery và revision hoạt động theo project đã chọn, kể cả hai project trùng tên hiển thị phân biệt được. Batch mới có asset trùng tên trong cùng project báo trùng và yêu cầu đổi tên; tạo lại asset cũ là thao tác riêng và giữ revision trước.

**Minh chứng:** test danh sách/tạo/chọn, reload và lỗi, hai project trùng tên, dữ liệu cũ trên bản sao, trùng asset/ID, lỗi ghi, retry khi lưu/queue hoặc response lỗi, job đang chạy khi đổi project và Batch end-to-end với adapter kiểm thử; build và browser. Model thật cần được chạy trên host có runtime; nếu không có, ghi UNVERIFIED. Không migrate/xóa ảnh.

## M3 — Bước kiểm chứng: Thiết kế và thử ranh giới plugin (G-07)

**Kết quả:** tài liệu chi tiết input/output, ai xử lý gì, đường dẫn, phiên bản, render, lỗi và quyền; xác định plugin/tunnel thực tế. Chạy spike một asset qua ChatGPT Web: ghi vào vùng thử, kích hoạt model local, quan sát kết quả hoặc lỗi và giới hạn. Nhận diện rõ việc Human duyệt phân tích và các thao tác thuộc quyền ChatGPT/Web; không coi prompt là cơ chế cưỡng chế.

**Điểm quyết định:** spike không thay cho minh chứng workflow Concept đầy đủ. Nếu bridge không được chứng minh, chưa cam kết thực thi M4; báo kết quả cho Human. Không tự thay bằng thao tác thủ công rồi tuyên bố đạt.

## M4 — GOAL: Tạo, render và tinh chỉnh concept (G-08, có điều kiện)

Sau thiết kế và tính khả thi đã được quyết định: concept thật → phân tích/duyệt → HTML và prompt → batch ảnh local vào đường dẫn HTML → render → click chọn phần tử → copy ID và ảnh → feedback → sửa đúng prompt qua plugin và gen lại → khôi phục được ảnh cũ. Kiểm chứng lỗi và bảo toàn phiên bản; không hứa khớp concept chính xác.

Lịch sử: [milestones cũ](./archive/milestones-2026-10-22.md).
