from django import forms
from .models import Appointment, Client, Service, BarberShop
from datetime import datetime, timedelta

class AppointmentForm(forms.ModelForm):
    # Hacemos que la selección de fecha sea más amigable con un widget de tipo Date
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Appointment
        fields = ['client', 'service', 'date', 'time', 'total_price', 'status']
    
    def __init__(self, *args, **kwargs):
        # Asumimos que la barbería se pasará al inicializar el formulario.
        # Esto es crucial para un entorno multi-tenant.
        self.barbershop = kwargs.pop('barbershop', None)
        super().__init__(*args, **kwargs)

        if self.barbershop:
            # Filtramos el queryset de clientes y servicios para que solo muestre
            # los que pertenecen a la barbería actual.
            self.fields['client'].queryset = Client.objects.filter(barbershop=self.barbershop)
            self.fields['service'].queryset = Service.objects.filter(barbershop=self.barbershop)

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get("date")
        time = cleaned_data.get("time")
        service = cleaned_data.get("service")

        if not (date and time and service):
            # Si falta alguno de los campos clave, no podemos validar.
            return cleaned_data

        # --- Lógica de Validación de Disponibilidad ---
        
        # 1. Combinar fecha y hora para obtener un objeto datetime de inicio
        start_datetime = datetime.combine(date, time)
        
        # 2. Calcular la hora de finalización sumando la duración del servicio
        duration = timedelta(minutes=service.duration_minutes)
        end_datetime = start_datetime + duration

        # 3. Buscar citas existentes que se solapen en el tiempo
        # Excluimos la cita actual si estamos en modo de edición
        conflicting_appointments = Appointment.objects.filter(
            barbershop=self.barbershop,
            date=date,
            status='pending' # Solo consideramos citas pendientes
        ).exclude(pk=self.instance.pk)

        for app in conflicting_appointments:
            existing_start = datetime.combine(app.date, app.time)
            existing_end = existing_start + timedelta(minutes=app.service.duration_minutes)
            
            # Comprobación de solapamiento:
            # (StartA <= EndB) and (EndA >= StartB)
            if start_datetime < existing_end and end_datetime > existing_start:
                raise forms.ValidationError(
                    f"Conflicto de horario: ya existe una cita para '{app.service.name}' "
                    f"de {existing_start.strftime('%H:%M')} a {existing_end.strftime('%H:%M')}. "
                    "Por favor, elige otra hora."
                )

        return cleaned_data
