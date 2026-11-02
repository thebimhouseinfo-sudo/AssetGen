# Technical Proposal — Batch project và Concept workflow

Trạng thái: **HUMAN APPROVED 2026-11-02**. Đây là thiết kế đề xuất để GSA lập task, triển khai và review, không phải mô tả code đã hoạt động. Hướng sản phẩm duy nhất là [CRITERIA](./CRITERIA.md); thứ tự và acceptance thuộc [Plan](./IMPLEMENTATION_PLAN.md) và [Milestones](./MILESTONES.md). Human đã duyệt đề xuất ở mức tài liệu; mọi capability chưa kiểm chứng và các chi tiết phải chốt khi lập task vẫn cần bằng chứng và review phù hợp. Plugin cụ thể chưa được xác định, không giả định API của plugin tồn tại.

## 1. Bài toán, kết quả và ranh giới

AssetGen có hai phần: Batch prompt→ảnh local và Concept mới dùng ChatGPT Web. Phần Batch đang chạy và cần chỉnh **có chọn lọc**, không rewrite toàn bộ. Concept frame/crop/mask cũ đã gỡ; trang Concept hiện là placeholder. Phạm vi sắp triển khai là **chọn/tạo project theo tên cho Batch**; chưa làm HTML engine, plugin hoặc Concept mới trong bước này.

Một người dùng trên một máy. User không chọn thư mục mỗi lần gen: dùng `storage.output_root` đã cấu hình. Model và ảnh được tạo local; riêng concept được user paste vào ChatGPT Web. Không yêu cầu database server, dịch vụ remote mới, cộng tác, hay thiết kế enterprise.

## 2. Hiện trạng có bằng chứng và khoảng trống

| Thành phần | Hiện trạng source / bằng chứng | Khoảng trống |
|---|---|---|
| UI | `frontend/src/App.jsx` lưu `projectId` và tab trong localStorage; `BatchWorkspace.jsx` tự tạo project tên cố định và hiển thị ID; `BatchGallery.jsx` lấy status theo ID. | Chưa chọn project cũ theo tên, chưa nhập tên project mới. |
| Project | `backend/projects/models.py` có UUID `id`, `name`, `created_at`, `output_root`, `schema_version`; `ProjectManager` lưu `projects_root/<id>/project.json`. API đã có POST `/projects` và GET `/projects/{id}`. | Chưa thấy API liệt kê project. `output_root` trong project không phải nguồn tính đường publish hiện tại. |
| Batch | Upload parser tạo job; API lưu job JSON, queue in-process gọi adapter local, hậu xử lý, lưu revision rồi publish ảnh. | Lưu job có thể ghi đè job cùng ID; slug trùng bị từ chối nếu ID khác. Phải phân biệt tạo mới với sửa/regenerate. |
| Output | `image_folder_for` dùng `settings.storage.output_root/<project-id>`; `publish_image` ghi vào tên asset sau khi thay ký tự không hợp lệ và dùng replace; revision lưu trong `projects_root/<project-id>/revisions/<job-id>/`. | Asset tên khác nhau có thể đi tới cùng tên file sau chuẩn hóa hoặc theo filesystem; replace có thể ghi đè output. Chưa thể coi slug check là bảo vệ đầy đủ. |
| Restart / legacy | `recover_interrupted_jobs` đọc job khi khởi động; `load_jobs` bỏ qua job Concept cũ và `save_job` bảo vệ ID legacy. TASK-07 đã thử synthetic và bản sao 3 project/4 job/6 revision records. | Không giả định mọi dữ liệu lịch sử đều hợp lệ; không sửa file gốc hoặc âm thầm bỏ lỗi dữ liệu. |
| Concept / bridge | Chưa có renderer, clipboard hoặc plugin. | ChatGPT Web gọi plugin/tunnel, ghi file, gen và nhận kết quả là **UNVERIFIED**. |

