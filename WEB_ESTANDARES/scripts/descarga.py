from urllib.parse import unquote, urljoin
# Importar módulos necesarios para la manipulación de html", "solicitudes HTTP, expresiones regulares,
# descargas de archivos y manipulación de archivos y tiempo.
import io
import requests
from bs4 import BeautifulSoup
import re
import wget
import os
import logging
import datetime
# Configurar el nivel de logs y el formato
logging.basicConfig(
    filename='/var/log/estandares.log', 
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
    )
# Obtener la fecha actual
current_date = datetime.datetime.now().strftime("%d-%m-%Y")

# Mensaje de encabezado con la fecha actual
header = f"=== Ejecucion Actualizador {current_date} ==="

# Agregar el encabezado al archivo de log
with open('/var/log/estandares.log', 'a') as f:
    f.write(header + '\n')

# Función para obtener la versión del archivo utilizando una expresión regular
def obtener_version(pattern, filename):
    match = re.search(pattern, filename)
    if match:
        return match.group(0)
    return None

# Funcion para obtener el enlace de descarga de una url, en la que buscaremos el link mediante un filtro.
# Si lo encuentra lo devolvera 
def obtener_enlace_descarga(url, filtro):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (Khtml", "like Gecko) Chrome/123.0.0.0 Safari/537.36',
        # Agrega más encabezados según sea necesario
    }
    try:
        # Realiza la solicitud HTTP con los encabezados personalizados
        response = requests.get(url, headers=headers)
        html_content = response.content
        soup = BeautifulSoup(html_content, 'html.parser')
        # dentro del codigo html buscaremos los elementos 'a', filtrando por el contenido de su href
        link = soup.find('a', **filtro)
        # si encuentra un elemento lo montaremos si hace falta para obtener una url valida
        if link:
            href = link['href']

            if href.startswith('//'):
                # Agregar el esquema 'https:' a la URL
                href = 'https:' + href
            elif href.startswith('/'):
                # Concatenar el dominio original con la URL que comienza con '/'
                base_url = response.url.split('//')[0] + '//' + response.url.split('//')[1].split('/')[0]
                href = urljoin(base_url, href)
            else:
                # Añadir barra diagonal al principio y luego unir con la url
                href = urljoin(url + '/', href)
            return href
    except (requests.RequestException, ValueError, KeyError) as e:
        print(f"Error al obtener el enlace de descarga: {e}")
        logging.error(f"Error al obtener el enlace de descarga: {e}")
        return None

#Funcion para buscar la ultima version dentro de la url ejemplo /blender x.x,
def encontrar_version_mas_alta(url, filtro, pattern, simbolo):
    # Realizar la solicitud HTTP
    response = requests.get(url)
    html_content = response.content
    # Crear el objeto BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    # Encontrar todos los enlaces que coinciden con el filtro
    enlaces = soup.find_all('a', **filtro)
    # Inicializar la variable para almacenar la versión más alta encontrada
    version_mayor = None
    # Inicializar la variable para almacenar la parte diferente del enlace con la versión mayor
    parte_diferente = None
    # Recorrer todos los enlaces y encontrar la versión más alta
    for enlace in enlaces:
        # Extraer el número de versión del enlace
        match = re.search(pattern, enlace['href'])
        if match:
            version = match.group(1)
            # Verificar si esta versión es mayor que la versión previamente encontrada
            if version_mayor is None or comparar_versiones(version, version_mayor, simbolo) > 0:
                version_mayor = version
                # Calcular la parte diferente del enlace con la versión mayor
                #parte_diferente = re.sub(pattern, "", enlace['href'])
                parte_igual = enlace['href']
                url_entera = urljoin(url, parte_igual)
                parte_diferente = url_entera.replace(url, "", 1)if url_entera else None
    return  parte_diferente

def comparar_versiones(version1, version2, simbolo):

    if simbolo:
        partes_version1 = version1.split(simbolo)
        partes_version2 = version2.split(simbolo)
    else:
        partes_version1 = version1
        partes_version2 = version2
    for i in range(len(partes_version1)):
        if int(partes_version1[i]) < int(partes_version2[i]):
            return -1
        elif int(partes_version1[i]) > int(partes_version2[i]):
            return 1
    return 0

# Función para buscar un archivo existente para reemplazar si no encuentra version antigua devuelve 'primera descarga'
def buscar_archivo_a_reemplazar(version_descargada, nombre, simbolo):  
    for filename in os.listdir('/srv/repositorios/estandares/aplicacion/'):
        if filename.startswith(nombre):
            version_existente = obtener_version(pattern, filename)
            if version_existente and version_descargada:
                if comparar_versiones(version_existente, version_descargada, simbolo):
                    return filename
                else:
                    return None
    return 'primera descarga'

