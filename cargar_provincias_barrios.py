#!/usr/bin/env python
"""
Script para cargar datos de provincias y barrios de Córdoba
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tu_solucion.settings')
django.setup()

from catering.models import Provincia, Barrio

def cargar_provincias():
    """Cargar provincias de Argentina"""
    provincias_data = [
        {'nombre': 'Córdoba', 'codigo': 'COR'},
        {'nombre': 'Buenos Aires', 'codigo': 'BA'},
        {'nombre': 'Santa Fe', 'codigo': 'SF'},
        {'nombre': 'Mendoza', 'codigo': 'MEN'},
        {'nombre': 'Tucumán', 'codigo': 'TUC'},
        {'nombre': 'Salta', 'codigo': 'SAL'},
        {'nombre': 'Entre Ríos', 'codigo': 'ER'},
        {'nombre': 'Misiones', 'codigo': 'MIS'},
        {'nombre': 'Corrientes', 'codigo': 'CORR'},
        {'nombre': 'Chaco', 'codigo': 'CHA'},
        {'nombre': 'Santiago del Estero', 'codigo': 'SDE'},
        {'nombre': 'San Juan', 'codigo': 'SJ'},
        {'nombre': 'Jujuy', 'codigo': 'JUJ'},
        {'nombre': 'Río Negro', 'codigo': 'RN'},
        {'nombre': 'Formosa', 'codigo': 'FOR'},
        {'nombre': 'Neuquén', 'codigo': 'NEU'},
        {'nombre': 'Chubut', 'codigo': 'CHU'},
        {'nombre': 'San Luis', 'codigo': 'SL'},
        {'nombre': 'Catamarca', 'codigo': 'CAT'},
        {'nombre': 'La Rioja', 'codigo': 'LR'},
        {'nombre': 'La Pampa', 'codigo': 'LP'},
        {'nombre': 'Santa Cruz', 'codigo': 'SC'},
        {'nombre': 'Tierra del Fuego', 'codigo': 'TF'},
    ]
    
    for provincia_data in provincias_data:
        try:
            provincia, created = Provincia.objects.get_or_create(
                codigo=provincia_data['codigo'],
                defaults={
                    'nombre': provincia_data['nombre'],
                    'activa': True
                }
            )
            if created:
                print(f"✅ Provincia creada: {provincia.nombre}")
            else:
                print(f"ℹ️  Provincia ya existe: {provincia.nombre}")
        except Exception as e:
            print(f"⚠️  Error con provincia {provincia_data['nombre']}: {e}")
            # Intentar crear solo por nombre si falla por código
            try:
                provincia, created = Provincia.objects.get_or_create(
                    nombre=provincia_data['nombre'],
                    defaults={
                        'codigo': provincia_data['codigo'],
                        'activa': True
                    }
                )
                if created:
                    print(f"✅ Provincia creada (por nombre): {provincia.nombre}")
                else:
                    print(f"ℹ️  Provincia ya existe (por nombre): {provincia.nombre}")
            except Exception as e2:
                print(f"❌ Error definitivo con provincia {provincia_data['nombre']}: {e2}")

def cargar_barrios_cordoba():
    """Cargar barrios de Córdoba Capital"""
    try:
        provincia_cordoba = Provincia.objects.get(codigo='COR')
    except Provincia.DoesNotExist:
        print("❌ Error: Provincia Córdoba no encontrada")
        return
    
    barrios_data = [
        'Centro', 'Nueva Córdoba', 'Güemes', 'San Martín', 'Alberdi',
        'Villa Allende', 'Villa Belgrano', 'Villa Carlos Paz', 'Villa Dolores',
        'Villa General Belgrano', 'Villa María', 'Villa Mercedes',
        'Alta Córdoba', 'Barrio Jardín', 'Barrio Norte', 'Barrio Sur',
        'Cofico', 'Colón', 'Córdoba', 'Cruz del Eje', 'General Paz',
        'Jardín', 'La Calera', 'La Falda', 'La Plata', 'Los Boulevares',
        'Maldonado', 'Mariquita Sánchez', 'Mercado Norte', 'Mercado Sur',
        'Nueva Esperanza', 'Nueva Italia', 'Observatorio', 'Paso de los Libres',
        'Pilar', 'Pueyrredón', 'Residencial San Martín', 'Río Cuarto',
        'Río Segundo', 'San Antonio', 'San Fernando', 'San Francisco',
        'San Isidro', 'San Jerónimo', 'San José', 'San Martín',
        'San Nicolás', 'San Pedro', 'San Rafael', 'San Roque',
        'San Vicente', 'Santa Ana', 'Santa Fe', 'Santa Isabel',
        'Santa Lucía', 'Santa María', 'Santa Rosa', 'Sarmiento',
        'Sierras de Córdoba', 'Tablada', 'Tiro Federal', 'Villa Azalais',
        'Villa Bustos', 'Villa Cárcano', 'Villa Clodomiro', 'Villa del Totoral',
        'Villa El Libertador', 'Villa Elisa', 'Villa Esquiú', 'Villa Fontana',
        'Villa Libertador San Martín', 'Villa María', 'Villa Mercedes',
        'Villa Mitre', 'Villa Nueva', 'Villa Parque', 'Villa Quilino',
        'Villa Rivera Indarte', 'Villa San Antonio', 'Villa San Martín',
        'Villa Santa Isabel', 'Villa Santa Rosa', 'Villa Taninga',
        'Villa Tulumba', 'Villa Valeria', 'Villa Yacanto', 'Yapeyú'
    ]
    
    for barrio_nombre in barrios_data:
        barrio, created = Barrio.objects.get_or_create(
            nombre=barrio_nombre,
            provincia=provincia_cordoba,
            defaults={
                'activo': True
            }
        )
        if created:
            print(f"✅ Barrio creado: {barrio.nombre}, {barrio.provincia.nombre}")
        else:
            print(f"ℹ️  Barrio ya existe: {barrio.nombre}, {barrio.provincia.nombre}")

def cargar_barrios_buenos_aires():
    """Cargar algunos barrios de Buenos Aires"""
    try:
        provincia_ba = Provincia.objects.get(codigo='BA')
    except Provincia.DoesNotExist:
        print("❌ Error: Provincia Buenos Aires no encontrada")
        return
    
    barrios_data = [
        'Capital Federal', 'La Plata', 'Mar del Plata', 'Bahía Blanca',
        'Tandil', 'Olavarría', 'Necochea', 'Junín', 'Azul', 'Pergamino',
        'Chivilcoy', 'Mercedes', 'Luján', 'San Nicolás', 'Zárate',
        'Campana', 'Escobar', 'Pilar', 'Tigre', 'San Isidro',
        'Vicente López', 'San Martín', 'Tres de Febrero', 'Hurlingham',
        'Ituzaingó', 'Morón', 'La Matanza', 'Lomas de Zamora',
        'Avellaneda', 'Lanús', 'Quilmes', 'Berazategui', 'Florencio Varela'
    ]
    
    for barrio_nombre in barrios_data:
        barrio, created = Barrio.objects.get_or_create(
            nombre=barrio_nombre,
            provincia=provincia_ba,
            defaults={
                'activo': True
            }
        )
        if created:
            print(f"✅ Barrio creado: {barrio.nombre}, {barrio.provincia.nombre}")
        else:
            print(f"ℹ️  Barrio ya existe: {barrio.nombre}, {barrio.provincia.nombre}")

def main():
    """Función principal"""
    print("🚀 Iniciando carga de provincias y barrios...")
    print("=" * 50)
    
    print("\n📍 Cargando provincias...")
    cargar_provincias()
    
    print("\n🏘️  Cargando barrios de Córdoba...")
    cargar_barrios_cordoba()
    
    print("\n🏘️  Cargando barrios de Buenos Aires...")
    cargar_barrios_buenos_aires()
    
    print("\n" + "=" * 50)
    print("✅ Carga completada!")
    
    # Mostrar estadísticas
    total_provincias = Provincia.objects.count()
    total_barrios = Barrio.objects.count()
    print(f"📊 Total de provincias: {total_provincias}")
    print(f"📊 Total de barrios: {total_barrios}")

if __name__ == '__main__':
    main()