Bằng chứng lịch sử: [TASK-06](./reports/task-06-evidence.md), [TASK-07](./reports/task-07-evidence.md). Test sau TASK-07 dùng adapter giả cho một số đường Batch; một lượt model local thật đã từng chạy ở M1, không phải lần xác nhận mới nhất.

## 3. Thiết kế đề xuất cho project Batch

**Nguyên tắc tỷ lệ:** ưu tiên thay đổi nhỏ trên Batch hiện có. Những ví dụ về API, khóa retry, quy tắc collision và test dưới đây là hướng dẫn xem xét rủi ro, không phải yêu cầu phải xây cơ chế tổng quát hoặc bảo đảm exactly-once qua restart. Chỉ chọn phần nhỏ nhất chứng minh được Batch làm việc đúng, báo lỗi trung thực và không làm mất ảnh/revision cũ. Nếu không có đủ bằng chứng crash/retry, báo giới hạn thay vì thêm hạ tầng hoặc tuyên bố đã bảo đảm.


### 3.1 Luồng người dùng

1. Vào Batch: hiển thị project đang chọn bằng **tên**, hoặc trạng thái chưa chọn. Nạp danh sách project thực có; phân biệt loading, rỗng và lỗi.
2. **Tạo mới:** nhập tên không rỗng → backend tạo UUID và project → chỉ chọn project đó sau khi server xác nhận. Hủy hoặc lỗi thì giữ lựa chọn và công việc hiện tại; không báo thành công. Không tự tạo tên cố định ngầm khi bấm Generate.
3. **Chọn cũ:** chọn từ danh sách. Cho phép trùng tên project, kèm thời gian tạo và chỉ dấu ổn định dễ phân biệt nếu thông tin hiển thị vẫn trùng. ID có thể là giá trị kỹ thuật nội bộ, không bắt user nhớ hoặc nhập. Nếu project đã bị xóa/không đọc được, báo rõ và yêu cầu chọn lại; không tự tạo project mới.
4. Nhập/dán prompt → xác nhận project đích rõ ràng → lưu job và queue → gallery theo cùng project. Khi đổi project, state preview/draft, lỗi và gallery phải được xử lý minh bạch để tránh gửi nhầm; không xóa job hay hủy công việc đã queue. Đề xuất khóa đích project tại lúc bấm Generate, ngăn chuyển hoặc xử lý rõ request đang chạy, tránh response cũ cập nhật nhầm project mới.
5. Khi reload, khôi phục project ID trong localStorage nếu server xác nhận còn tồn tại và đọc được; nếu không, báo và bỏ lựa chọn đó. Gallery và Batch dùng cùng nguồn trạng thái; stale response từ lần chọn cũ không được hiển thị thành project mới.

### 3.2 Backend/API đề xuất — chưa triển khai

- Giữ `POST /projects` cho tạo mới và `GET /projects/{id}` cho đọc. Validate tên sau trim; không dùng tên làm đường dẫn hoặc ID. Cho phép tên trùng và tạo UUID riêng. Không tự đổi schema của project cũ nếu không cần.
- Bổ sung một endpoint liệt kê project, ví dụ `GET /projects`, trả danh sách metadata tối thiểu (`id`, `name`, `created_at`), thứ tự ổn định. `id` chỉ là khóa kỹ thuật cho client. Đọc `project.json` dưới root đã cấu hình, không dựa vào tên thư mục tùy ý từ client. Contract chính xác và cách báo từng record hỏng là đề xuất để GSA chốt khi lập task.
- Một project metadata lỗi không được giả vờ danh sách đầy đủ hoặc ghi đè/xóa file hỏng. Đề xuất trả phần hợp lệ kèm cảnh báo có thể kiểm tra, hoặc báo lỗi rõ; tránh lộ nội dung file riêng tư. Thiết kế UI và test phải khớp cơ chế được chọn. Thư mục rỗng là trạng thái bình thường.
- Giữ các API Batch/Revision hiện có trừ thay đổi cần thiết để bảo vệ dữ liệu. ID project/job phải được validate ở backend; không dùng tên hiển thị để cấu thành path. Không thêm endpoint xóa project.

