from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from catering.forms import RegistroForm
from catering.models import Provincia, Barrio, Cliente, PerfilUsuario
from django.test import RequestFactory
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware
from django.utils import timezone

class Command(BaseCommand):
    help = 'Probar el formulario de registro final'

    def handle(self, *args, **options):
        self.stdout.write('🔍 Probando formulario de registro final...')

        cordoba = Provincia.objects.get(nombre='Córdoba')
        centro = Barrio.objects.get(nombre='Centro', provincia=cordoba)

        factory = RequestFactory()
        request = factory.post('/registro/', {
            'username': 'test_registro_final',
            'email': 'testfinal@example.com',
            'password1': 'testpassword123',
            'password2': 'testpassword123',
            'nombre': 'Test',
            'apellido': 'Final',
            'tipo_doc': 'DNI',
            'num_doc': '44444444',
            'domicilio': 'Calle Test 123, Centro, Córdoba',
            'provincia': str(cordoba.id_provincia),
            'barrio': str(centro.id_barrio)
        })

        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()

        messages_middleware = MessageMiddleware(lambda req: None)
        messages_middleware.process_request(request)

        if request.method == 'POST':
            form = RegistroForm(request.POST)
            self.stdout.write(f'Formulario creado con POST data')
            self.stdout.write(f'Formulario válido: {form.is_valid()}')
            
            if not form.is_valid():
                self.stdout.write('\n❌ Errores en el formulario:')
                for field, errors in form.errors.items():
                    self.stdout.write(f'  {field}: {errors}')
            else:
                self.stdout.write('\n✅ Formulario válido - creando usuario...')
                
                try:

                    user = User.objects.create_user(
                        username=form.cleaned_data['username'],
                        email=form.cleaned_data['email'],
                        password=form.cleaned_data['password1'],
                        first_name=form.cleaned_data['nombre'],
                        last_name=form.cleaned_data['apellido']
                    )
                    self.stdout.write('✅ Usuario creado')

                    PerfilUsuario.objects.create(
                        usuario=user,
                        tipo_usuario='CLIENTE'
                    )
                    self.stdout.write('✅ Perfil creado')

                    cliente = Cliente.objects.create(
                        nombre=form.cleaned_data['nombre'],
                        apellido=form.cleaned_data['apellido'],
                        tipo_doc=form.cleaned_data['tipo_doc'],
                        num_doc=form.cleaned_data['num_doc'],
                        email=form.cleaned_data['email'],
                        domicilio=form.cleaned_data['domicilio'],
                        provincia=form.cleaned_data.get('provincia'),
                        barrio=form.cleaned_data.get('barrio'),
                        fecha_alta=timezone.now().date(),
                        usuario=user
                    )
                    self.stdout.write('✅ Cliente creado')
                    
                    self.stdout.write(f'\n🎉 Registro exitoso!')
                    self.stdout.write(f'  Usuario: {user.username}')
                    self.stdout.write(f'  Cliente: {cliente}')
                    self.stdout.write(f'  Domicilio: {cliente.domicilio}')

                    user.delete()
                    
                except Exception as e:
                    self.stdout.write(f'\n❌ Error al crear usuario: {str(e)}')
                    import traceback
                    traceback.print_exc()
        else:
            form = RegistroForm()
            self.stdout.write('Formulario creado sin datos POST')
        
        self.stdout.write('\n✅ Prueba de registro completada')
