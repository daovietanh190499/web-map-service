# Hệ thống Authentication - Web Map Service

## Tổng quan

Hệ thống đã được tích hợp authentication hoàn chỉnh với Django REST Framework và Django's built-in authentication system.

## API Endpoints

### Authentication APIs

#### 1. Đăng nhập
- **URL**: `/api/auth/login/`
- **Method**: `POST`
- **Body**:
```json
{
    "username": "admin",
    "password": "admin123"
}
```
- **Response thành công**:
```json
{
    "message": "Đăng nhập thành công",
    "user": {
        "id": 1,
        "username": "admin",
        "email": "admin@example.com",
        "first_name": "",
        "last_name": "",
        "is_staff": true,
        "is_superuser": true
    }
}
```

#### 2. Đăng xuất
- **URL**: `/api/auth/logout/`
- **Method**: `POST`
- **Response**:
```json
{
    "message": "Đăng xuất thành công"
}
```

#### 3. Thông tin người dùng
- **URL**: `/api/auth/user/`
- **Method**: `GET`
- **Response**:
```json
{
    "user": {
        "id": 1,
        "username": "admin",
        "email": "admin@example.com",
        "first_name": "",
        "last_name": "",
        "is_staff": true,
        "is_superuser": true
    }
}
```

#### 4. Đăng ký
- **URL**: `/api/auth/register/`
- **Method**: `POST`
- **Body**:
```json
{
    "username": "newuser",
    "email": "newuser@example.com",
    "password": "password123",
    "first_name": "New",
    "last_name": "User"
}
```

### Django Built-in Authentication URLs

- **Đăng nhập**: `/accounts/login/`
- **Đăng xuất**: `/accounts/logout/`
- **Đổi mật khẩu**: `/accounts/password_change/`

## Cách sử dụng

### 1. Tạo superuser đầu tiên

```bash
cd wms_project
python manage.py create_superuser
```

Hoặc sử dụng management command:

```bash
python manage.py create_superuser
```

### 2. Chạy migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Khởi động server

```bash
python manage.py runserver
```

### 4. Test API

Sử dụng curl hoặc Postman:

```bash
# Đăng nhập
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Kiểm tra thông tin user
curl -X GET http://localhost:8000/api/auth/user/ \
  -H "Cookie: sessionid=<session_id>"
```

## Frontend Integration

### Các trang đã tích hợp authentication:

1. **index.html** - Trang chủ
2. **draw.html** - Trang vẽ bản đồ
3. **compare.html** - Trang so sánh bản đồ
4. **topic.html** - Trang quản lý chủ đề

### Tính năng:

- Popup đăng nhập đẹp mắt
- Kiểm tra trạng thái đăng nhập tự động
- Cập nhật UI theo trạng thái đăng nhập
- Xử lý lỗi và thông báo
- Đăng xuất an toàn

## Bảo mật

- CSRF protection được bật
- Session authentication
- Password validation
- Secure headers

## Cấu hình

### Settings.py

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# Authentication settings
LOGIN_URL = '/api/auth/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
```

## Troubleshooting

### 1. Lỗi CSRF

Nếu gặp lỗi CSRF, hãy đảm bảo:
- CSRF middleware được bật
- Template có `{% csrf_token %}`
- Request có header `X-CSRFToken`

### 2. Lỗi Session

Nếu session không hoạt động:
- Kiểm tra `SESSION_ENGINE` trong settings
- Đảm bảo database migrations đã chạy
- Kiểm tra cookie settings

### 3. Lỗi Permission

Nếu gặp lỗi permission:
- Kiểm tra user đã đăng nhập
- Kiểm tra user có quyền truy cập
- Kiểm tra `DEFAULT_PERMISSION_CLASSES`

## Tích hợp với Topic Management

Sau khi đăng nhập, người dùng có thể:
- Tạo topic mới với tham chiếu user
- Chỉnh sửa topic của mình
- Xem danh sách topic theo user
- Quản lý attachments

## Mở rộng

Để thêm tính năng mới:

1. Tạo view mới trong `auth.py`
2. Thêm URL pattern
3. Cập nhật frontend nếu cần
4. Test với user đã đăng nhập

## Liên hệ

Nếu có vấn đề hoặc cần hỗ trợ, vui lòng liên hệ team development.