### 3.3 Tên asset, collision và revision

Hiện slug của parser và `image_filename` không phải cùng một phép chuẩn hóa. Một slug khác chưa đủ chứng minh filename khác trên hệ file; dấu câu, chữ hoa/thường và tên đã tồn tại có thể gây va chạm. Hơn nữa, một payload dùng lại ID job có thể thay metadata/selected revision trước khi gen. Những điều này cần test trước và sửa trong phạm vi bảo toàn Batch, không để project cũ mất dữ liệu.

**Quyết định Human 2026-11-02 — lựa chọn 1:** nhập batch mới chỉ tạo job mới; nếu asset name/đường publish xung đột trong project thì từ chối asset/batch có lỗi rõ, yêu cầu đổi tên. Chỉ hành động regenerate có chủ đích cho job hiện có được thay ảnh đang hiển thị; ảnh revision cũ vẫn giữ. Không tự suy ra ý định thay ảnh chỉ vì cùng tên hay cùng ID. Không ghi đè file lạ đã tồn tại; xác minh quyền sở hữu và tên đích trước publication. Các quy tắc filename/case cần thử trên filesystem đích; không khẳng định kiểm tra bằng lowercase giải quyết mọi trường hợp.

Lưu và queue hiện là hai request riêng: nếu job đã lưu nhưng queue lỗi hoặc response bị mất, bấm lại không được tạo bản sao, ghi đè metadata/revision hoặc bị kẹt vì chính ID của draft. **Đề xuất cần kiểm chứng:** phân biệt retry cùng yêu cầu chưa hoàn tất với tạo job mới bằng khóa yêu cầu/ID ổn định kèm nội dung tương ứng; lần gửi lại chỉ tiếp tục hoặc trả trạng thái các job đã lưu/queue, không reset job đang chạy hay đã hoàn tất. Nếu nội dung hoặc trạng thái không khớp, báo xung đột để user quyết định. Thiết kế phải bao phủ cả trường hợp response queue bị mất sau khi queue thành công, tránh gen hai lần trong các tình huống được kiểm chứng. Cơ chế cụ thể, phạm vi bảo đảm và khả năng phục hồi qua restart cần được chốt ở task theo mức cần thiết; không tuyên bố idempotency đã tồn tại hoặc exactly-once sau restart.

Luồng ghi cần giữ ảnh/revision cũ nếu lưu job, inference, postprocess, ghi revision hoặc publish lỗi. Tránh lưu payload mới đè selected revision/attempts của job cũ. Không báo một job queued nếu thực tế queue từ chối; không báo thành công trước khi có output. Việc đảm bảo an toàn qua crash và thứ tự ghi thực tế phải được kiểm tra với lỗi mô phỏng; không tuyên bố atomic toàn bộ pipeline chỉ vì một thao tác rename là atomic.

**Đã thống nhất:** asset trùng tên trong cùng project bị báo trùng và cần đổi tên; việc tạo lại asset cũ là thao tác riêng, giữ revision trước. Project trùng tên vẫn được phép và phải phân biệt được. Các chi tiết kỹ thuật chưa kiểm chứng vẫn cần evidence và task review trước triển khai.

## 4. Dữ liệu, tương thích và trách nhiệm

