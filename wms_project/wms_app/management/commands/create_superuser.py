from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Tạo superuser mặc định cho hệ thống'

    def handle(self, *args, **options):
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123'
            )
            self.stdout.write(
                self.style.SUCCESS('Superuser "admin" đã được tạo thành công với password: admin123')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Superuser "admin" đã tồn tại')
            )
