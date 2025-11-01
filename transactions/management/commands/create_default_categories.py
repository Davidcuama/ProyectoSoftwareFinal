"""
Comando de management para crear categorías por defecto para usuarios existentes.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from transactions.utils import create_default_categories


class Command(BaseCommand):
    help = 'Crea categorías por defecto para todos los usuarios que aún no las tienen'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=str,
            help='Nombre de usuario específico para crear categorías (opcional)',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Crear categorías para todos los usuarios',
        )

    def handle(self, *args, **options):
        if options['user']:
            try:
                user = User.objects.get(username=options['user'])
                self.create_categories_for_user(user)
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Usuario "{options["user"]}" no encontrado.')
                )
        elif options['all']:
            users = User.objects.all()
            count = 0
            for user in users:
                if self.create_categories_for_user(user):
                    count += 1
            self.stdout.write(
                self.style.SUCCESS(f'Categorías creadas para {count} usuarios.')
            )
        else:
            # Por defecto, crear para usuarios sin categorías
            users_without_categories = User.objects.filter(categories__isnull=True).distinct()
            count = 0
            for user in users_without_categories:
                if self.create_categories_for_user(user):
                    count += 1
            self.stdout.write(
                self.style.SUCCESS(f'Categorías creadas para {count} usuarios sin categorías.')
            )

    def create_categories_for_user(self, user):
        """Crea categorías por defecto para un usuario si no las tiene."""
        from transactions.models import Category
        
        # Verificar si el usuario ya tiene categorías
        if Category.objects.filter(user=user).exists():
            self.stdout.write(
                self.style.WARNING(f'El usuario "{user.username}" ya tiene categorías. Omitiendo...')
            )
            return False
        
        try:
            create_default_categories(user)
            self.stdout.write(
                self.style.SUCCESS(f'Categorías creadas para "{user.username}"')
            )
            return True
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creando categorías para "{user.username}": {e}')
            )
            return False

