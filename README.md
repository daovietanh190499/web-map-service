# Web Map Service (WMS)

Dự án Web Map Service là một ứng dụng web cung cấp dịch vụ bản đồ sử dụng Django và các công nghệ hiện đại.

## 🚀 Tính năng

- **Django Backend**: Framework web mạnh mẽ với REST API
- **PostGIS Database**: Hỗ trợ dữ liệu không gian địa lý
- **MinIO Storage**: Lưu trữ file và hình ảnh
- **Redis Cache**: Tăng hiệu suất ứng dụng
- **Docker Containerization**: Triển khai dễ dàng
- **GDAL Support**: Xử lý dữ liệu raster và vector

## 📋 Yêu cầu hệ thống

- Docker và Docker Compose
- Git
- Ít nhất 4GB RAM
- 10GB dung lượng ổ cứng trống

## 🛠️ Cài đặt và chạy dự án

### 1. Clone dự án

```bash
git clone <repository-url>
cd web-map-service
```

### 2. Tạo file môi trường

Tạo file `.env` trong thư mục gốc với nội dung sau:

```bash
# Database Configuration
POSTGRES_USER=wms_user
POSTGRES_PASSWORD=wms_password_123
POSTGRES_DB=wms_database
DB_ENGINE=django.contrib.gis.db.backends.postgis
DB_HOST=wms-db
DB_PORT=5432

# AWS/MinIO Configuration
MINIO_ROOT_USER=wms-minio
MINIO_ROOT_PASSWORD=wms-minio-123!@
AWS_S3_ENDPOINT=http://wms-minio:9000
AWS_S3_REGION=us-east-1
```

### 3. Chạy dự án

#### Cách 1: Sử dụng script tự động
```bash
chmod +x start.sh
./start.sh
```

#### Cách 2: Chạy thủ công
```bash
# Pull code mới nhất
git pull

# Khởi động các container
docker compose up -d --remove-orphans

# Restart để đảm bảo tất cả service hoạt động
docker compose restart
```

### 4. Kiểm tra trạng thái

```bash
# Xem trạng thái các container
docker compose ps

# Xem logs của backend
docker compose logs wms-backend

# Xem logs của database
docker compose logs wms-db
```

## 🌐 Truy cập ứng dụng

Sau khi khởi động thành công, bạn có thể truy cập:

- **Ứng dụng chính**: http://localhost:80
- **MinIO Console**: http://localhost:9001
- **Docker Registry**: http://localhost:5000

### Thông tin đăng nhập MinIO:
- **Username**: wms-minio
- **Password**: wms-minio-123!@

## 📁 Cấu trúc dự án

```
web-map-service/
├── docker-compose.yaml      # Cấu hình Docker services
├── start.sh                 # Script khởi động tự động
├── .env                     # File biến môi trường (cần tạo)
├── wms_project/            # Django application
│   ├── manage.py           # Django management script
│   ├── requirements.txt    # Python dependencies
│   ├── Dockerfile         # Docker image cho backend
│   ├── wms_project/       # Django project settings
│   └── wms_app/           # Django apps
├── wms_data/              # Persistent data storage
│   ├── postgis/           # PostgreSQL/PostGIS data
│   ├── minio/             # MinIO storage data
│   ├── redis/             # Redis cache data
│   └── docker_registry/   # Docker registry data
└── README.md              # Tài liệu này
```

## 🔧 Các lệnh hữu ích

### Quản lý Docker containers

```bash
# Dừng tất cả services
docker compose down

# Dừng và xóa volumes (cẩn thận - sẽ mất dữ liệu)
docker compose down -v

# Xem logs real-time
docker compose logs -f

# Restart một service cụ thể
docker compose restart wms-backend
```

### Django management commands

```bash
# Truy cập vào container backend
docker compose exec wms-backend bash

# Chạy migrations
docker compose exec wms-backend python3 manage.py migrate

# Tạo superuser
docker compose exec wms-backend python3 manage.py createsuperuser

# Collect static files
docker compose exec wms-backend python3 manage.py collectstatic
```

### Database operations

```bash
# Truy cập PostgreSQL
docker compose exec wms-db psql -U wms_user -d wms_database

# Backup database
docker compose exec wms-db pg_dump -U wms_user wms_database > backup.sql

# Restore database
docker compose exec -T wms-db psql -U wms_user -d wms_database < backup.sql
```

## 🐛 Xử lý sự cố

### Container không khởi động

```bash
# Kiểm tra logs
docker compose logs wms-backend

# Kiểm tra tài nguyên hệ thống
docker stats

# Restart Docker service
sudo systemctl restart docker
```

### Database connection issues

```bash
# Kiểm tra kết nối database
docker compose exec wms-backend python3 manage.py dbshell

# Reset database (cẩn thận - mất dữ liệu)
docker compose down -v
docker compose up -d
```

### Port conflicts

Nếu có xung đột port, bạn có thể thay đổi trong `docker-compose.yaml`:

```yaml
ports:
  - 8080:8000  # Thay đổi từ 80:8000
```

## 📚 Tài liệu tham khảo

- [Django Documentation](https://docs.djangoproject.com/)
- [PostGIS Documentation](https://postgis.net/documentation/)
- [MinIO Documentation](https://docs.min.io/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

## 🤝 Đóng góp

1. Fork dự án
2. Tạo feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Mở Pull Request

## 📄 License

Dự án này được phân phối dưới giấy phép MIT. Xem file `LICENSE` để biết thêm chi tiết.

## 📞 Hỗ trợ

Nếu bạn gặp vấn đề hoặc có câu hỏi, vui lòng:

1. Kiểm tra phần [Xử lý sự cố](#-xử-lý-sự-cố)
2. Tìm kiếm trong [Issues](../../issues)
3. Tạo issue mới nếu vấn đề chưa được báo cáo

---

**Lưu ý**: Đảm bảo bạn đã cài đặt Docker và Docker Compose trước khi chạy dự án này.
