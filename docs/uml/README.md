# Diagramas UML - Sistema de Gestión de Catering

Este directorio contiene los diagramas UML del sistema "Tu Solución" de gestión de catering.

## Archivos de Diagramas

### 1. `class_diagram.mmd` - Diagrama de Clases
**Descripción**: Muestra la estructura de clases del sistema y sus relaciones.

**Contenido**:
- Todas las entidades del sistema (Cliente, Evento, Menú, etc.)
- Atributos y métodos de cada clase
- Relaciones entre clases (herencia, asociación, composición)
- Notas explicativas para clases principales

**Uso**: Visualizar la arquitectura del sistema y las relaciones entre entidades.

### 2. `reserva_sequence.mmd` - Diagrama de Secuencia
**Descripción**: Ilustra el flujo de la transacción principal (reserva de catering).

**Contenido**:
- Interacción entre actores (Cliente, Responsable, Sistema)
- Flujo completo de reserva desde la solicitud hasta la generación del comprobante
- Verificación de disponibilidad
- Armado del menú
- Cálculo de precios

**Uso**: Entender el proceso de negocio principal del sistema.

### 3. `use_case_diagram.mmd` - Diagrama de Casos de Uso
**Descripción**: Muestra todos los casos de uso del sistema y los actores involucrados.

**Contenido**:
- Actores del sistema (Cliente, Responsable, Cobro, Compras, Admin)
- Casos de uso organizados por módulos
- Relaciones entre actores y casos de uso
- Relaciones de inclusión entre casos de uso

**Uso**: Comprender las funcionalidades del sistema desde la perspectiva del usuario.

## Cómo Visualizar los Diagramas

### Opción 1: Mermaid Live Editor
1. Ir a https://mermaid.live/
2. Copiar el contenido del archivo `.mmd`
3. Pegar en el editor
4. El diagrama se renderizará automáticamente

### Opción 2: Extensiones de VS Code
- Instalar la extensión "Mermaid Preview"
- Abrir el archivo `.mmd`
- Usar Ctrl+Shift+P y seleccionar "Mermaid Preview"

### Opción 3: GitHub
- Los archivos `.mmd` se renderizan automáticamente en GitHub
- Subir los archivos al repositorio para visualizarlos

## Convenciones Utilizadas

### Diagrama de Clases
- `+` : Atributo/método público
- `-` : Atributo/método privado
- `||--o{` : Relación uno a muchos
- `||--||` : Relación uno a uno

### Diagrama de Secuencia
- Participantes claramente identificados
- Flujo temporal de izquierda a derecha
- Notas explicativas para pasos complejos
- Alternativas (alt) para decisiones

### Diagrama de Casos de Uso
- Actores representados como figuras humanas
- Casos de uso como elipses
- Relaciones de asociación con líneas continuas
- Relaciones de inclusión con líneas punteadas

## Mantenimiento

### Actualizar Diagramas
1. Modificar el archivo `.mmd` correspondiente
2. Verificar la sintaxis en Mermaid Live Editor
3. Actualizar esta documentación si es necesario
4. Commitear los cambios al repositorio

### Agregar Nuevos Diagramas
1. Crear el archivo `.mmd` con sintaxis Mermaid
2. Agregar la descripción en este README
3. Verificar que se renderice correctamente
4. Documentar el propósito y uso del diagrama

## Notas Técnicas

- **Formato**: Todos los diagramas están en formato Mermaid (`.mmd`)
- **Compatibilidad**: Mermaid es compatible con GitHub, GitLab, y muchas herramientas de documentación
- **Sintaxis**: Verificar la sintaxis en https://mermaid.live/ antes de commitear
- **Versionado**: Los diagramas deben actualizarse cuando cambie la estructura del sistema

---

**Sistema de Gestión de Catering - Tu Solución**
*Documentación UML - Versión 1.0*
