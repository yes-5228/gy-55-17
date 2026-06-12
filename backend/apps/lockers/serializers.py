from rest_framework import serializers

from .models import LockerCell


class LockerCellSerializer(serializers.ModelSerializer):
    status_label = serializers.CharField(source="get_status_display", read_only=True)
    size_label = serializers.CharField(source="get_size_display", read_only=True)
    cell_type_label = serializers.CharField(source="get_cell_type_display", read_only=True)
    is_temperature_alert = serializers.BooleanField(read_only=True)

    class Meta:
        model = LockerCell
        fields = [
            "id",
            "code",
            "zone",
            "size",
            "size_label",
            "status",
            "status_label",
            "cell_type",
            "cell_type_label",
            "temperature",
            "min_temperature",
            "max_temperature",
            "is_temperature_alert",
            "last_opened_at",
            "updated_at",
        ]
