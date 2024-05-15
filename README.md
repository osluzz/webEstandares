**README**

Este documento describe la estructura y funcionalidad del sitio web **Aplicaciones libres para Windows**, que ofrece una selección de software de código abierto para diversas disciplinas, como matemáticas, ciencias e ingenierías.

**Estructura del Sitio**

El sitio está estructurado en diferentes secciones accesibles desde el menú lateral izquierdo:

  • **Principal**: Página de inicio del sitio.
  
  • **Aplicaciones**: Listado de aplicaciones disponibles, organizadas por categorías.
  
  • **Manuales**: Recursos de ayuda y manuales de uso para las aplicaciones.

**Categorías de Aplicaciones**

Las aplicaciones se agrupan en las siguientes categorías:

  • **Internet**
    
  • **Oficina**
  
  • **Utilidades**
    
  • **Multimedia**
    
  • **Científico**

**Acceso y Descarga**

Cada aplicación cuenta con un enlace de descarga directa y botones adicionales para obtener más información y acceder a manuales de uso.

**Actualizador de Versiones de Software**

Con la intención de mantener el repositorio de aplicaciones actualizado hemos desarrollado ste script de Python que está diseñado para automatizar la descarga de instaladores de versiones de software en un repositorio web y en archivos HTML. Permite buscar, descargar y actualizar la información de la última versión de una lista predefinida de software. El script se encuentra en la carpeta “scripts” y se llama descarga.py.

**Requisitos**

  • Python 3.x
    
  • Bibliotecas Python: requests, beautifulsoup4, wget


**Configuración**

  1. **Instalar bibliotecas Python**: Asegúrate de tener las bibliotecas necesarias instaladas. Puedes instalarlas utilizando pip:
    
       pip install requests beautifulsoup4 wget
    
  2. **Editar la lista de descargas**: En el script, hay una lista llamada descargas que contiene información sobre el software que se actualizará. Cada entrada en esta lista incluye la URL de descarga, el nombre del software, filtros HTML (si es necesario), patrones de expresiones regulares para extraer la versión, entre otros detalles.
    
  3. **Configurar la ruta de destino**: Ajusta la ruta donde se guardarán los archivos descargados y los archivos HTML que se actualizarán.
    
  4. **Configurar el registro**: El script registra su actividad en un archivo de registro. Asegúrate de configurar la ruta del archivo de registro en la sección de configuración del script.

**Uso**

Ejecuta el script descarga.py. El script buscará la última versión disponible para cada software en la lista y la descargará si es necesario. Luego, actualizará los archivos HTML asociados con la información de la versión descargada.

**Funcionamiento**

  1. **Obtención de enlaces de descarga**: El script busca en las páginas web especificadas los enlaces de descarga del software.
    
  2. **Descarga de archivos**: Si se encuentra una nueva versión, el script descarga el archivo correspondiente.
    
  3. **Actualización de archivos HTML**: El script busca y actualiza los archivos HTML asociados con la información de la versión descargada.

**Consideraciones**

  • Es importante mantener actualizada la lista de descargas con la información correcta sobre cada software.
    
  • Se recomienda ejecutar este script periódicamente para mantener actualizado el repositorio de software y los archivos HTML. Para ello se puede configurar Cron.

**Notas**

  • Este script puede requerir ajustes adicionales según los requisitos específicos del entorno y las fuentes de descarga de software.
    
  • Se recomienda probar el script en un entorno de prueba antes de implementarlo en producción.

**Créditos**

El sitio es gestionado por la Oficina de Software Libre de la Universidad de Zaragoza.

Fecha de creación: Mayo de 2024

Licencia: CC0 1.0 Universal.

Para más información, visita [OSLUZ - Oficina de Software Libre de la Universidad de Zaragoza](https://osluz.unizar.es/)
