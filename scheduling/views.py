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

