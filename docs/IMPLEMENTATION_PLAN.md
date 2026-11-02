# Implementation Plan — bản chi tiết đã duyệt

Trạng thái: **HUMAN APPROVED 2026-11-02** — Human duyệt bản cập nhật sau khi đối chiếu Criteria và Reviewer rà phạm vi. Hướng Batch/Concept và các lựa chọn project đã được Human xác nhận. [CRITERIA](./CRITERIA.md) là nguồn WHAT/WHY duy nhất. Bản Criteria trong source khi đối chiếu có Git blob SHA `d102ec550d8255720a8a8d4ef64efa9f80cdfa63`; SHA chỉ nhận diện nội dung đã đọc, không phải phê duyệt hay bằng chứng GSA đã liên kết. Đọc lại bản thực tế trước review. Lập/duyệt task theo quy trình dự án trước khi code.

## GOALMAP

G-01 và G-08 là kết quả sản phẩm trực tiếp; G-05 diễn giải lựa chọn thao tác project mà Human đã chốt cho Batch. G-06 là kết quả chuyển tiếp đã thực hiện và G-07 là bước kiểm chứng khả thi phục vụ G-08: không nhầm placeholder hay spike với việc hoàn thành sản phẩm Concept.

| Goal | Kết quả quan sát được | Criteria | Thứ tự / trạng thái |
|---|---|---|---|
| G-06 | Concept cũ đã được gỡ; tab Concept là trang tạm không giả vờ có engine. | [Concept](./CRITERIA.md#tái-hiện-và-chỉnh-sửa-concept) | Đã thực hiện; TASK-06/07 có bằng chứng, chưa xác nhận model thật lần mới |
| G-01 | Batch và dữ liệu project/ảnh/revision hiện có tiếp tục dùng được. | [Batch](./CRITERIA.md#tạo-ảnh-hàng-loạt) | Xuyên suốt; kiểm tra lại mỗi lần thay đổi liên quan |
| G-05 | Tôi đặt tên project mới hoặc chọn project cũ theo tên để gen Batch, không phải nhập ID. | [Batch](./CRITERIA.md#tạo-ảnh-hàng-loạt) | Tiếp theo; chưa triển khai |
| G-07 | Có thiết kế chi tiết và kết quả thử thực tế cho ranh giới ChatGPT Web–plugin–máy local. | [Concept](./CRITERIA.md#tái-hiện-và-chỉnh-sửa-concept), [OPEN](./CRITERIA.md#open--chưa-xác-minh-về-mặt-kỹ-thuật) | Sau G-05; cầu nối chưa xác minh |
| G-08 | Sau khi có bằng chứng cầu nối và thiết kế được duyệt, tôi có thể tạo, xem và chỉnh asset concept, giữ ảnh cũ. | [Concept](./CRITERIA.md#tái-hiện-và-chỉnh-sửa-concept) | Sau G-07; điều kiện, chưa triển khai |

## GOAL G-06 — Trang Concept tạm và loại bỏ workflow cũ

TASK-06 đã thay giao diện bằng trang tạm; TASK-07 đã gỡ các route và xử lý chỉ thuộc Concept cũ. Dữ liệu cũ không bị xóa; job Concept cũ được bỏ qua khi đọc Batch và được bảo vệ khỏi va chạm ID. Xem [TASK-06](./reports/task-06-evidence.md) và [TASK-07](./reports/task-07-evidence.md). Các test tại thời điểm đó không chứng minh một lượt inference thật mới. Chưa có HTML engine, clipboard hay plugin.

## GOAL G-01 — Tôi tiếp tục tạo ảnh Batch local và dùng được dữ liệu đã có

**Nguồn:** [Tạo ảnh hàng loạt](./CRITERIA.md#tạo-ảnh-hàng-loạt) và [phạm vi, giới hạn](./CRITERIA.md#phạm-vi-và-giới-hạn). Nhập prompt và gen ảnh hàng loạt bằng model chạy local; project, ảnh và revision Batch đã có tiếp tục dùng được. Không làm mất hay xóa dữ liệu cũ trong khi sửa; thay đổi dữ liệu do người dùng chủ động yêu cầu vẫn được phép và phải giữ các ảnh/revision cần bảo toàn. Xác minh chức năng liên quan bằng dữ liệu cô lập/bản sao; inference model thật chỉ được coi là đã xác nhận nếu thực sự chạy trên host phù hợp. G-01 là ràng buộc xuyên suốt các bước sau, không đòi viết lại Batch.

## GOAL G-05 — Tạo hoặc chọn project bằng tên, giữ Batch (phụ thuộc G-01)

**Nguồn:** [Tạo ảnh hàng loạt](./CRITERIA.md#tạo-ảnh-hàng-loạt), cùng lựa chọn giao diện project do Human xác nhận sau đó (chi tiết triển khai, không tự sửa Criteria).

**Kết quả:** người dùng nhập tên để tạo project mới hoặc chọn một project đã có theo tên; ứng dụng tự dùng ID nội bộ và thư mục output mặc định. Cả khi trùng tên project, người dùng phải phân biệt được chúng mà không cần nhớ mã. Project đang chọn phải đúng cho nhập prompt, generate và gallery.

**Quyết định Human 2026-11-02:** batch mới gặp tên asset đã có trong cùng project thì báo trùng và yêu cầu đổi tên; tạo lại ảnh cũ là thao tác riêng, giữ revision trước.

**Phạm vi:** danh sách/đọc project cũ; tạo mới có tên; chọn và khôi phục lựa chọn; tiếp tục gen trong project đã chọn; xử lý lỗi và va chạm; bảo toàn job, revision và ảnh. Không thêm folder picker, di chuyển dữ liệu, cơ sở dữ liệu hay engine Concept.

**Chấp nhận:** dùng dữ liệu cách ly cho hai project, kể cả tên trùng; tạo mới, chọn lại project sau reload, nhập prompt và queue đúng project; gallery mở đúng ảnh/revision cũ; thử trùng tên asset, ID, lỗi ghi và retry sau lỗi lưu/queue hoặc mất response, project không còn tồn tại và chuyển project khi có job đang chạy; không báo thành công giả hoặc làm mất dữ liệu. Kiểm tra Batch bằng test backend, trình duyệt, build và một lượt model thật khi host/model sẵn có; tách rõ mock và bằng chứng inference thật. Hợp đồng và hướng dẫn giao việc từng lát cắt, file cần đọc, ca kiểm tra và điểm dừng ở Technical Proposal §3–6 và §9; hướng dẫn này không tự kích hoạt task.

## GOAL G-07 — Làm rõ và thử cầu nối Concept

**Nguồn:** [Concept](./CRITERIA.md#tái-hiện-và-chỉnh-sửa-concept) và [OPEN](./CRITERIA.md#open--chưa-xác-minh-về-mặt-kỹ-thuật). Đây là bước kiểm chứng phục vụ G-08, không phải một tính năng Concept hoàn chỉnh.

Sau G-05, xác định plugin/tunnel thực tế. Soạn thiết kế: input/output và trách nhiệm của ChatGPT, plugin, ứng dụng local và model; nhận duyệt phân tích; đặt tên asset/đường dẫn; render và lựa chọn phần tử; feedback, version, lỗi và quyền truy cập. Làm spike một asset qua **ChatGPT Web thực tế**, quan sát yêu cầu ghi file, kích hoạt model và báo kết quả/lỗi trong môi trường xác định. Trước spike mọi khả năng cầu nối là UNVERIFIED; một spike không chứng minh toàn workflow. Nếu thất bại hoặc không có quyền truy cập, báo bằng chứng và xin quyết định thay vì tự chuyển sang luồng thủ công.

## GOAL G-08 — Hoàn thành workflow Concept mới (điều kiện)

**Nguồn:** toàn bộ [Tái hiện và chỉnh sửa concept](./CRITERIA.md#tái-hiện-và-chỉnh-sửa-concept) và [Minh chứng thành công](./CRITERIA.md#minh-chứng-thành-công).

Chỉ lập các task triển khai sau khi thiết kế G-07 được thống nhất và có bằng chứng khả thi. Một concept thực tế phải đi qua: ChatGPT phân tích → Human duyệt → tạo HTML và prompt → local batch gen → ảnh nằm đúng đường dẫn HTML → render → click chọn phần tử → copy ID và ảnh → ChatGPT nhận feedback, cập nhật đúng prompt qua plugin → gen lại đúng asset → chọn và khôi phục ảnh cũ. Kiểm tra lỗi và sự bảo toàn ảnh ở mỗi lần thay; chất lượng và mức giống concept không được hứa trước.

## Giới hạn và bàn giao

Cá nhân, một máy; concept gửi tới ChatGPT Web. Không thêm cộng tác, thương mại, hạ tầng enterprise hoặc dependency chưa được phép. Model, runtime, project, output và dữ liệu người dùng không bị xóa/migrate vì dọn code. Workspace local hiện dùng Git và branch authority chọn `main` sau quyết định Human; xác minh lại policy thực tế ở mỗi clone, không suy từ tên branch hay bản sao file. GSA hiện chưa chấp nhận liên kết tới Criteria trong source: không tạo bản Criteria thứ hai hay giả PASS để qua kiểm tra; xử lý liên kết và đọc lại evidence trước khi tuyên bố Bootstrap READY. Harness chỉ hỗ trợ, không chứng minh hook hay phê duyệt được xác thực. Task-07 còn ACTIVE trong harness cho kiểm tra bàn giao; kiểm tra/đóng theo quy trình thực tế trước khi kích hoạt task khác. Lịch sử: [plan cũ](./archive/implementation-plan-2026-10-22.md).
