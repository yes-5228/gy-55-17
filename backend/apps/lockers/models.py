from decimal import Decimal

from django.db import models


class LockerCell(models.Model):
    class Size(models.TextChoices):
        SMALL = "small", "小"
        MEDIUM = "medium", "中"
        LARGE = "large", "大"

    class Status(models.TextChoices):
        EMPTY = "empty", "空闲"
        OCCUPIED = "occupied", "已占用"
        OPEN = "open", "已开门"
        MAINTENANCE = "maintenance", "维护中"

    class CellType(models.TextChoices):
        NORMAL = "normal", "普通"
        REFRIGERATED = "refrigerated", "冷藏"

    code = models.CharField(max_length=20, unique=True)
    zone = models.CharField(max_length=30, default="A区")
    size = models.CharField(max_length=20, choices=Size.choices, default=Size.MEDIUM)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.EMPTY)
    cell_type = models.CharField(
        max_length=20, choices=CellType.choices, default=CellType.NORMAL)
    temperature = models.DecimalField(max_digits=5, decimal_places=2, default=24)
    min_temperature = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("2.00"))
    max_temperature = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("8.00"))
    last_opened_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["zone", "code"]

    def __str__(self):
        return f"{self.zone}-{self.code}"

    @property
    def is_temperature_alert(self):
        if self.cell_type == LockerCell.CellType.REFRIGERATED and not (
            self.min_temperature <= self.temperature <= self.max_temperature
        ):
            return True
        return False
