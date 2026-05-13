# Hướng dẫn chạy data-driven test Add New User Moodle

Tài liệu này hướng dẫn cách chạy bộ kiểm thử tự động trong dự án này.

## 1. Mục tiêu

Dự án dùng Selenium WebDriver + unittest để kiểm thử chức năng **Add a new user** trên Moodle demo.

Test đã được chuyển sang dạng **data-driven testing**:

- Script chính: `test_add_user.py`
- File dữ liệu test: `test_data_users.csv`
- File gốc export từ Katalon Recorder: `SchoolMoodle-AddNewUser.krecorder`

Mỗi dòng trong `test_data_users.csv` là một bộ dữ liệu test. Script sẽ đọc từng dòng và chạy test tương ứng.

## 2. Yêu cầu môi trường

Cần cài đặt:

- Python 3
- Google Chrome
- ChromeDriver tương thích với phiên bản Chrome đang dùng
- Selenium cho Python

Kiểm tra Python:

```bash
python3 --version
```

Cài Selenium:

```bash
python3 -m pip install selenium
```

Kiểm tra ChromeDriver:

```bash
chromedriver --version
```

Nếu máy không nhận lệnh `chromedriver`, cần tải ChromeDriver và thêm vào `PATH`, hoặc chạy test với biến môi trường `CHROMEDRIVER_PATH`.

## 3. Cấu trúc file

```text
SchoolMoodleAddNewUser/
├── README.md
├── SchoolMoodle-AddNewUser.krecorder
├── test_add_user.py
└── test_data_users.csv
```

Ý nghĩa:

- `SchoolMoodle-AddNewUser.krecorder`: file test case gốc export từ Katalon Recorder.
- `test_data_users.csv`: dữ liệu đầu vào và kết quả mong đợi.
- `test_add_user.py`: script unittest đọc CSV và chạy toàn bộ test data.
- `README.md`: hướng dẫn chạy test.

## 4. Cấu trúc dữ liệu CSV

File `test_data_users.csv` có các cột:

```csv
test_id,username,password,firstname,lastname,email,city,country,force_password_change,suspended,cancel,verify_after_login,Expected Result
```

Ý nghĩa từng cột:

| Cột | Ý nghĩa |
| --- | --- |
| `test_id` | Mã test case, ví dụ `TC-004-001` |
| `username` | Username cần tạo |
| `password` | Password cần nhập |
| `firstname` | First name |
| `lastname` | Last name |
| `email` | Email |
| `city` | City/town |
| `country` | Country |
| `force_password_change` | `true` nếu cần bật Force password change |
| `suspended` | `true` nếu cần tạo user bị suspended |
| `cancel` | `true` nếu test nút Cancel thay vì Submit |
| `verify_after_login` | `true` nếu sau khi tạo user cần logout manager và login bằng user mới để verify |
| `Expected Result` | Text mong đợi xuất hiện trên trang |

Ví dụ:

```csv
TC-004-007,thuan2,t123,thuan,truong,thuan2gmail.com,Ho Chi Minh city,Viet Nam,false,false,false,false,Invalid email address
```

Dòng trên kiểm tra email sai định dạng và mong đợi trang hiển thị `Invalid email address`.

## 5. Cách chạy test

Mở terminal tại thư mục dự án và chạy:

```bash
python3 test_add_user.py
```

Hoặc chạy bằng unittest:

```bash
python3 -m unittest test_add_user.py
```

Nếu ChromeDriver không nằm trong `PATH`, chạy bằng cách truyền biến môi trường:

```bash
CHROMEDRIVER_PATH=/duong/dan/toi/chromedriver python3 test_add_user.py
```

Ví dụ trên macOS nếu ChromeDriver nằm trong thư mục dự án:

```bash
CHROMEDRIVER_PATH=./chromedriver python3 test_add_user.py
```

## 6. Cách script hoạt động

Khi chạy `test_add_user.py`, script sẽ:

1. Mở Chrome bằng Selenium WebDriver.
2. Đọc toàn bộ dữ liệu từ `test_data_users.csv`.
3. Với mỗi dòng dữ liệu:
   - Login bằng tài khoản manager.
   - Mở trang Add a new user.
   - Nhập dữ liệu vào form.
   - Submit hoặc Cancel tùy theo cột `cancel`.
   - Nếu `verify_after_login=true`, script sẽ logout manager và login bằng user vừa tạo để kiểm tra tiếp.
   - Kiểm tra text thực tế trên trang có chứa giá trị trong cột `Expected Result` hay không.
4. Nếu có dòng nào lỗi, unittest sẽ báo fail kèm `test_id`.

## 7. Cách thêm hoặc sửa dữ liệu test

Để thêm test case mới:

1. Mở `test_data_users.csv`.
2. Thêm một dòng mới theo đúng header.
3. Điền dữ liệu input.
4. Điền kết quả mong đợi vào cột `Expected Result`.
5. Chạy lại test.

Ví dụ thêm một user hợp lệ:

```csv
TC-004-016,newuser16,t123,Nguyen,Van A,newuser16@example.com,Ho Chi Minh city,Viet Nam,false,false,false,false,Changes saved
```

Lưu ý:

- Không được xóa dòng header đầu tiên.
- Nếu giá trị có dấu phẩy, nên đặt trong dấu nháy kép.
- Nếu test cần kiểm tra sau khi login user mới, đặt `verify_after_login=true`.
- Nếu test user bị suspended, đặt `suspended=true` và `verify_after_login=true` để kiểm tra login fail.

## 8. Cách kiểm tra cú pháp trước khi chạy thật

Chạy lệnh:

```bash
python3 -m py_compile test_add_user.py
```

Nếu không có lỗi hiển thị nghĩa là file Python hợp lệ về cú pháp.

Kiểm tra CSV đọc được bao nhiêu dòng:

```bash
python3 - <<'PY'
import csv
with open('test_data_users.csv', newline='', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))
print('CSV rows:', len(rows))
print('Headers:', ','.join(rows[0].keys()))
PY
```

Kết quả mong đợi hiện tại:

```text
CSV rows: 15
```

## 9. Lỗi thường gặp

### Lỗi không tìm thấy ChromeDriver

Thông báo thường gặp:

```text
WebDriverException: 'chromedriver' executable needs to be in PATH
```

Cách xử lý:

- Cài ChromeDriver đúng version với Chrome.
- Thêm ChromeDriver vào `PATH`.
- Hoặc chạy bằng `CHROMEDRIVER_PATH`.

### Lỗi ChromeDriver không tương thích Chrome

Cách xử lý:

- Kiểm tra version Chrome.
- Tải ChromeDriver tương ứng.

### Lỗi không tìm thấy element

Có thể do Moodle demo thay đổi giao diện hoặc load chậm.

Cách xử lý:

- Chạy lại test.
- Kiểm tra lại locator trong `test_add_user.py`.
- Tăng thời gian chờ nếu cần.

### Test fail vì user đã tồn tại

Moodle demo có thể chưa reset dữ liệu hoặc user đã được tạo ở lần chạy trước.

Cách xử lý:

- Đổi `username` và `email` trong `test_data_users.csv`.
- Hoặc đợi Moodle demo reset.

## 10. Ghi chú

- Test phụ thuộc vào website `https://school.moodledemo.net/`, nên kết quả có thể thay đổi nếu site demo reset dữ liệu hoặc đổi giao diện.
- File `test_data_users.csv` hiện đã được trích xuất từ các test case trong `SchoolMoodle-AddNewUser.krecorder`.
- Script kiểm tra kết quả bằng cách tìm text trong cột `Expected Result` trên nội dung trang sau khi thao tác.
