from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class BarberShop(models.Model):
    """
    Representa una barbería en el sistema.
    En un modelo multi-tenant, este sería el modelo principal de anclaje.
    """
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="barbershops")
    name = models.CharField(max_length=100)
    # Futuro campo para manejar suscripciones (ej: 'free', 'basic', 'premium')
    subscription_plan = models.CharField(max_length=50, default='free')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Service(models.Model):
    """
    Servicios ofrecidos por una barbería específica.
    """
    barbershop = models.ForeignKey(BarberShop, on_delete=models.CASCADE, related_name="services")
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_minutes = models.PositiveIntegerField(help_text="Duración del servicio en minutos")

    def __str__(self):
        return f"{self.name} - {self.barbershop.name}"

class Client(models.Model):
    """
    Clientes de una barbería. Un cliente pertenece a una sola barbería
    para mantener los datos aislados.
    """
    barbershop = models.ForeignKey(BarberShop, on_delete=models.CASCADE, related_name="clients")
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, unique=True, blank=True, null=True)
    nickname = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.phone})"

class Appointment(models.Model):
    """
    Citas agendadas en una barbería.
    """
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('completed', 'Completada'),
        ('cancelled', 'Cancelada'),
    ]

    barbershop = models.ForeignKey(BarberShop, on_delete=models.CASCADE, related_name="appointments")
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="appointments")
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, related_name="appointments")
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    # total_price se podría calcular al momento de crear, pero almacenarlo
    # ofrece flexibilidad si los precios de los servicios cambian en el futuro.
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Evita que se pueda agendar más de una cita para la misma barbería a la misma fecha y hora.
        unique_together = ('barbershop', 'date', 'time')

    def __str__(self):
        return f"Cita de {self.client.name} el {self.date} a las {self.time}"
