> HISTORICAL / SUPERSEDED: this document describes the old concept workflow and is not an instruction for current work. See docs/IMPLEMENTATION_PLAN.md and docs/HANDOFF_QWEN.md (relative to project root).

# Concept Extractor — yêu cầu sản phẩm

Nguồn yêu cầu được rút từ kế hoạch AssetGen ngày 29/09/2026. `EXECUTION_PLAN.md` là danh sách việc để Qwen thực hiện và nghiệm thu. Nếu hai tài liệu khác nhau, ưu tiên yêu cầu người dùng mới nhất.

## Luồng chính

1. Import một ảnh concept vào project, đặt nhiều vùng chọn rectangle, square hoặc circle trên ảnh gốc. Có chọn, di chuyển, đổi kích thước, duplicate, xóa, undo/redo, zoom và pan. Frame giữ tọa độ theo pixel ảnh gốc.
2. Kiểm tra từng frame trên canvas chỉ hiển thị frame đang chọn. Xem crop dự kiến, đặt tên, kích thước đích, Fit/Fill, PNG/WebP/JPEG, mức nén, `max_kb`, màu nền và prompt tùy chọn. Mask Brush/Eraser riêng cho từng frame, lưu và mở lại được.
3. Xuất crop cơ bản theo từng frame qua queue; Gallery hiển thị trạng thái, lỗi, preview, retry, lịch sử revision và thư mục ảnh. Prompt regeneration và inpaint chỉ được bật sau khi model thật vượt qua kiểm tra bằng ảnh before/after.

## Quy tắc dữ liệu và output

- Project, source, frame, mask, selected revision và bước hiện tại phải còn đúng sau khi tắt/mở app. Source và revision bất biến. ID frame ổn định qua rename; duplicate có ID và tên mới. Sửa frame sau khi xuất thì giữ revision cũ và đánh dấu cần xuất lại.
- Source nằm trong `projects/<project-id>/source/`; mask một kênh trong `projects/<project-id>/masks/` với 0 = giữ, 255 = xóa/tái tạo; revision trong `projects/<project-id>/revisions/<frame-id>/`. Đường dẫn metadata là relative và được kiểm tra trong project root.
- Thư mục `outputs/<project-id>/concept/` chỉ chứa ảnh người dùng, tên file lấy từ tên frame đã chuẩn hóa. Không có JSON, manifest, mask hoặc file tạm. Batch tiếp tục ở `outputs/<project-id>/`. Publish file thành công bằng temp + rename; lỗi không thay ảnh đang dùng.
- Crop cơ bản không cần AI. Circle có alpha trong PNG/WebP; JPEG được flatten bằng màu nền. Output đúng kích thước đích, format, Fit/Fill, mức nén và `max_kb` hoặc báo rõ khi giới hạn không đạt. Không chấp nhận JPEG + lossless.
- Mask yêu cầu AI inpaint. Khi capability chưa PASS, không được báo mask đã xử lý; người dùng phải chọn rõ bỏ mask hoặc xuất crop gốc. Regeneration phải image-conditioned từ crop/revision đang chọn, không thay bằng text-to-image thuần.
- API trả lỗi có `code`, `message`, `details`; ID không tồn tại 404, input sai 422, job đang chạy 409, AI chưa xác nhận 501. UI có loading, empty, error và retry; không dùng alert/console/placeholder như dấu hiệu thành công.

## Tiêu chí cuối

- Một concept có ít nhất 4 frame, gồm rectangle, square, circle và một bản duplicate cùng kích thước ở vị trí khác, đi hết ba bước; kiểm tra đúng số file, tên, pixel dimensions, format và alpha.
- Reload ở từng bước khôi phục đúng source, frame, mask, cấu hình, revision và bước. Một frame lỗi không chặn các frame khác. Retry không xóa ảnh/revision cũ.
- Batch và dữ liệu sẵn có trong `projects/`, `outputs/` vẫn dùng được. Backend tests, frontend build và thao tác UI trên `http://127.0.0.1:5173/` có bằng chứng.
