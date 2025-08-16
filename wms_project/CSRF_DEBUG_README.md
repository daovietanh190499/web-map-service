# CSRF Token Debug Guide - Web Map Service

## Vấn đề đã gặp

**Lỗi**: `"CSRF Failed: CSRF token missing." when saving topic`

## Nguyên nhân

Frontend đang sử dụng axios để gửi request đến Django backend, nhưng không bao gồm CSRF token trong headers.

## Giải pháp đã thực hiện

### 1. **Cập nhật tất cả axios requests** ✅

Tất cả các axios requests trong `topic.html` đã được cập nhật để bao gồm CSRF token:

```javascript
// Trước (không có CSRF token)
await axios.post(API_BASE, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
});

// Sau (có CSRF token)
await axios.post(API_BASE, formData, {
    headers: { 
        'Content-Type': 'multipart/form-data',
        'X-CSRFToken': getCSRFToken()
    }
});
```

### 2. **Tạo function helper** ✅

```javascript
function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}
```

### 3. **Cập nhật tất cả functions** ✅

- `saveTopic()` - Tạo/cập nhật topic
- `deleteTopic()` - Xóa topic  
- `removeAttachment()` - Xóa attachment
- `loadTopics()` - Tải danh sách topics
- `searchTopics()` - Tìm kiếm topics
- `loadStats()` - Tải thống kê
- `editTopic()` - Chỉnh sửa topic
- `viewTopic()` - Xem topic
- `downloadAttachment()` - Tải attachment

## Cách test

### 1. **Test CSRF Protection**

Truy cập: `http://localhost:8000/test-csrf`

- Click "Test CSRF Token" - Nên thành công (có token)
- Click "Test Without CSRF Token" - Nên bị chặn (không có token)

### 2. **Test Topic Creation**

1. Đăng nhập vào hệ thống
2. Tạo topic mới
3. Kiểm tra console để đảm bảo không có lỗi CSRF

## Debug Steps

### 1. **Kiểm tra CSRF token trong template**

```html
<!-- Đảm bảo có CSRF token -->
{% csrf_token %}
```

### 2. **Kiểm tra CSRF token trong JavaScript**

```javascript
// Mở console và chạy:
document.querySelector('[name=csrfmiddlewaretoken]').value
// Nên trả về một chuỗi dài
```

### 3. **Kiểm tra Network tab**

1. Mở Developer Tools
2. Chuyển sang tab Network
3. Tạo topic mới
4. Kiểm tra request headers có `X-CSRFToken`

### 4. **Kiểm tra Django logs**

```bash
python manage.py runserver --verbosity=2
```

## Cấu hình Backend

### 1. **CSRF Middleware** ✅

```python
MIDDLEWARE = [
    'django.middleware.csrf.CsrfViewMiddleware',
    # ... other middleware
]
```

### 2. **CSRF Cookie Settings** ✅

```python
# CSRF settings
CSRF_USE_SESSIONS = False
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_TRUSTED_ORIGINS = ['http://localhost:8000', 'http://127.0.0.1:8000']

# CSRF Cookie settings
CSRF_COOKIE_NAME = 'csrftoken'
CSRF_HEADER_NAME = 'HTTP_X_CSRFTOKEN'
```

### 3. **REST Framework Settings** ✅

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
```

## Troubleshooting

### 1. **CSRF token missing**

**Nguyên nhân**: Template không có `{% csrf_token %}`

**Giải pháp**: Thêm `{% csrf_token %}` vào template

### 2. **CSRF token expired**

**Nguyên nhân**: Session hết hạn

**Giải pháp**: Refresh trang để lấy token mới

### 3. **CSRF token mismatch**

**Nguyên nhân**: Token trong form khác với token trong session

**Giải pháp**: Clear browser cache và cookies

### 4. **Axios không gửi CSRF token**

**Nguyên nhân**: JavaScript không lấy được token

**Giải pháp**: Kiểm tra function `getCSRFToken()`

## Best Practices

### 1. **Luôn sử dụng CSRF token**

```javascript
// ✅ Tốt
headers: { 'X-CSRFToken': getCSRFToken() }