| Dữ liệu | Chủ sở hữu / đường hiện tại | Cách xử lý đề xuất |
|---|---|---|
| Project metadata | `projects_root/<id>/project.json` | Đọc tên/created_at hiện có; UUID ổn định; không rename/migrate vì chọn theo tên. |
| Batch jobs | `projects_root/<id>/jobs/*.json` | Chỉ ghi job mới hoặc cập nhật có chủ đích; bảo vệ legacy ID và metadata của job cũ. |
| Revision | `projects_root/<id>/revisions/<job-id>/` | Giữ JSON và ảnh cũ; chọn project khác không xóa hay sửa. |
| Ảnh đang publish | `output_root/<id>/<asset-name>.<ext>` | Vẫn output mặc định; không ghi đè file không thuộc thao tác regenerate có chủ đích. |
| Legacy Concept | File cũ trong project/output | Giữ nguyên bytes; không khôi phục API cũ, không nhầm thành Batch. |
| UI selection | `assetgen.ui-state` trong localStorage | Chỉ là lựa chọn tiện dụng, không phải nguồn xác thực project; xác nhận lại với backend khi khởi động. |

Kiểm thử trên bản sao hoặc temporary root bằng `ASSETGEN_SETTINGS`. Không thay settings thật, weights, binary, project, output. Recovery khi khởi động có thể cập nhật trạng thái job interrupted: thử trên **bản sao**, không kiểm tra recovery trên project thật.

## 5. Trạng thái và lỗi cần mô tả trong implementation

- Danh sách project: đang tải, không có project, lỗi backend và record hỏng phải phân biệt. Tạo tên rỗng/whitespace không tạo project; tên trùng không được âm thầm chọn nhầm.
- Sau khi chọn: UI hiển thị project đích trước khi gen; khi đổi project, gallery không hiển thị ảnh cũ dưới tên project mới. Đặc biệt kiểm tra request status/parse/generate trả về sau khi đã chuyển.
- Project bị xóa/thiếu quyền/JSON sai hoặc output không ghi được: hiện lỗi có thể hiểu; không tạo project thay thế, không đổi project âm thầm, không mất ảnh cũ.
- Job đang chạy khi chọn project khác: vẫn thuộc project gốc; không nhầm trạng thái, không tự cancel. Test multi-project queue vì queue hiện nhận `job_id` và API cancel có đường tác động toàn queue; không mở rộng chức năng cancel nếu không cần thiết để đạt hành vi này.
- Thành công phân biệt **đã lưu**, **đã queue** và **đã tạo ảnh**; lỗi một asset không được che giấu bởi thành công asset khác.

## 6. Kế hoạch kiểm chứng G-05

1. **Backend/API, isolated:** list rỗng/đầy, project legacy và duplicate name; tạo name hợp lệ/rỗng/trùng; project hỏng/mất; chọn theo ID nội bộ đúng; Batch vào đúng project; tên asset/filename/ID va chạm, lỗi ghi và retry; revision và file cũ còn nguyên. Thử một project chứa cả Batch và legacy Concept job, kể cả startup/recovery trên bản sao.
2. **Queue + lưu ảnh:** kiểm tra lưu thành công rồi queue lỗi, queue thành công nhưng response bị mất, retry cùng request, retry với nội dung khác và các trường hợp restart được xử lý. Với trạng thái không thể xác định chắc sau restart, báo chưa rõ và chờ user quyết định thay vì tự chạy lại hoặc tuyên bố exactly-once; bảo vệ ảnh/revision cũ. Dùng adapter giả có kiểm soát để thực sự đi qua queue và output, không gọi đó là model thật. Test job hai project, chuyển project trong khi đang chạy, sự cố trước/sau publish và trạng thái chính xác. Nếu vấn đề crash recovery không giải quyết trọn trong task, báo hạn chế và không khẳng định bảo đảm tuyệt đối.
3. **Browser:** hai project khác nhau và trùng tên, tạo/chọn, nhập prompt, mở gallery, chuyển project với response đến muộn, reload, lỗi backend/project thiếu. Xác minh UI không đòi nhập ID hoặc chọn folder và Concept vẫn là placeholder.
4. **Host:** build frontend; chạy các check cấu hình bằng `ASSETGEN_SETTINGS` cô lập. Nếu runtime/weights thật có sẵn và được phép, gen tối thiểu một asset trên output tạm, kiểm tra ảnh và revision. Nếu không có thì ghi rõ UNVERIFIED; không suy từ mock hoặc chỉ build. Không cài dependency khi chưa được phép.
5. **Review:** so sánh với Criteria/Plan, kiểm tra mọi thay đổi dữ liệu và kết quả của từng phép thử; không claim toàn hệ thống đã được chứng minh khi chỉ có test hẹp.

