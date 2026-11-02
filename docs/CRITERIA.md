# Tiêu chí sản phẩm — AssetGen

Trạng thái: APPROVED — Human đã phê duyệt thay đổi sau khi nhận tư vấn Technical Advisor.

## Mục đích và người dùng
AssetGen giúp tôi tạo hình ảnh cho các ứng dụng của mình và tái hiện concept bằng các asset mới. Sản phẩm dành cho một người dùng trên một máy, dùng cho mục đích cá nhân, không bán và không cần cộng tác.

## Tạo ảnh hàng loạt
Tiếp tục hỗ trợ tạo ảnh batch từ prompt bằng model chạy cục bộ; hành vi Batch và dữ liệu cục bộ hiện có tiếp tục dùng được.

## Tái hiện và chỉnh sửa concept
- Tôi paste ảnh concept vào ChatGPT Web. ChatGPT phân tích concept và trình bày kết quả để tôi duyệt trước khi tiếp tục.
- Sau khi tôi duyệt, ChatGPT sử dụng plugin kết nối qua tunnel tới máy của tôi để viết HTML và prompt chi tiết cho từng asset, đồng thời yêu cầu model local tạo ảnh hàng loạt. HTML xác định tên và vị trí các asset; ảnh được tạo và đặt đúng vị trí để render concept.
- Khi một phần tử chưa đạt, tôi có thể copy ID và ảnh hiện tại của phần tử, paste vào cuộc trò chuyện ChatGPT cùng nhận xét. ChatGPT nhìn ảnh và nhận xét, sửa prompt qua plugin và yêu cầu model local tạo lại asset tương ứng.
- Giữ lại các ảnh đã tạo. Ảnh được chọn được copy vào đúng vị trí HTML sử dụng để cập nhật bản render; có thể chọn lại ảnh cũ.
- Báo rõ lỗi, không báo thành công khi thao tác thất bại và không làm mất ảnh đã tạo khi tạo lại hoặc thay ảnh đang dùng.

## Phạm vi và giới hạn
Tạo ảnh chạy bằng model cục bộ. Bước phân tích concept và viết prompt, HTML sử dụng ChatGPT Web; ảnh concept và nội dung tôi đưa vào cuộc trò chuyện được gửi tới ChatGPT. Plugin là cầu nối để ChatGPT làm việc với file và tác vụ trên máy; phạm vi truy cập cần phù hợp với công việc. Không cần người dùng từ xa, cộng tác nhiều người, bán hoặc phát hành thương mại, hay bảo mật và quản trị cấp doanh nghiệp.

Workflow concept cũ dựa trên frame, crop và mask được thay thế hoàn toàn; không yêu cầu duy trì các thao tác đó trong workflow mới.

## Minh chứng thành công
- Batch từ prompt tiếp tục tạo ảnh bằng model local.
- Với một concept thực tế, tôi duyệt phân tích trong ChatGPT, sau đó nhận được bản HTML render từ các asset do model local tạo và đặt đúng vị trí.
- Tôi copy ID và ảnh của một phần tử, đưa vào ChatGPT cùng nhận xét, rồi tạo lại đúng asset. Bản render hiển thị ảnh được chọn, và tôi có thể chọn lại ảnh cũ đã giữ.
- Khi một bước thất bại, ứng dụng báo rõ và các ảnh đã tạo trước đó vẫn còn.

## OPEN — chưa xác minh về mặt kỹ thuật
- Cầu nối ChatGPT Web → plugin/tunnel → máy local, bao gồm ghi file, kích hoạt model và báo kết quả hoặc lỗi, chưa được xác minh cho workflow này.
- Việc copy ID cùng ảnh, liên kết đúng phần tử với asset, tạo lại và chọn phiên bản cũ cần được kiểm chứng trong một luồng thực tế.
- Chất lượng phân tích và mức độ giống concept phụ thuộc vào ChatGPT và model ảnh; chưa có cam kết tái hiện chính xác.

## Lịch sử phê duyệt
- 2026-10-22: Human phê duyệt phiên bản đầu sau khi nhận tư vấn Technical Advisor.
- 2026-10-29: Human đồng ý thay workflow concept và giữ Batch sau khi nhận tư vấn Technical Advisor.

## Ranh giới bàn giao
CRITERIA định nghĩa sản phẩm cần làm gì. GOALMAP và các mục tiêu triển khai thuộc `docs/IMPLEMENTATION_PLAN.md`; các kế hoạch, milestone và task cần được đánh giá lại theo Criteria này trước khi triển khai.