#funcion para modificar los link y el texto de la version en los htmls indicados.
#Le pasamos un array de htmls el enlace y la version que modificaremos en los htmls ademas de el nombre de la aplicacion
#para indicar el id de los elementos a buscar
def modificar_htmls(html_files, enlace, version, aplicacion):
    for index, html_file in enumerate(html_files):
        # Construir la ruta adecuada dependiendo del índice
        if index == 0:
            ruta = "/srv/repositorios/webnueva/aplicacion/" + html_file
        else:
            ruta = "/srv/repositorios/webnueva/aplicaciones/" + html_file

         # Abrir el archivo HTML y leer su contenido
        with io.open(ruta, "r", encoding="iso-8859-15") as f:
             html_content = f.read()

        # Crear un objeto BeautifulSoup para analizar el HTML
        soup = BeautifulSoup(html_content, "html.parser")

        # Encuentra el elemento <a> y <span> en el HTML por el id
        link = soup.find("a", id=aplicacion.lower())
        span = soup.find('span', id=aplicacion.lower()+"_version")

        # Modificar el atributo href del enlace encontrado
        if link:
            link["href"] = "https://softlibre.unizar.es/estandares/aplicacion/"+enlace

        if span:
             span.string = version
         # html_str = str(soup)
         # # Guardar los cambios en el archivo HTML
         # with open(ruta, "w", encoding='iso-8859-15') as f:
         #    f.write(html_str.encode('iso-8859-15').decode('iso-8859-15'))
        with io.open(ruta, "w", encoding="iso-8859-15") as f:
            f.write(str(soup))