## 7. Concept và plugin — hợp đồng ứng viên, chưa cam kết

Đây là khung để **G-07 thiết kế và xác minh**, không phải API đã tồn tại hoặc lệnh triển khai sẵn:

| Bước | Người/component chủ động | Input → output mong muốn | Ranh giới cần chứng minh |
|---|---|---|---|
| 1 | User + ChatGPT Web | Ảnh concept trong chat → phân tích trình Human | ChatGPT nhìn hiểu concept; chất lượng không bảo đảm. |
| 2 | Human | Duyệt phân tích trong chat | App local không tự chứng minh nội dung hay sự kiện duyệt trong ChatGPT. |
| 3 | ChatGPT + plugin | Sau duyệt: HTML, danh sách asset có định danh, đường dẫn và prompt → file ở project local | Plugin/tunnel có khả năng ghi đúng nơi, nhận biết lỗi, không được giả định chỉ từ tên plugin. |
| 4 | Plugin + app local + model | Yêu cầu gen từng asset → queue, ảnh local, trạng thái/kết quả | Quyền kích hoạt/tình trạng model, timeout, lỗi, và nơi đặt file cần thử; không chạy lệnh tùy ý như cơ chế mặc định. |
| 5 | UI local | HTML + ảnh theo path → render; chọn phần tử → copy ID và ảnh | Cách render, cô lập HTML, hỗ trợ CSS/JS/asset tương đối và clipboard phải thử trong host thật. |
| 6 | User + ChatGPT + plugin | User paste ID, ảnh và nhận xét → prompt thay đổi → gen đúng asset | Định danh phải ánh xạ không mơ hồ, xử lý ID/ảnh thiếu hoặc sai, lỗi và feedback đi qua chat. |
| 7 | App local | Revision mới → ảnh active ở đường HTML; revision cũ vẫn chọn lại được | Cần thiết kế xuất bản, đồng bộ và phục hồi khi lỗi/crash; không coi `replace` một file là bảo đảm toàn pipeline. |

**Artifact/contract cần đặc tả ở M3:** project được chọn; file HTML; manifest liên kết `element_id` ↔ `asset_id` ↔ prompt ↔ relative asset path ↔ version; trạng thái từng yêu cầu (accepted/queued/running/completed/failed); format báo lỗi; lựa chọn phiên bản đang dùng. Đây là các thông tin ứng viên để làm rõ, không áp đặt schema hay tên file trước khi hiểu plugin và browser.

**Spike tối thiểu:** trên môi trường cách ly, xác định plugin/tunnel thật và quyền của nó; từ ChatGPT Web thực hiện một yêu cầu có chủ đích để ghi một file vô hại vào vùng thử, yêu cầu local model tạo một asset, quan sát file và báo thành công/thất bại về ChatGPT. Ghi host, phiên bản, giới hạn quyền, log không chứa bí mật và chi phí vận hành. Kiểm tra đường lỗi và timeout. Thành công chỉ chứng minh ranh giới đã thử; chưa chứng minh phân tích/duyệt, render, clipboard hay cả workflow.

**Kiểm soát:** scope file/tác vụ phải tương xứng với use cá nhân; không tuyên bố thư mục làm việc là sandbox chống lệnh tùy ý. Render HTML sinh từ AI cần phương án phù hợp để không tự cho code đó cùng quyền với app; lựa chọn sandbox và khả năng đọc asset/copy cần thử thực tế. Đừng đưa credentials hay dữ liệu khác vào prompt/log. Quyền lực ChatGPT Web, plugin và tunnel phụ thuộc platform bên ngoài, không do code dự án tự bảo đảm.

