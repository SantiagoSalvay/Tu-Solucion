from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from catering.models import Responsable, Personal, Cliente, PerfilUsuario
from django.db import transaction

class Command(BaseCommand):
    help = 'Crear usuarios iniciales para responsables, personal y clientes'

    def handle(self, *args, **options):
        with transaction.atomic():

            if not User.objects.filter(username='admin').exists():
                admin_user = User.objects.create_superuser(
                    username='admin',
                    email='admin@tusolucion.com',
                    password='admin123',
                    first_name='Administrador',
                    last_name='Sistema'
                )

                PerfilUsuario.objects.create(
                    usuario=admin_user,
                    tipo_usuario='ADMIN'
                )
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Superusuario admin creado (password: admin123)')
                )

            responsables = Responsable.objects.all()
            for responsable in responsables:
                if not User.objects.filter(email=responsable.email).exists():
                    username = responsable.email.split('@')[0]
                    user = User.objects.create_user(
                        username=username,
                        email=responsable.email,
                        password='responsable123',
                        first_name=responsable.nombre_apellido.split()[0],
                        last_name=' '.join(responsable.nombre_apellido.split()[1:]) if len(responsable.nombre_apellido.split()) > 1 else ''
                    )

                    PerfilUsuario.objects.create(
                        usuario=user,
                        tipo_usuario='RESPONSABLE'
                    )
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ Usuario responsable creado: {username} (password: responsable123)')
                    )

            personal_list = Personal.objects.all()
            for personal in personal_list:
                if not User.objects.filter(email=personal.email).exists():
                    username = personal.email.split('@')[0]
                    user = User.objects.create_user(
                        username=username,
                        email=personal.email,
                        password='empleado123',
                        first_name=personal.nombre_y_apellido.split()[0],
                        last_name=' '.join(personal.nombre_y_apellido.split()[1:]) if len(personal.nombre_y_apellido.split()) > 1 else ''
                    )

                    PerfilUsuario.objects.create(
                        usuario=user,
                        tipo_usuario='EMPLEADO'
                    )
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ Usuario empleado creado: {username} (password: empleado123)')
                    )

            clientes = Cliente.objects.all()
            for cliente in clientes:
                if not User.objects.filter(email=cliente.email).exists():
                    username = f"cliente_{cliente.num_doc}"
                    user = User.objects.create_user(
                        username=username,
                        email=cliente.email,
                        password=f"cliente{cliente.num_doc}",
                        first_name=cliente.nombre,
                        last_name=cliente.apellido
                    )

                    PerfilUsuario.objects.create(
                        usuario=user,
                        tipo_usuario='CLIENTE'
                    )

                    cliente.usuario = user
                    cliente.save()
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ Usuario cliente creado: {username} (password: cliente{cliente.num_doc})')
                    )

        self.stdout.write(
            self.style.SUCCESS('\n🎉 Todos los usuarios iniciales han sido creados exitosamente!')
        )
        self.stdout.write(
            self.style.WARNING('\n📋 Credenciales por defecto:')
        )
        self.stdout.write('   • Admin: admin / admin123')
        self.stdout.write('   • Responsables: [email] / responsable123')
        self.stdout.write('   • Empleados: [email] / empleado123')
        self.stdout.write('   • Clientes: cliente_[dni] / cliente[dni]')