# Lista de descargas con la información de cada una
descargas = [
    {"url": "https://www.thunderbird.net/es-ES/", "nombre": "Thunderbird",
     "filtro": {'href': lambda href: href and re.search(r'os=win64&lang=es-ES', href)}, "pattern": r'\d+\.\d+\.\d+', "extension": ".exe", "find_tipe" : 0, "v_simb": ".", "html":["thunderbird.html", "internet.html"]},
    {"url": "https://download.mozilla.org/?product=firefox-latest-ssl&os=win64&lang=es-ES", "nombre": "Firefox",
     "filtro": "", "pattern": r'\d+\.\d+\.\d+', "extension": ".exe", "find_tipe" : 0, "v_simb": ".", "html":["firefox.html", "internet.html"]},
    {"url": "https://filezilla-project.org/download.php?show_all=1", "nombre": "FileZilla",
     "filtro": {'href': lambda href: href and re.search(r'win64-setup.exe', href)}, "pattern": r'\d+\.\d+\.\d+', "extension": ".exe", "find_tipe" : 0, "v_simb": ".", "html":["filezilla.html", "internet.html"]},
    {"url": "https://sourceforge.net/projects/atunes/files/latest/download", "nombre": "aTunes",
     "filtro": "", "pattern": r'\d+\.\d+\.\d+', "extension": ".exe", "find_tipe" : 0, "v_simb": ".", "html":["atunes.html", "multimedia.html"]},
    {"url": "https://www.gimp.org/downloads/", "nombre": "gimp",
     "filtro": {'id': 'win-download-link'}, "pattern": r'\d+\.\d+\.\d+', "extension": ".exe", "find_tipe" : 0, "v_simb": ".", "html":["gimp.html", "multimedia.html"]},
    {"url": "https://www.videolan.org/", "nombre": "vlc",
     "filtro": {'href': lambda href: href and re.search(r'win64.exe', href)}, "pattern": r'\d+\.\d+\.\d+', "extension": ".exe", "find_tipe" : 0, "v_simb": ".", "html":["vlc.html", "multimedia.html"]},
    {"url": "https://obsproject.com/es", "nombre": "OBSStudio",
     "filtro": {'href': lambda href: href and re.search(r'x64.exe', href)}, "pattern": r'\d+\.\d+\.\d+', "extension": ".exe", "find_tipe" : 0, "v_simb": ".", "html":["obsstudio.html", "multimedia.html"]},
    {"url": "https://sourceforge.net/projects/pidgin/files/latest/download", "nombre": "pidgin",
     "filtro": "", "pattern": r'\d+\.\d+\.\d+', "extension": ".exe", "find_tipe" : 0, "v_simb": ".", "html":["pidgin.html", "utilidades.html"]},
    {"url": "https://boinc.berkeley.edu/download.php", "nombre": "boinc",
     "filtro": {'href': lambda href: href and re.search(r'64.exe', href)}, "pattern": r'\d+\.\d+\.\d+', "extension": ".exe", "find_tipe" : 0, "v_simb": ".", "html":["boinc.html", "cientifico.html"]},
    {"url": "https://www.chiark.greenend.org.uk/~sgtatham/putty/latest.html", "nombre": "putty",
     "filtro": {'href': lambda href: href and re.search(r'w64/putty-64bit', href)}, "pattern": r'\d+\.\d+', "extension": ".msi", "find_tipe" : 0, "v_simb": ".", "html":["putty.html", "internet.html"]},
    {"url": "https://www.mirc.com/get.php", "nombre": "mIRC", "filtro": "", "pattern": r'\d+\d+\d+', "extension": ".exe", "find_tipe" : 0, "v_simb": ".", "html":["mirc.html", "internet.html"]},
    {"url": "https://sourceforge.net/projects/libreoffice/files/latest/download", "nombre": "LibreOffice",
     "filtro": "", "pattern": r'\d+\.\d+\.\d+', "extension": ".msi", "find_tipe" : 0, "v_simb": ".", "html":["libreoffice.html", "oficina.html"]},
    {"url": "https://download.pdfforge.org/download/pdfcreator/PDFCreator-stable?download", "nombre": "PDFCreator",
     "filtro": "", "pattern": r'\d+\.\d+\.\d+', "extension": ".exe", "find_tipe" : 0, "v_simb": ".", "html":["pdfcreator.html", "oficina.html"]},
    {"url": "https://www.audacityteam.org/download/windows/", "nombre": "Audacity",
     "filtro": {'href': lambda href: href and re.search(r'64bit.exe', href)}, "pattern": r'\d+\.\d+\.\d+', "extension": ".exe", "find_tipe" : 0, "v_simb": ".", "html":["audacity.html", "multimedia.html"]},
    {"url": "https://sourceforge.net/projects/imgseek/files/latest/download", "nombre": "imgSeek",
     "filtro": "", "pattern": r'\d+\.\d+\.\d+', "extension": ".exe", "find_tipe" : 0, "v_simb": ".", "html":["imgseek.html", "multimedia.html"]},
    {"url": "https://www.openshot.org/es/download/", "nombre": "OpenShot",
     "filtro": {'href': lambda href: href and re.search('x86_64.exe', href)}, "pattern": r'\d+\.\d+\.\d+', "extension": ".exe", "find_tipe" : 0, "v_simb": ".", "html":["openshot.html", "multimedia.html"]},
    {"url": "https://sourceforge.net/projects/shotcut/files/latest/download", "nombre": "Shotcut", "filtro": "", "pattern": r'\d+\d+\d+', "extension": ".exe", "find_tipe" : 0, "v_simb": ".", "html":["shotcut.html", "multimedia.html"]},
    {"url": "https://ftp.cixug.es/CRAN/bin/windows/base/", "nombre": "R",
     "filtro": {'href': lambda href: href and re.search(r'win.exe', href)}, "pattern": r'\d+\.\d+\.\d+', "extension": ".exe", "find_tipe" : 0, "v_simb": ".", "html":["r.html", "cientifico.html"]},
    {"url": "https://caeis.etech.fh-augsburg.de/downloads/windows/latest-release/", "nombre": "pspp",
     "filtro": {'href': lambda href: href and re.search(r'pspp-64bit-install', href)}, "pattern": r'\d+\-\d+\-\d+', "extension": ".exe", "find_tipe" : 0, "v_simb": "-", "html":["pspp.html", "cientifico.html"]},
    {"url": "https://www.octave.org/download", "nombre": "octave",
     "filtro": {'href': lambda href: href and re.search(r'w64-installer', href)}, "pattern": r'\d+\.\d+\.\d+', "extension": ".exe", "find_tipe" : 0, "v_simb": ".", "html":["octave.html", "cientifico.html"]},
    {"url":  "https://sourceforge.net/projects/maxima/files/latest/download", "nombre": "Maxima", "filtro": "", "pattern": r'\d+\.\d+\.\d+', "extension": ".exe", "find_tipe" : 0, "v_simb": ".", "html":["maxima.html", "cientifico.html"]},
     {"url": "https://sourceforge.net/projects/dia-installer/files/latest/download", "nombre": "Dia", "filtro": "", "pattern": r'\d+\.\d+\.\d+', "extension": ".exe", "find_tipe" : 0, "v_simb": ".", "html":["dia.html", "cientifico.html"]},
     {"url": "https://sourceforge.net/projects/ganttproject/files/latest/download", "nombre": "GanttProject",
     "filtro": "", "pattern": r'\d+\.\d+\.\d+', "extension": ".exe", "find_tipe" : 0, "v_simb": ".", "html":["ganttproject.html", "cientifico.html"]},
     {"url": "https://sourceforge.net/projects/sevenzip/files/latest/download", "nombre": "7Zip", "filtro": "", "pattern": r'\d+\d+\d+', "extension": ".exe", "find_tipe" : 0, "v_simb": "", "html":["7zip.html", "utilidades.html"]},
     {"url": "https://sourceforge.net/projects/clamwin/files/latest/download", "nombre": "ClamWin",
     "filtro": "", "pattern": r'\d+\.\d+\.\d+\.\d+', "extension": ".exe", "find_tipe" : 0, "v_simb": ".", "html":["clamwin.html", "utilidades.html"]},
    {"url":  "https://sourceforge.net/projects/notepadplusplus.mirror/files/latest/download", "nombre": "Notepad",
     "filtro": "", "pattern": r'\d+\.\d+\.\d+', "extension": ".exe", "find_tipe" : 0, "v_simb": ".", "html":["notepad.html", "utilidades.html"]},
     {"url": "https://www.virtualbox.org/wiki/Downloads", "nombre": "VirtualBox",
     "filtro": {'href': lambda href: href and re.search(r'Win.exe', href)}, "pattern": r'\d+\.\d+\.\d+', "extension": ".exe", "find_tipe" : 0, "v_simb": ".", "html":["virtualbox.html", "utilidades.html"]},
    {"url": "https://sourceforge.net/projects/azureus/files/latest/download", "nombre": "vuze", "filtro": "", "pattern": r'\d+\d+\d+\d+', "extension": ".exe", "find_tipe" : 0, "v_simb": "", "html":["vuze.html", "utilidades.html"]},
    {"url": "https://sourceforge.net/projects/infrarecorder/files/latest/download", "nombre": "InfraRecorder",
     "filtro": "", "pattern": r'\d+\d+\d+', "extension": ".exe", "find_tipe" : 0, "v_simb": "", "html":["infrarecorder.html", "utilidades.html"]},
    {"url": "https://mirrors.sahilister.in/blender/release/", "nombre": "Blender",
      "filtro": {'href': lambda href: href and re.search(r'Blender(\d+\.\d+)', href)}, "pattern": r'(\d+\.\d+)', "extension": ".msi", "find_tipe" : 1, "v_simb": ".", "html":["blender.html", "multimedia.html"]},
    ### a la hora de obtener la url con 'location' obtiene una version antigua
    #scribus#
    #{"url": "https://sourceforge.net/projects/scribus/files/scribus/", "nombre": "scribus",
    # "filtro": {'href': lambda href: href and re.search(r'scribus/(\d+\.\d+\.\d+)', href)}, "pattern": r'(\d+\.\d+\.\d+)', "extension": ".exe", "find_tipe" : 1, "v_simb": ".", "html":["scribus.html", "oficina.html"]},
    ### HTTP Error 403: Forbidden 
    #sumatrapdf#
    ## {"url": "https://www.sumatrapdfreader.org/download-free-pdf-viewer", "nombre": "Sumatra",
    ##  "filtro": {'href': lambda href: href and re.search(r'64-install', href)}, "pattern": r'\d+\.\d+\.\d+', "extension": ".exe", "find_tipe" : 0, "v_simb": ".", "html":["sumatra.html", "oficina.html"]},
    #inkscape#
     {"url": "https://inkscape.org/release/all/windows/64-bit/exe/", "nombre": "inkscape",
      "filtro": {'href': lambda href: href and re.search(r'inkscape-(\d+\.\d+\.\d+)_', href)}, "pattern": r'(\d+\.\d+\.\d+)', "extension": ".exe", "find_tipe" : 2, "v_simb": ".", "html":["inkscape.html", "multimedia.html"]},   
    ### HTTP Error 403: Forbidden 
    ####{"url": "https://www.zotero.org/download/", "nombre": "zotero",
    ## "filtro": {'href': lambda href: href and re.search(r'version', href)}, "pattern": r'\d+\.\d+\.\d+', "extension": ".exe", "find_tipe" : 0, "v_simb": ".", "html":["zotero.html", "utilidades.html"]},
    {"url": "https://ftp.osuosl.org/pub/osgeo/download/qgis/windows/", "nombre": "qgis",
     "filtro": {'href': lambda href: href and re.search(r'QGIS-OSGeo4W-(\d+\.\d+\.\d+)', href)}, "pattern": r'(\d+\.\d+\.\d+)', "extension": ".msi", "find_tipe" : 3, "v_simb": ".", "html":["qgis.html", "cientifico.html"]},
     {"url": "https://cran.rstudio.com/bin/windows/base/", "nombre": "rstudio",
     "filtro": {'href': lambda href: href and re.search(r'win.exe', href)}, "pattern": r'(\d+\.\d+\.\d+)', "extension": ".exe", "find_tipe" : 0, "v_simb": ".", "html":["rstudio.html", "cientifico.html"]},
]