## 8. GSA và giới hạn xác minh

GSA đọc `AGENTS.md`, role/skills và `harness/` nếu thực sự được cấp; tuân theo trạng thái branch và quy trình task trong môi trường hiện hành. Task-07 đang ACTIVE với evidence, cần xử lý theo quy trình trước task mới. Không coi file cấu hình là chứng minh native dispatch, enforcement hay user approval có xác thực. Nếu là môi trường online thiếu Mac/model/clipboard/plugin, thực hiện phần kiểm thử khả dụng và báo giới hạn; không bịa kết quả hoặc sao chép dữ liệu cá nhân lên môi trường khác. [Handoff](./HANDOFF_GSA.md) nêu bước bắt đầu.

## 9. Hướng dẫn thực hiện cho GSA — hướng dẫn đã duyệt, chưa phải task ACTIVE

Đọc phần này như senior bàn giao cho implementer. Dưới đây là cách chia việc và contract **đề xuất để review**, không chứng minh code đã có và không tự kích hoạt task. Human đã duyệt Plan và chọn báo trùng asset. Planner/Reviewer kiểm tra lại và ghi từng task có goal + exit condition vào `TASKS.md` theo harness thực tế. Chỉ làm một lát cắt có thể kiểm chứng mỗi lần; không dùng tên task dưới đây làm ID chính thức.

### 9.1 Bước chuẩn bị trước khi sửa

1. Đọc `AGENTS.md`, Criteria, Plan, milestones, proposal này, `TASKS.md` và evidence TASK-07. Xác nhận host, task-07 ACTIVE thực tế, quyền ghi và branch nếu là Git. Không tự sửa branch policy; nếu thiếu policy bắt buộc, báo BLOCKED theo hướng dẫn dự án.
2. Kiểm tra `settings.json` chỉ để hiểu cấu trúc, không in secrets; tạo file settings test trỏ project/output vào thư mục tạm độc lập. Kiểm tra các test không xóa đường dẫn thật trước khi chạy. Nếu có dữ liệu cần thử, copy trước rồi hash bản gốc trước/sau; không dùng dữ liệu thật làm fixture ghi.
3. Kiểm tra baseline bằng `python3 harness/common/verify.py` với `ASSETGEN_SETTINGS` cô lập, build frontend ra thư mục tạm, và browser test nếu môi trường cho phép. Ghi lệnh, host, pass/fail và giới hạn. Nếu baseline hỏng, điều tra nguyên nhân trước khi sửa; không sửa test để che lỗi.
4. Snapshot các file dự định sửa và kiểm tra cách phục hồi. Vì workspace từng không có Git, không coi `git diff` là phương án rollback mặc định. Nếu task scope vượt dự kiến, cập nhật phạm vi và review trước khi mở rộng.

### 9.2 Lát cắt A — API tạo và liệt kê project (G-05)

**Đọc trước:** `backend/projects/models.py`, `backend/projects/manager.py`, phần `/projects` và `project_root_for` trong `backend/api/main.py`, test `tests/test_smoke_api.py` và `tests/backend_verify.py`.

**Làm:** giữ file-format và `POST /projects`, `GET /projects/{id}` đang có; bổ sung `GET /projects` và kiểm tra tên tạo mới không rỗng sau `strip()`. Không chuyển thư mục theo tên người dùng, không tạo schema mới chỉ để list. Không sửa JSON project khi chỉ đọc danh sách. Tên project trùng được phép; project khác nhau vẫn có UUID khác nhau.

