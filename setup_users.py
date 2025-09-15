
"""
Script para configurar usuarios y perfiles en el sistema Tu Solución
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tu_solucion.settings')
django.setup()

from django.contrib.auth.models import User
from catering.models import PerfilUsuario

def crear_perfil_admin():
    """Crear perfil para el usuario admin existente"""
    try:
        admin_user = User.objects.get(username='admin')
        if not hasattr(admin_user, 'perfilusuario'):
            PerfilUsuario.objects.create(
                usuario=admin_user,
                tipo_usuario='ADMIN',
                estado='ACTIVO',
                telefono='+54 9 11 1234-5678',
                direccion='Av. Principal 123, CABA'
            )
            print("✅ Perfil de administrador creado para usuario 'admin'")
        else:
            print("ℹ️  El usuario 'admin' ya tiene un perfil")
    except User.DoesNotExist:
        print("❌ Usuario 'admin' no encontrado")

def crear_usuarios_ejemplo():
    """Crear usuarios de ejemplo para diferentes roles"""
    usuarios_ejemplo = [
        {
            'username': 'empleado1',
            'email': 'empleado1@tusolucion.com',
            'first_name': 'María',
            'last_name': 'González',
            'tipo_usuario': 'EMPLEADO',
            'telefono': '+54 9 11 2345-6789',
            'direccion': 'Calle Empleado 456, CABA'
        },
        {
            'username': 'empleado2',
            'email': 'empleado2@tusolucion.com',
            'first_name': 'Carlos',
            'last_name': 'Rodríguez',
            'tipo_usuario': 'EMPLEADO',
            'telefono': '+54 9 11 3456-7890',
            'direccion': 'Av. Trabajador 789, CABA'
        },
        {
            'username': 'responsable1',
            'email': 'responsable1@tusolucion.com',
            'first_name': 'Ana',
            'last_name': 'López',
            'tipo_usuario': 'RESPONSABLE',
            'telefono': '+54 9 11 4567-8901',
            'direccion': 'Calle Responsable 321, CABA'
        },
        {
            'username': 'admin2',
            'email': 'admin2@tusolucion.com',
            'first_name': 'Roberto',
            'last_name': 'Martínez',
            'tipo_usuario': 'ADMIN',
            'telefono': '+54 9 11 5678-9012',
            'direccion': 'Av. Administrador 654, CABA'
        }
    ]
    
    for datos in usuarios_ejemplo:
        try:
            if not User.objects.filter(username=datos['username']).exists():

                user = User.objects.create_user(
                    username=datos['username'],
                    email=datos['email'],
                    password='TuSolucion2024!',
                    first_name=datos['first_name'],
                    last_name=datos['last_name'],
                    is_staff=datos['tipo_usuario'] in ['ADMIN', 'EMPLEADO']
                )

                PerfilUsuario.objects.create(
                    usuario=user,
                    tipo_usuario=datos['tipo_usuario'],
                    estado='ACTIVO',
                    telefono=datos['telefono'],
                    direccion=datos['direccion']
                )
                
                print(f"✅ Usuario '{datos['username']}' creado como {datos['tipo_usuario']}")
            else:
                print(f"ℹ️  Usuario '{datos['username']}' ya existe")
        except Exception as e:
            print(f"❌ Error creando usuario '{datos['username']}': {e}")

def mostrar_usuarios():
    """Mostrar todos los usuarios y sus perfiles"""
    print("\n📋 USUARIOS EN EL SISTEMA:")
    print("-" * 80)
    
    for user in User.objects.all().order_by('username'):
        try:
            perfil = user.perfilusuario
            estado_color = "🟢" if perfil.estado == 'ACTIVO' else "🔴"
            tipo_icon = {
                'ADMIN': '👑',
                'EMPLEADO': '👷',
                'RESPONSABLE': '👨‍💼',
                'CLIENTE': '👤'
            }.get(perfil.tipo_usuario, '❓')
            
            print(f"{tipo_icon} {user.username:<15} | {user.get_full_name():<25} | {perfil.get_tipo_usuario_display():<12} | {estado_color} {perfil.get_estado_display()}")
        except:
            print(f"❓ {user.username:<15} | {user.get_full_name():<25} | Sin perfil{'':<12} | ⚠️  Sin perfil")

def main():
    print("🚀 Configurando usuarios para Tu Solución")
    print("=" * 50)

    crear_perfil_admin()

    print("\n👥 Creando usuarios de ejemplo...")
    crear_usuarios_ejemplo()

    mostrar_usuarios()
    
    print("\n" + "=" * 50)
    print("✅ Configuración completada!")
    print("\n🔑 CREDENCIALES DE ACCESO:")
    print("   Usuario: admin")
    print("   Contraseña: (la que configuraste al crear el superusuario)")
    print("\n👥 USUARIOS DE EJEMPLO:")
    print("   empleado1 / TuSolucion2024!")
    print("   empleado2 / TuSolucion2024!")
    print("   responsable1 / TuSolucion2024!")
    print("   admin2 / TuSolucion2024!")
    print("\n🌐 Accede al admin en: http://localhost:8000/admin/")

if __name__ == '__main__':
    main()
