from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from catering.models import Cliente, Responsable, Comprobante, EventoSolicitado
from django.utils import timezone
from datetime import date, time

class Command(BaseCommand):
    help = 'Probar la creación de eventos'

    def handle(self, *args, **options):
        self.stdout.write('🔍 Probando creación de eventos...')
        
        try:

            cliente = Cliente.objects.first()
            responsable = Responsable.objects.first()
            
            if not cliente:
                self.stdout.write('❌ No hay clientes en la base de datos')
                return
            
            if not responsable:
                self.stdout.write('❌ No hay responsables en la base de datos')
                return
            
            self.stdout.write(f'✅ Cliente encontrado: {cliente}')
            self.stdout.write(f'✅ Responsable encontrado: {responsable}')

            comprobante = Comprobante.objects.create(
                id_cliente=cliente,
                fecha_pedido=timezone.now().date(),
                importe_total_productos=0.00,
                total_servicio=0.00,
                precio_x_persona=0.00,
                fecha_vigencia=date.today()
            )
            
            self.stdout.write(f'✅ Comprobante creado: {comprobante}')

            evento = EventoSolicitado.objects.create(
                id_cliente=cliente,
                id_responsable=responsable,
                id_comprobante=comprobante,
                tipo_evento='CUMPLEAÑOS',
                fecha=date.today(),
                hora=time(18, 0),
                ubicacion='Calle Test 123, Centro, Córdoba',
                cantidad_personas=20,
                estado='SOLICITADO'
            )
            
            self.stdout.write(f'✅ Evento creado: {evento}')
            self.stdout.write(f'✅ Evento ID: {evento.id_evento}')
            self.stdout.write(f'✅ Comprobante ID: {evento.id_comprobante.id_comprobante}')

            evento.delete()
            comprobante.delete()
            
            self.stdout.write('✅ Prueba exitosa - datos limpiados')
            
        except Exception as e:
            self.stdout.write(f'❌ Error: {str(e)}')
            import traceback
            traceback.print_exc()
        
        self.stdout.write('\n✅ Prueba completada')