**Contract ứng viên để hiện thực nhất quán:** `GET /projects` trả `200` với `{ "projects": [{"id": "<uuid>", "name": "Tên", "created_at": "<ISO-8601>"}], "warnings": [] }`; root chưa có project trả mảng rỗng. Một record lỗi được bỏ khỏi mảng hợp lệ và thêm cảnh báo tổng quát `PROJECT_READ_FAILED` không chứa nội dung file; không xóa hoặc sửa record. Nếu không đọc được toàn root, trả lỗi rõ và không giả vờ danh sách rỗng. Thứ tự: mới tạo trước, tie-break ổn định bằng ID nội bộ. Tên trắng trả 422; tên trùng tạo project riêng. Format lỗi cụ thể là đề xuất, cần giữ nhất quán giữa test và UI; không thêm lộ trình migration ngoài scope.

**Xong khi:** test API qua TestClient với temporary root chứng minh danh sách rỗng, tạo/tải danh sách, hai project cùng tên, tên chỉ gồm khoảng trắng, project JSON hỏng và root không đọc được (nếu host cho phép mô phỏng hợp lệ). Đối chiếu file gốc/copy không thay đổi khi list; test hiện có về Batch vẫn chạy. Lát cắt này chưa thay UI.

### 9.3 Lát cắt B — Gắn project picker vào Batch (G-05)

**Đọc trước:** `frontend/src/App.jsx`, `frontend/src/components/BatchWorkspace.jsx`, `BatchGallery.jsx`, `frontend/tests/concept-placeholder.spec.ts`. Kiểm tra API GSA đã thật sự tạo ở A; không dựa trên ví dụ ở proposal nếu kết quả review đã thay contract.

**Làm:** lưu selection tại nơi cả Batch lẫn Gallery cùng dùng. Hiển thị tên; tạo mới bằng input, chọn cũ bằng danh sách, không hiện ô nhập ID/folder. Hai project trùng tên dùng ngày giờ tạo; nếu vẫn trùng thì thêm nhãn chỉ đọc gắn ổn định với từng project (ví dụ một đoạn ID đủ phân biệt), để user không phải nhập hay nhớ mã. Nhãn không được đổi khi danh sách project thay đổi; kiểm tra cả trường hợp đoạn ID trùng. Chỉ chọn project mới sau response thành công. Khi khôi phục localStorage, xác minh project còn tồn tại. Với yêu cầu async cũ, gắn project/request tương ứng hoặc hủy khi có thể để response muộn không ghi nhầm state mới.

**Quy tắc chuyển project đề xuất:** khi user đổi project, giữ job đã queue ở project cũ; bỏ preview prompt **chưa lưu** chỉ sau khi người dùng được cảnh báo và xác nhận nếu có dữ liệu đang nhập. Sau khi chọn, xóa preview cũ và thông báo lỗi/trạng thái cũ khỏi màn hình mới; gallery tải theo ID mới. Trong lúc request save/queue đang chờ, giữ đích từ thời điểm bấm Generate và không để response muộn điều hướng gallery sang project khác. Không dùng cách chuyển project làm cancel toàn queue.

**Xong khi:** browser test với hai project trùng tên và hai project khác tên, tạo mới/hủy/lỗi, chọn cũ, reload hợp lệ/missing, input chưa lưu, server lỗi và response cũ về muộn. User thấy project đúng trước khi Generate, Gallery đúng sau đó; không có thao tác nhập ID/folder; Concept vẫn placeholder. API giả lập trong browser test phải được ghi là giả lập; còn kiểm tra API thật phải chạy riêng.

### 9.4 Lát cắt C — Không ghi đè và retry rõ ràng (G-05)

G-01 là ràng buộc regression và bảo toàn dữ liệu, không phải GOAL thứ hai của task.

**Đọc trước:** `save_batch_jobs`, `generate_batch`, `process_job`, `publish_image`, `image_filename` trong `backend/api/main.py`; `backend/projects/manager.py`, `backend/generation/parser.py`, `backend/queue/engine.py`, `tests/test_regressions.py` và `tests/test_legacy_concept_cleanup.py`.

