from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Service, Client, Appointment, BarberShop

# NOTA: Por ahora, asumimos que estamos trabajando con una única barbería.
# En una fase posterior, filtraremos todo por la barbería del usuario autenticado.
# Por simplicidad, tomaremos la primera barbería que exista.
# En un entorno real, esto se manejaría con el request.user.
def get_barbershop():
    return BarberShop.objects.first()

class ServiceListView(ListView):
    model = Service
    template_name = 'scheduling/service_list.html'
    context_object_name = 'services'

    def get_queryset(self):
        # Filtrar servicios por la barbería (actualmente la primera que exista)
        barbershop = get_barbershop()
        if barbershop:
            return Service.objects.filter(barbershop=barbershop)
        return Service.objects.none()

class ServiceCreateView(CreateView):
    model = Service
    template_name = 'scheduling/service_form.html'
    fields = ['name', 'price', 'duration_minutes']
    success_url = reverse_lazy('scheduling:service_list')

    def form_valid(self, form):
        # Asignar la barbería automáticamente antes de guardar
        form.instance.barbershop = get_barbershop()
        return super().form_valid(form)

class ServiceUpdateView(UpdateView):
    model = Service
    template_name = 'scheduling/service_form.html'
    fields = ['name', 'price', 'duration_minutes']
    success_url = reverse_lazy('scheduling:service_list')

class ServiceDeleteView(DeleteView):
    model = Service
    template_name = 'scheduling/service_confirm_delete.html'
    success_url = reverse_lazy('scheduling:service_list')


# --- Vistas para Clientes ---

class ClientListView(ListView):
    model = Client
    template_name = 'scheduling/client_list.html'
    context_object_name = 'clients'

    def get_queryset(self):
        barbershop = get_barbershop()
        if barbershop:
            return Client.objects.filter(barbershop=barbershop)
        return Client.objects.none()

class ClientCreateView(CreateView):
    model = Client
    template_name = 'scheduling/client_form.html'
    fields = ['name', 'phone', 'nickname']
    success_url = reverse_lazy('scheduling:client_list')

    def form_valid(self, form):
        form.instance.barbershop = get_barbershop()
        return super().form_valid(form)

class ClientUpdateView(UpdateView):
    model = Client
    template_name = 'scheduling/client_form.html'
    fields = ['name', 'phone', 'nickname']
    success_url = reverse_lazy('scheduling:client_list')

class ClientDeleteView(DeleteView):
    model = Client
    template_name = 'scheduling/client_confirm_delete.html'
    success_url = reverse_lazy('scheduling:client_list')

from .forms import AppointmentForm


# --- Vistas para Citas ---

class AppointmentListView(ListView):
    model = Appointment
    template_name = 'scheduling/appointment_list.html'
    context_object_name = 'appointments'
    ordering = ['-date', '-time']

    def get_queryset(self):
        barbershop = get_barbershop()
        if barbershop:
            return Appointment.objects.filter(barbershop=barbershop).order_by('-date', '-time')
        return Appointment.objects.none()

