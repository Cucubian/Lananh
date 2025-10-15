# 🏸 Website Quản lý Sân Cầu Lông - BadmintonCourt

Website quản lý sân cầu lông được xây dựng bằng Django 5.x với giao diện hiện đại, vibrant sử dụng TailwindCSS.

## ✨ Tính năng chính

### 👥 Dành cho Khách hàng
- ✅ Đăng ký, đăng nhập tài khoản
- ✅ Quản lý thông tin cá nhân với avatar
- ✅ Xem danh sách sân và giá
- ✅ Đặt sân theo khung giờ
- ✅ Upload minh chứng thanh toán
- ✅ Mua dịch vụ bổ sung (nước uống, thuê vợt, ...)
- ✅ Theo dõi lịch sử giao dịch
- ✅ Hủy đơn đặt sân

### 🏢 Dành cho Chủ sân
- ✅ Dashboard quản lý tổng quan
- ✅ Quản lý đơn đặt sân (xác nhận/từ chối)
- ✅ Quản lý dịch vụ bổ sung
- ✅ Báo cáo doanh thu chi tiết
- ✅ Quản lý người dùng
- ✅ Thống kê theo thời gian

### 👨‍💼 Dành cho Nhân viên
- ✅ Xem danh sách đơn đặt sân
- ✅ Cập nhật trạng thái đơn
- ✅ Quản lý dịch vụ bán kèm

## 🛠️ Công nghệ sử dụng

- **Backend**: Django 5.0.7
- **Frontend**: TailwindCSS (CDN)
- **Database**: SQLite3
- **Icons**: Font Awesome 6.4.0
- **Forms**: django-crispy-forms với crispy-tailwind

## 📦 Cài đặt

### 1. Clone repository

```bash
cd deadlineWebQuanLySanCauLong
```

### 2. Tạo môi trường ảo (khuyến nghị)

```bash
python -m venv venv
```

**Kích hoạt môi trường ảo:**

Windows:
```bash
venv\Scripts\activate
```

macOS/Linux:
```bash
source venv/bin/activate
```

### 3. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 4. Tạo file .env

Sao chép file `.env.example` thành `.env`:

```bash
copy .env.example .env
```

Chỉnh sửa file `.env` với thông tin của bạn:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 5. Migrate database

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Tạo superuser (admin)

```bash
python manage.py createsuperuser
```

Nhập thông tin:
- Username: admin
- Email: admin@example.com
- Password: (nhập mật khẩu mạnh)

### 7. Tạo dữ liệu mẫu (tùy chọn)

Truy cập Django Admin để tạo dữ liệu:

```bash
python manage.py runserver
```

Truy cập: http://127.0.0.1:8000/admin

**Tạo dữ liệu mẫu:**

1. **TimeSlot** (Khung giờ): Tạo các khung giờ từ 06:00 đến 22:00
2. **Court** (Sân): Tạo 3-5 sân với giá khác nhau
3. **User** (Người dùng):
   - Khách hàng: role = "customer"
   - Chủ sân: role = "owner"
   - Nhân viên: role = "staff"
4. **Service** (Dịch vụ): Tạo các dịch vụ như nước uống, thuê vợt
5. **Booking** (Đơn đặt sân): Tạo một số đơn đặt mẫu

### 8. Chạy server

```bash
python manage.py runserver
```

Truy cập website: **http://127.0.0.1:8000**

## 📱 Hướng dẫn sử dụng

### Khách hàng

1. **Đăng ký tài khoản**: Click "Đăng ký" ở góc phải trên
2. **Đăng nhập**: Sử dụng username và password đã đăng ký
3. **Đặt sân**: 
   - Vào menu "Đặt sân"
   - Chọn sân và ngày
   - Chọn khung giờ
   - Xác nhận đặt sân
4. **Thanh toán**:
   - Upload minh chứng thanh toán
   - Chờ xác nhận từ chủ sân
5. **Mua dịch vụ**:
   - Vào menu "Dịch vụ"
   - Tạo đơn hàng
   - Thêm sản phẩm vào đơn

### Chủ sân / Nhân viên

1. **Đăng nhập**: Sử dụng tài khoản có role "owner" hoặc "staff"
2. **Truy cập Dashboard**: Menu "Quản lý"
3. **Xác nhận đơn đặt**:
   - Vào "Quản lý đặt sân"
   - Xem minh chứng thanh toán
   - Cập nhật trạng thái: Đã xác nhận/Từ chối
