#!/bin/bash
# Activa el entorno virtual
source /srv/repositorios/webnueva/scripts/env/bin/activate
# Ejecuta el script de Python
python3 /srv/repositorios/webnueva/scripts/descarga.py
# Desactiva el entorno virtual
deactivate
