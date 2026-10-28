from datetime import datetime
from typing import Any

from rest_framework import serializers


class AppointmentCreateInputSerializer(serializers.Serializer[Any]):

    doctor_id = serializers.IntegerField(min_value=1, required=True)
    patient_id = serializers.IntegerField(min_value=1, required=True)
    start_time = serializers.DateTimeField(required=True)
    end_time = serializers.DateTimeField(required=True)

    symptoms = serializers.ListField(
        child=serializers.CharField(max_length=200),
        required=False,
        default=list,
    )

    # Полевой валидатор (validate_<field_name>)
    def validate_doctor_id(self, value: int) -> int:
        return value
    # Межполевой валидатор (Object-level validation)
    def validate(self, attrs: dict[str, object]) -> dict[str, object]:
        start = attrs.get("start_time")
        end = attrs.get("end_time")

        if isinstance(start, datetime) and isinstance(end, datetime):
            if start >= end:
                raise serializers.ValidationError(
                    {
                        "end_time": "Время окончания должно быть позже времени начала",
                    }
                )

        return attrs

class AppointmentOutputSerializer(serializers.Serializer[Any]):
    id = serializers.IntegerField()
    doctor_id = serializers.IntegerField()
    patient_id = serializers.IntegerField()
    status = serializers.CharField()
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    notes = serializers.CharField()
