from django.core.management.base import BaseCommand

from apps.lockers.models import LockerCell
from apps.parcels.services import inbound_parcel
from apps.parcels.models import Parcel


class Command(BaseCommand):
    help = "Create demo locker cells and parcels for local verification."

    def handle(self, *args, **options):
        for index in range(1, 13):
            size = LockerCell.Size.SMALL if index <= 4 else LockerCell.Size.MEDIUM if index <= 9 else LockerCell.Size.LARGE
            LockerCell.objects.update_or_create(
                code=f"A{index:02d}",
                defaults={
                    "zone": "A区",
                    "size": size,
                    "cell_type": LockerCell.CellType.NORMAL,
                    "temperature": 23 + index / 10,
                    "min_temperature": 2.0,
                    "max_temperature": 8.0,
                },
            )

        for index in range(1, 13):
            size = LockerCell.Size.SMALL if index <= 4 else LockerCell.Size.MEDIUM if index <= 9 else LockerCell.Size.LARGE
            if index <= 3:
                temperature = 12.0
            elif index <= 6:
                temperature = 1.0
            else:
                temperature = 5.0
            LockerCell.objects.update_or_create(
                code=f"B{index:02d}",
                defaults={
                    "zone": "B区",
                    "size": size,
                    "cell_type": LockerCell.CellType.REFRIGERATED,
                    "temperature": temperature,
                    "min_temperature": 2.0,
                    "max_temperature": 8.0,
                },
            )

        samples = [
            {
                "tracking_no": "SF202606010001",
                "sender_name": "上海仓",
                "receiver_name": "张三",
                "receiver_phone": "13800000001",
                "carrier": "顺丰",
                "size": LockerCell.Size.SMALL,
                "note": "易碎",
            },
            {
                "tracking_no": "YD202606010002",
                "sender_name": "杭州仓",
                "receiver_name": "李四",
                "receiver_phone": "13800000002",
                "carrier": "韵达",
                "size": LockerCell.Size.MEDIUM,
                "note": "",
            },
            {
                "tracking_no": "ZT202606010003",
                "sender_name": "广州仓",
                "receiver_name": "王五",
                "receiver_phone": "13800000003",
                "carrier": "中通",
                "size": LockerCell.Size.LARGE,
                "note": "大件",
            },
        ]
        for sample in samples:
            if not Parcel.objects.filter(tracking_no=sample["tracking_no"]).exists():
                inbound_parcel(sample)

        self.stdout.write(self.style.SUCCESS("Demo data is ready."))