class AppointmentCreateView(CreateView):
    model = Appointment
    form_class = AppointmentForm
    template_name = 'scheduling/appointment_form.html'
    success_url = reverse_lazy('scheduling:appointment_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['barbershop'] = get_barbershop()
        return kwargs

    def form_valid(self, form):
        form.instance.barbershop = get_barbershop()
        return super().form_valid(form)

class AppointmentUpdateView(UpdateView):
    model = Appointment
    form_class = AppointmentForm
    template_name = 'scheduling/appointment_form.html'
    success_url = reverse_lazy('scheduling:appointment_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['barbershop'] = get_barbershop()
        return kwargs


from django.views.generic import TemplateView
from django.utils import timezone
from django.db.models import Sum
import json

class DashboardView(TemplateView):
    template_name = 'scheduling/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        barbershop = get_barbershop()
        
        if not barbershop:
            # Si no hay barbería, no podemos calcular nada.
            return context

        today = timezone.now().date()
        start_of_week = today - timedelta(days=today.weekday())
        start_of_month = today.replace(day=1)

        # Citas completadas
        completed_appointments = Appointment.objects.filter(barbershop=barbershop, status='completed')

        # 1. Ingresos
        total_today = completed_appointments.filter(date=today).aggregate(total=Sum('total_price'))['total'] or 0
        total_week = completed_appointments.filter(date__gte=start_of_week).aggregate(total=Sum('total_price'))['total'] or 0
        total_month = completed_appointments.filter(date__gte=start_of_month).aggregate(total=Sum('total_price'))['total'] or 0
        
        context['total_today'] = total_today
        context['total_week'] = total_week
        context['total_month'] = total_month

        # 2. Ranking de Clientes
        client_ranking = Client.objects.filter(
            barbershop=barbershop,
            appointments__status='completed'
        ).annotate(
            total_spent=Sum('appointments__total_price')
        ).order_by('-total_spent')[:5] # Top 5
        context['client_ranking'] = client_ranking

        # 3. Próximas Citas
        upcoming_appointments = Appointment.objects.filter(
            barbershop=barbershop,
            date__gte=today,
            status='pending'
        ).order_by('date', 'time')[:5] # 5 más próximas
        context['upcoming_appointments'] = upcoming_appointments

        # 4. Datos para el Gráfico (ej: ingresos de los últimos 7 días)
        chart_data = []
        labels = []
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            labels.append(day.strftime('%d/%m'))
            daily_total = completed_appointments.filter(date=day).aggregate(total=Sum('total_price'))['total'] or 0
            chart_data.append(float(daily_total))
        
        context['chart_labels'] = json.dumps(labels)
        context['chart_data'] = json.dumps(chart_data)
        
        return context


# --- Vistas Públicas para Clientes Finales ---

class PublicServiceListView(ListView):
    model = Service
    template_name = 'scheduling/public_service_list.html'
    context_object_name = 'services'

    def get_queryset(self):
        # En el futuro, la barbería se podría determinar por la URL (ej: barberpro.com/barberia-cool)
        # Por ahora, seguimos usando la primera que exista.
        barbershop = get_barbershop()
        if barbershop:
            return Service.objects.filter(barbershop=barbershop)
        return Service.objects.none()

from django.http import JsonResponse
from datetime import datetime, time, timedelta
from django.views import View
from django.shortcuts import get_object_or_404, redirect

def get_available_slots(request):
    """
    Endpoint de API que devuelve los horarios disponibles para un servicio y fecha específicos.
    """
    date_str = request.GET.get('date')
    service_id = request.GET.get('service_id')
    
    if not date_str or not service_id:
        return JsonResponse({'error': 'Faltan parámetros de fecha o servicio.'}, status=400)

    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        service = Service.objects.get(pk=service_id)
    except (ValueError, Service.DoesNotExist):
        return JsonResponse({'error': 'Fecha o servicio inválido.'}, status=400)

    # --- Lógica de cálculo de disponibilidad ---
    
    # 1. Definir horario laboral (se podría hacer configurable en el futuro)
    work_start_time = time(9, 0)
    work_end_time = time(18, 0)
    
    # 2. Obtener citas ya agendadas para ese día
    barbershop = get_barbershop()
    booked_appointments = Appointment.objects.filter(barbershop=barbershop, date=date, status='pending')
    
    # 3. Generar todos los posibles slots de inicio en el horario laboral
    available_slots = []
    slot_start = datetime.combine(date, work_start_time)
    work_end_datetime = datetime.combine(date, work_end_time)
    service_duration = timedelta(minutes=service.duration_minutes)

    while (slot_start + service_duration) <= work_end_datetime:
        slot_end = slot_start + service_duration
        is_available = True
        
        # 4. Comprobar si el slot actual se solapa con alguna cita existente
        for app in booked_appointments:
            app_start = datetime.combine(date, app.time)
            app_end = app_start + timedelta(minutes=app.service.duration_minutes)
            
            # Condición de solapamiento: (StartA <= EndB) and (EndA >= StartB)
            if slot_start < app_end and slot_end > app_start:
                is_available = False
                break
        
        if is_available:
            available_slots.append(slot_start.strftime('%H:%M'))
            
        # Incrementar para el siguiente slot (ej. cada 30 min)
        slot_start += timedelta(minutes=30) 

    return JsonResponse({'available_slots': available_slots})


class BookingView(View):
    def get(self, request, service_id):
        service = get_object_or_404(Service, pk=service_id)
        context = {
            'service': service
        }
        return render(request, 'scheduling/booking_form.html', context)

    def post(self, request, service_id):
        service = get_object_or_404(Service, pk=service_id)
        barbershop = get_barbershop()

        # Recoger datos del formulario
        client_name = request.POST.get('name')
        client_phone = request.POST.get('phone')
        date_str = request.POST.get('date')
        time_str = request.POST.get('time')

        # Validación simple (se puede mejorar con un Django Form)
        if not all([client_name, client_phone, date_str, time_str]):
            # Manejar error
            return render(request, 'scheduling/booking_form.html', {'service': service, 'error': 'Todos los campos son obligatorios.'})

        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        time = datetime.strptime(time_str, '%H:%M').time()

        # Buscar o crear al cliente
        client, created = Client.objects.get_or_create(
            phone=client_phone,
            defaults={'name': client_name, 'barbershop': barbershop}
        )
        if not created and client.name != client_name:
            client.name = client_name # Actualizar nombre si es diferente
            client.save()

        # Crear la cita
        appointment = Appointment.objects.create(
            barbershop=barbershop,
            client=client,
            service=service,
            date=date,
            time=time,
            total_price=service.price,
            status='pending'
        )

        return redirect('public_booking_confirmation', pk=appointment.pk)

class BookingConfirmationView(View):
    def get(self, request, pk):
        appointment = get_object_or_404(Appointment, pk=pk)
        return render(request, 'scheduling/booking_confirmation.html', {'appointment': appointment})


