from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from accounts.models import User


USERS = [
    dict(email='admin@ccs.dev',  name='Admin',      role=User.Role.ADMIN, status=User.Status.ACTIVE, password='admin1234'),
    dict(email='cct@ccs.dev',    name='Care Taker',  role=User.Role.CCT,   status=User.Status.ACTIVE, password='cct1234'),
    dict(email='alice@ccs.dev',  name='Alice',       role=User.Role.USER,  status=User.Status.ACTIVE, password='user1234'),
    dict(email='bob@ccs.dev',    name='Bob',         role=User.Role.USER,  status=User.Status.ACTIVE, password='user1234'),
    dict(email='carol@ccs.dev',  name='Carol',       role=User.Role.USER,  status=User.Status.ACTIVE, password='user1234'),
]


class Command(BaseCommand):
    help = 'Create test users for local development (safe to re-run — skips existing emails).'

    def handle(self, *args, **options):
        for data in USERS:
            password = data.pop('password')
            if User.objects.filter(email=data['email']).exists():
                self.stdout.write(f"  skip    {data['email']} (already exists)")
            else:
                user = User(username=data['email'], **data)
                user.set_password(password)
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  created [{data['role']:5}]  {data['email']}  pw: {password}"
                    )
                )
            data['password'] = password  # restore for next iteration