// ❌ Không tốt  
headers: { 'Content-Type': 'application/json' }
```

### 2. **Kiểm tra token trước khi gửi**

```javascript
function getCSRFToken() {
    // Try to get from cookie first
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') {
            return value;
        }
    }
    // Fallback to DOM if cookie not found
    const tokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
    if (tokenElement) {
        return tokenElement.value;
    }
    // If still not found, try to get from meta tag
    const metaToken = document.querySelector('meta[name=csrf-token]');
    if (metaToken) {
        return metaToken.getAttribute('content');
    }
    throw new Error('CSRF token not found');
}
```

### 3. **Sử dụng function helper nhất quán**

Tất cả các trang đều sử dụng function `getCSRFToken()` để đảm bảo tính nhất quán:

```javascript
// ✅ Sử dụng function helper
headers: { 'X-CSRFToken': getCSRFToken() }

// ❌ Không sử dụng function helper
headers: { 'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || '' }
```

### 4. **Cookie-based CSRF Token**

Function `getCSRFToken()` được thiết kế để ưu tiên lấy token từ cookie:

```javascript
// 1. Ưu tiên lấy từ cookie 'csrftoken'
// 2. Fallback về DOM element '[name=csrfmiddlewaretoken]'
// 3. Fallback về meta tag 'meta[name=csrf-token]'
// 4. Throw error nếu không tìm thấy token
```

### 5. **Page Reload After Login**

Tất cả các trang đều reload sau khi login thành công để cập nhật trạng thái:

```javascript
.then(data => {
    if (data.message) {
        alert('Đăng nhập thành công!');
        loginModal.classList.add('hidden');
        // Reload page to update login state
        window.location.reload();
    }
})
```

### 6. **Error handling**

```javascript
try {
    await axios.post(url, data, {
        headers: { 'X-CSRFToken': getCSRFToken() }
    });
} catch (error) {
    if (error.response?.status === 403) {
        // CSRF error - refresh page
        window.location.reload();
    }
}
```

## Files Updated with CSRF Protection

### ✅ **index.html** - Trang chủ
- Thêm function `getCSRFToken()` với cookie support
- Cập nhật login/logout requests với CSRF token
- Cập nhật tất cả API calls với CSRF token:
  - `/api/images/search/` (POST)
  - `/api/basemaps/` (GET, POST, PUT, DELETE)
  - `/api/arcgis-config/` (GET, POST, PUT)
- Sử dụng `getCSRFToken()` cho tất cả API calls
- **Reload trang khi login thành công** để cập nhật trạng thái

### ✅ **draw.html** - Trang vẽ bản đồ
- Thêm function `getCSRFToken()` với cookie support
- Cập nhật login/logout requests với CSRF token
- Cập nhật tất cả API calls với CSRF token:
  - `api/images/{id}` (GET)
  - `api/predict-area/{id}/` (GET, DELETE)
  - `/api/predict-area/save_area/` (POST)
- Sử dụng `getCSRFToken()` cho tất cả API calls
- **Reload trang khi login thành công** để cập nhật trạng thái

### ✅ **compare.html** - Trang so sánh bản đồ
- Thêm function `getCSRFToken()` với cookie support
- Cập nhật login/logout requests với CSRF token
- Cập nhật tất cả API calls với CSRF token:
  - `/api/basemaps/` (GET) - cho cả map1 và map2
- Sử dụng `getCSRFToken()` cho tất cả API calls
- **Reload trang khi login thành công** để cập nhật trạng thái

### ✅ **topic.html** - Trang quản lý chủ đề
- Thêm function `getCSRFToken()` với cookie support
- Cập nhật tất cả axios requests với CSRF token
- Cập nhật tất cả API calls với CSRF token:
  - `/api/topics/` (GET, POST, PUT, DELETE)
  - `/api/topics/search/` (GET)
  - `/api/topics/{id}/remove_attachment/` (DELETE)
  - `/api/attachments/{id}/` (GET)
- Sử dụng `getCSRFToken()` cho tất cả API calls
- **Reload trang khi login thành công** để cập nhật trạng thái
- **Login/Logout button đã có sẵn trong navigation bar**

## Testing Checklist

- [ ] CSRF token hiển thị trong template
- [ ] Tất cả axios requests có CSRF token
- [ ] Tất cả fetch requests có CSRF token
- [ ] Login/logout hoạt động trên tất cả các trang
- [ ] Tạo topic thành công
- [ ] Cập nhật topic thành công  
- [ ] Xóa topic thành công
- [ ] Xóa attachment thành công
- [ ] Tải attachment thành công

## Liên hệ

Nếu vẫn gặp vấn đề, hãy:

1. Kiểm tra console errors
2. Kiểm tra Network tab
3. Kiểm tra Django logs
4. Liên hệ team development