4. **Xem báo cáo**: Menu "Báo cáo doanh thu"

## 🗂️ Cấu trúc dự án

```
deadlineWebQuanLySanCauLong/
├── badminton_court/          # Cấu hình Django chính
│   ├── settings.py           # Cài đặt dự án
│   ├── urls.py               # URL routing chính
│   └── wsgi.py               # WSGI config
├── accounts/                 # App quản lý người dùng
│   ├── models.py             # User model với roles
│   ├── views.py              # Login, register, profile
│   └── forms.py              # User forms
├── booking/                  # App đặt sân
│   ├── models.py             # Court, TimeSlot, Booking
│   ├── views.py              # Booking logic
│   └── forms.py              # Booking forms
├── services/                 # App dịch vụ bổ sung
│   ├── models.py             # Service, ServiceOrder
│   ├── views.py              # Service order logic
│   └── forms.py              # Service forms
├── management/               # App quản lý (admin)
│   ├── views.py              # Dashboard, reports
│   └── urls.py               # Management URLs
├── templates/                # Templates HTML
│   ├── base.html             # Base template
│   ├── home.html             # Trang chủ
│   ├── accounts/             # Account templates
│   ├── booking/              # Booking templates
│   ├── services/             # Service templates
│   └── management/           # Management templates
├── media/                    # User uploads
├── static/                   # Static files (nếu có)
├── db.sqlite3               # Database SQLite
├── manage.py                 # Django management
├── requirements.txt          # Dependencies
└── README.md                 # Hướng dẫn này
```

## 🎨 Giao diện

- **Theme**: Vibrant với gradient màu xanh dương và xanh lá
- **Responsive**: Tối ưu cho cả desktop và mobile
- **Components**: 
  - Cards với hover effects
  - Gradient buttons
  - Status badges với màu sắc rõ ràng
  - Forms với Tailwind styling
  - Tables responsive
  - Dashboard với charts và statistics

## 🔐 Phân quyền

- **Customer (Khách hàng)**: Đặt sân, mua dịch vụ, xem lịch sử
- **Staff (Nhân viên)**: Xem đơn, cập nhật trạng thái, quản lý dịch vụ
- **Owner (Chủ sân)**: Toàn quyền quản lý, xem báo cáo doanh thu
- **Superuser**: Truy cập Django Admin, quản lý toàn bộ

## 📊 Database Models

### User
- username, email, password
- full_name, phone, address
- role (customer/staff/owner)
- avatar

### Court
- name, description
- price_per_hour
- image
- is_active

### Booking
- customer → User
- court → Court
- date, time_slots
- total_price, status
- payment_proof

### Service
- name, category (drink/equipment/other)
- price, stock
- is_available

### ServiceOrder
- customer → User
- status, total_price
- ServiceOrderItem (many-to-many through)

## 🚀 Tính năng mở rộng (Future)

- [ ] Gửi email xác nhận đặt sân
- [ ] Payment gateway integration
- [ ] Real-time notifications
- [ ] Calendar view cho booking
- [ ] Review & rating system
- [ ] Mobile app
- [ ] Multi-language support

## ⚠️ Lưu ý

1. **Môi trường phát triển**: Code này dành cho môi trường development. Để deploy lên production cần:
   - Đổi `DEBUG=False`
   - Cấu hình ALLOWED_HOSTS
   - Sử dụng database mạnh hơn (PostgreSQL)
   - Cấu hình static files serving
   - Setup HTTPS

2. **Secret Key**: Đổi SECRET_KEY trong production
3. **Media files**: Cấu hình storage cho production (S3, etc.)

## 🐛 Troubleshooting

### Lỗi import Django
```bash
pip install --upgrade django
```

### Lỗi migrations
```bash
python manage.py makemigrations
python manage.py migrate --run-syncdb
```

### Lỗi static files
```bash
python manage.py collectstatic
```

## 👨‍💻 Tác giả

Dự án được phát triển theo yêu cầu quản lý sân cầu lông với Django Framework.

## 📄 License

MIT License - Free to use for learning and development.

---

**Chúc bạn sử dụng vui vẻ! 🏸**

Nếu gặp vấn đề, vui lòng tạo issue hoặc liên hệ support.
