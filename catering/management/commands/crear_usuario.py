from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from catering.models import PerfilUsuario
import getpass

class Command(BaseCommand):
    help = 'Crea un nuevo usuario con perfil personalizado'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Nombre de usuario')
        parser.add_argument('--email', type=str, help='Email del usuario')
        parser.add_argument('--first_name', type=str, help='Nombre')
        parser.add_argument('--last_name', type=str, help='Apellido')
        parser.add_argument('--tipo', type=str, choices=['ADMIN', 'EMPLEADO', 'RESPONSABLE', 'CLIENTE'], 
                          default='EMPLEADO', help='Tipo de usuario')
        parser.add_argument('--superuser', action='store_true', help='Crear como superusuario')
        parser.add_argument('--staff', action='store_true', help='Crear como staff')

    def handle(self, *args, **options):
        try:

            username = options['username']
            if not username:
                username = input('Nombre de usuario: ').strip()
            
            if User.objects.filter(username=username).exists():
                raise CommandError(f'El usuario "{username}" ya existe.')
            
            email = options['email']
            if not email:
                email = input('Email: ').strip()
            
            first_name = options['first_name']
            if not first_name:
                first_name = input('Nombre: ').strip()
            
            last_name = options['last_name']
            if not last_name:
                last_name = input('Apellido: ').strip()
            
            tipo_usuario = options['tipo']
            is_superuser = options['superuser']
            is_staff = options['staff']

            password = getpass.getpass('Contraseña: ')
            password_confirm = getpass.getpass('Confirmar contraseña: ')
            
            if password != password_confirm:
                raise CommandError('Las contraseñas no coinciden.')
            
            if len(password) < 8:
                raise CommandError('La contraseña debe tener al menos 8 caracteres.')

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                is_superuser=is_superuser,
                is_staff=is_staff or is_superuser
            )

            perfil = PerfilUsuario.objects.create(
                usuario=user,
                tipo_usuario=tipo_usuario,
                estado='ACTIVO'
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Usuario "{username}" creado exitosamente como {perfil.get_tipo_usuario_display()}'
                )
            )
            
            if is_superuser:
                self.stdout.write(
                    self.style.WARNING('⚠️  Usuario creado como SUPERUSUARIO')
                )
            
        except KeyboardInterrupt:
            self.stdout.write(self.style.ERROR('\nOperación cancelada por el usuario.'))
        except Exception as e:
            raise CommandError(f'Error al crear usuario: {str(e)}')
