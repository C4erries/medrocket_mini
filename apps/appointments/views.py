


import json

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.http import require_POST, require_safe

from appointments.serializers import (
    AppointmentCreateInputSerializer,
    AppointmentOutputSerializer,
)
from appointments.services import (
    AppointmentCreateDTO,
    appointment_cancel,
    appointment_create,
    appointment_get_cached,
)


@require_POST
def appointment_create_api_view(request: HttpRequest) -> HttpResponse:
    try:
        body = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    serializer = AppointmentCreateInputSerializer(data=body)
    if not serializer.is_valid():
        return JsonResponse({"errors": serializer.errors}, status=400)

    validated_data = serializer.validated_data
    dto = AppointmentCreateDTO(
        doctor_id=validated_data["doctor_id"],
        patient_id=validated_data["patient_id"],
        start_time=validated_data["start_time"],
        end_time=validated_data["end_time"],
    )
    appointment = appointment_create(dto, symptoms=validated_data["symptoms"])

    return JsonResponse({"id": appointment.id, "status": appointment.status}, status=201)

@require_safe
def appointment_detail_api_view(_request: HttpRequest, appointment_id: int) -> HttpResponse:
    appointment = appointment_get_cached(appointment_id)
    if appointment is None:
        return JsonResponse({"error": "Appointment not found"}, status=404)

    serializer = AppointmentOutputSerializer(appointment)

    return JsonResponse(serializer.data, status=200)

@require_POST
def appointment_cancel_api_view(_request: HttpRequest, appointment_id: int) -> HttpResponse:
    appt = appointment_cancel(appointment_id)
    if appt is None:
        return JsonResponse({"error": "Appointment not found"}, status=404)
    return JsonResponse({"id": appt.id, "status": appt.status}, status=200)
