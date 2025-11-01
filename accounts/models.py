from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """
    Modelo extendido para el perfil de usuario con roles.
    """
    ROLE_CHOICES = [
        ('user', 'Usuario'),
        ('admin', 'Administrador'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(
        max_length=10, 
        choices=ROLE_CHOICES, 
        default='user',
        verbose_name="Rol"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")
    
    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuario"
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"
    
    @property
    def is_admin(self):
        """Retorna True si el usuario es administrador."""
        return self.role == 'admin'
    
    @property
    def is_user(self):
        """Retorna True si el usuario es usuario normal."""
        return self.role == 'user'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Crea automáticamente un perfil y categorías por defecto cuando se crea un usuario.
    """
    if created:
        UserProfile.objects.create(user=instance)
        
        # Crear categorías por defecto para el nuevo usuario
        try:
            from transactions.utils import create_default_categories
            create_default_categories(instance)
        except Exception as e:
            # Si hay algún error, solo lo registramos pero no fallamos el registro
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"No se pudieron crear categorías por defecto para {instance.username}: {e}")


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Guarda el perfil cuando se guarda el usuario.
    """
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        UserProfile.objects.create(user=instance)
