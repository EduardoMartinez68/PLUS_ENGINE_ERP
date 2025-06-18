#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "No se puede importar Django. ¿Lo tienes instalado? "
            "Ejecuta 'pip install django' para instalarlo."
        ) from exc

    execute_from_command_line(sys.argv)
