import random
from string import digits

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.lockers.models import LockerCell
from apps.notifications.services import send_pickup_notification
from .models import Parcel


def generate_pickup_code():
    while True:
        code = "".join(random.choices(digits, k=6))
        if not Parcel.objects.filter(
            pickup_code=code,
            status__in=[Parcel.Status.STORED, Parcel.Status.RETURN_PENDING],
        ).exists():
            return code


def _describe_cell_type(cell_type):
    if cell_type == LockerCell.CellType.REFRIGERATED:
        return "冷藏"
    if cell_type == LockerCell.CellType.NORMAL:
        return "普通"
    return ""


def _describe_size(size):
    if size == LockerCell.Size.SMALL:
        return "小"
    if size == LockerCell.Size.MEDIUM:
        return "中"
    if size == LockerCell.Size.LARGE:
        return "大"
    return ""


def _describe_prefix(cell_type, size):
    parts = [_describe_size(size), _describe_cell_type(cell_type)]
    return "".join(p for p in parts if p)


@transaction.atomic
def inbound_parcel(validated_data):
    size = validated_data.pop("size", None)
    cell_type = validated_data.pop("cell_type", None)
    cells = (
        LockerCell.objects.select_for_update()
        .filter(status=LockerCell.Status.EMPTY)
        .order_by("zone", "code")
    )
    if size:
        cells = cells.filter(size=size)
    if cell_type:
        cells = cells.filter(cell_type=cell_type)
    cells_list = list(cells)
    prefix = _describe_prefix(cell_type, size)
    if not cells_list:
        if prefix:
            raise ValidationError({"locker_cell": f"没有空闲的{prefix}柜格。"})
        else:
            raise ValidationError({"locker_cell": "没有空闲柜格。"})
    available_cells = [cell for cell in cells_list if not cell.is_temperature_alert]
    if not available_cells:
        if cell_type == LockerCell.CellType.REFRIGERATED:
            size_label = _describe_size(size)
            if size_label:
                raise ValidationError(
                    {"locker_cell": f"{size_label}号冷藏柜温度异常，暂无可用于入库的{size_label}号冷藏柜格。"}
                )
            else:
                raise ValidationError(
                    {"locker_cell": "冷藏柜温度异常，暂无可用于入库的冷藏柜格。"}
                )
        elif prefix:
            raise ValidationError(
                {"locker_cell": f"冷藏柜温度异常，暂无可用于入库的{prefix}柜格。"}
            )
        else:
            raise ValidationError(
                {"locker_cell": "冷藏柜温度异常，暂无可用于入库的柜格。"}
            )
    cell = available_cells[0]

    if Parcel.objects.filter(tracking_no=validated_data["tracking_no"]).exists():
        raise ValidationError({"tracking_no": "该运单号已经入库。"})

    parcel = Parcel.objects.create(
        **validated_data,
        locker_cell=cell,
        pickup_code=generate_pickup_code(),
    )
    cell.status = LockerCell.Status.OCCUPIED
    cell.save(update_fields=["status", "updated_at"])
    send_pickup_notification(parcel)
    return parcel


@transaction.atomic
def open_by_pickup_code(pickup_code):
    parcel = (
        Parcel.objects.select_for_update()
        .select_related("locker_cell")
        .filter(pickup_code=pickup_code, status=Parcel.Status.STORED)
        .first()
    )
    if not parcel:
        return None

    now = timezone.now()
    parcel.status = Parcel.Status.PICKED_UP
    parcel.picked_up_at = now
    parcel.save(update_fields=["status", "picked_up_at"])

    cell = parcel.locker_cell
    cell.status = LockerCell.Status.OPEN
    cell.last_opened_at = now
    cell.save(update_fields=["status", "last_opened_at", "updated_at"])
    return parcel