**Làm:** giữ quyết định Human: batch mới có asset trùng trong cùng project thì báo trùng, user đổi tên; regenerate là thao tác riêng. Trước khi ghi, kiểm tra cả tên/đường output có thể xung đột lẫn ID job hiện hữu; không ghi đè legacy hoặc job có selected revision. Kiểm tra toàn bộ payload trước khi ghi batch, giữ dữ liệu nếu validation thất bại. Khi publish, không thay file không thuộc asset đích. Bảo toàn revision cũ khi regenerate hoặc khi một bước thất bại. Tính tương đương tên theo filesystem thực tế là vấn đề cần test, không xem slug parser là đủ.

**Retry giữa save và queue:** trước khi code, thiết kế một cách phân biệt chính xác retry của cùng draft với request mới, bao gồm response queue bị mất sau khi queue thành công. Có thể dùng khóa request ổn định hoặc cơ chế tương đương; phải ghi rõ nơi lưu, cách so khớp nội dung và hành vi khi request không khớp hoặc restart. Không được gán lại `READY` cho job đang chạy/đã xong, không reset `selected_revision_id`, không queue hai lần trong các tình huống đã được kiểm chứng, không trả số queue sai. Đưa thiết kế nhỏ này vào task review; không tự nhận crash-consistency nếu chưa thử. Vì queue hiện in-process, không giả định nó sống qua restart.

**Xong khi:** test integration isolated có các case: tạo job, lặp request cùng nội dung sau save và sau mất response queue; nội dung khác với cùng khóa; job đã queued/completed; hai asset có slug/filename va chạm; ID trùng Batch và legacy; file lạ đã tồn tại; lỗi ghi/adapter/publish; regenerate và revision trước còn đọc được. Verify dữ liệu trước/sau bằng bytes hoặc ảnh thực tế, không chỉ kiểm status HTTP. Một số tình huống có thể cần fault injection; ghi rõ cái nào là mô phỏng. Tài liệu không yêu cầu scheduler bền vững hay database.

### 9.5 Lát cắt D — Kiểm tra tổng thể và bàn giao G-05

1. Chạy lại toàn bộ configured backend checks trong isolated root; không tính các test Concept cũ đã loại như regression cần khôi phục. Build ra thư mục tạm và chạy browser tests phù hợp. Báo từng lệnh và kết quả thật.
2. Dùng bản sao project cũ: list/chọn, đọc job và revision; so sánh hash dữ liệu gốc trước/sau. Nếu runtime/model Mac khả dụng, thực hiện một Batch thật với project/output tạm và kiểm ảnh cùng revision. Nếu không, nêu rõ chưa chạy thật; adapter fake chỉ chứng minh orchestration.
3. Reviewer kiểm tra diff, dữ liệu, tests và scope trước khi coi hoàn thành. Nếu code/hook/harness không khả dụng trên host GSA, báo chính xác thay vì nói đã được bảo vệ hoặc đã review.
4. Cập nhật `TASKS.md`, milestone/evidence bằng kết quả quan sát; không tự ghi Human acceptance. Không chuyển sang Concept chỉ vì tests giả lập đã pass.

### 9.6 Sau Batch — giao việc thiết kế Concept, chưa phải giao code

GSA nên tạo đề xuất chi tiết riêng ở M3 sau khi đã biết plugin và tunnel thật, bao gồm: sơ đồ luồng và trách nhiệm từng bên; ví dụ request/response thực tế của plugin nếu có; artifact HTML/prompt/asset và liên kết ID; chọn phần tử và cách copy ảnh; lựa chọn version và rollback; quyền/trust boundary; lỗi, chi phí và giới hạn. Kèm spike một asset và bằng chứng. Nếu plugin không cung cấp quyền cần thiết hoặc không truy cập được ChatGPT Web, dừng ở kết quả và hỏi Human; không bịa API hay lén thay bằng luồng thủ công. Sau khi Human quyết định thiết kế và kết quả khả thi, mới lập task G-08.