# Procesar cada descarga
for descarga in descargas:
    url = descarga["url"]
    nombre = descarga["nombre"]
    filtro = descarga["filtro"]
    pattern = descarga["pattern"]
    extension = descarga["extension"]
    findTipe = descarga["find_tipe"]
    simbolo = descarga["v_simb"]
    enlace_descarga = ""
    htmls =descarga["html"]

    if findTipe == 0:
        # utilizamos el metodo para obtener el enlace, pero si filtro esta vacio le pasamos el link directo sin buscarlo en el html
        enlace_descarga = obtener_enlace_descarga(url, filtro) if filtro else url                
    elif findTipe == 1:
        ### De momento esto solo se utiliza para la descarga de blender
        # Si findAll es verdadero utilizaremos el metodo obtener_enlace_descarga
            filtro2={'href': lambda href: href and re.search(extension, href)}
            doble_filtro = encontrar_version_mas_alta(url, filtro, pattern, simbolo)
            url = url + doble_filtro
            enlace_descarga = obtener_enlace_descarga(url, filtro2)        
    elif findTipe == 2:
        enlace_descarga = encontrar_version_mas_alta(url, filtro, pattern, simbolo)
    elif findTipe == 3:
        enlace_descarga = url + encontrar_version_mas_alta(url, filtro, pattern, simbolo)
    if enlace_descarga:
        logging.info(f'Enlace de descarga encontrado: {enlace_descarga}')
        response = requests.head(enlace_descarga)
        if response.status_code == 307:
            enlace_descarga = unquote(response.headers.get('Location'))
        # Verificar el código de estado de la respuesta
        if response.status_code == 200 or response.status_code == 302 or response.status_code == 307:
            # Obtener el nombre del archivo desde el enlace de descarga
            location = unquote(response.url)
            # Obtener la versión del archivo a descargar, si no pasamos pattern sera vacio
            if pattern:
                version_descargada = obtener_version(pattern, location)
                if not version_descargada:
                    try:
                        location = unquote(response.headers.get('Location'))
                        version_descargada = obtener_version(pattern, location)
                    except OSError as e:
                        logging.error(f"Error al obtener version: {e}")    
            else:
                version_descargada = ""
            nombre_descarga = nombre+"_"+version_descargada
            # Buscar archivo existente para reemplazar
            archivo_a_reemplazar = buscar_archivo_a_reemplazar(version_descargada, nombre, simbolo)

            if archivo_a_reemplazar:
                # Descargar el archivo
                try:
                    #response = descargar_con_reintentos(enlace_descarga, response.headers, 3)  
                    headers = {
                    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0',
                    }
                    nombre_completo = nombre_descarga+extension                           
                    response.headers = headers
                    wget.download(enlace_descarga, f'/srv/repositorios/estandares/aplicacion/{nombre_completo}')
                    modificar_htmls(htmls, nombre_completo, version_descargada, nombre)
                    logging.info("Descarga completada")
                except Exception as e:
                    logging.error(f"Error al descargar el archivo: {e}")
                    continue
                # borrar archivo de la version antigua
                if os.path.exists(f"/srv/repositorios/estandares/aplicacion/{archivo_a_reemplazar}"):
                    try:
                        os.remove(f"/srv/repositorios/estandares/aplicacion/{archivo_a_reemplazar}")
                        logging.info(f"Archivo reemplazado: {archivo_a_reemplazar} por {nombre_completo}")
                    except OSError as e:
                        logging.error(f"No se pudo borrar el archivo antiguo: {e}")
                else:
                    logging.info(f"{archivo_a_reemplazar} {nombre_descarga}")
            else:
                logging.info(f"No se ha encontrado una version nueva para descargar de {nombre}")
        else:
            logging.info(f"Error al descargar el archivo: Código de estado {response.status_code}")
    else:
        logging.info('No se encontró el enlace de descarga en la página '+url)
