from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from core.plus.decorators import require_permission
from core.plus.services import ServiceRegistry
from apps.contract.models import contractTemplates


class ContractTemplateService:

    # =========================================================
    # 1. BUSCAR PLANTILLAS DE CONTRATOS
    # =========================================================
    @staticmethod
    @require_permission("view_contract_templates")
    @ServiceRegistry.register(
        "contracts.ContractTemplateService.search_contract_templates"
    )
    def search_contract_templates(user, query=None):

        try:
            # Obtener la empresa del usuario.
            company = getattr(user, "company", None)

            if not company:
                return {
                    "success": False,
                    "error": "El usuario no tiene una empresa asignada."
                }

            # Filtrar exclusivamente por empresa.
            templates = contractTemplates.objects.filter(
                company=company
            ).order_by("-created_at", "-id")

            # Búsqueda opcional por nombre.
            if query:
                query = str(query).strip()

                if query:
                    templates = templates.filter(
                        name__icontains=query
                    )

            # Obtener los primeros 20 resultados.
            templates = templates[:20]

            # Convertir los modelos a diccionarios.
            results = [
                {
                    "id": template.id,
                    "name": template.name,
                    "created_at": template.created_at.isoformat(),
                }
                for template in templates
            ]

            return {
                "success": True,
                "answer": results,
                "error": "La búsqueda de plantillas se realizó correctamente."
            }

        except Exception:
            return {
                "success": False,
                "error": "Ocurrió un error al buscar las plantillas."
            }


    # =========================================================
    # 2. CREAR UNA PLANTILLA DE CONTRATO
    # =========================================================

    @staticmethod
    @require_permission("create_contract_template")
    @ServiceRegistry.register(
        "contracts.ContractTemplateService.create_contract_template"
    )
    def create_contract_template(user, data):

        try:
            company = getattr(user, "company", None)

            if not company:
                return {
                    "success": False,
                    "error": "El usuario no tiene una empresa asignada."
                }

            if not isinstance(data, dict):
                return {
                    "success": False,
                    "error": "Los datos proporcionados no son válidos."
                }

            # Validar nombre.
            name = data.get("name")

            if not isinstance(name, str) or not name.strip():
                return {
                    "success": False,
                    "error": "El nombre de la plantilla es obligatorio."
                }

            name = name.strip()

            if len(name) > 255:
                return {
                    "success": False,
                    "error": "El nombre no puede superar los 255 caracteres."
                }

            # Validar el contenido del contrato.
            contract_container = data.get("contract_container")

            if not isinstance(contract_container, dict):
                return {
                    "success": False,
                    "error": "El contenido de la plantilla debe ser un objeto JSON."
                }

            # La sucursal debe pertenecer a la empresa del usuario.
            branch = getattr(user, "branch", None)

            if not branch:
                return {
                    "success": False,
                    "error": "El usuario no tiene una sucursal asignada."
                }

            if branch.company_id != company.id:
                return {
                    "success": False,
                    "error": "La sucursal no pertenece a la empresa del usuario."
                }

            with transaction.atomic():

                template = contractTemplates.objects.create(
                    company=company,
                    branch=branch,
                    name=name,
                    contract_container=contract_container
                )

            return {
                "success": True,
                "message": "La plantilla se creó correctamente.",
                "data": {
                    "id": template.id,
                    "name": template.name,
                    "branch_id": template.branch_id,
                    "created_at": template.created_at.isoformat()
                }
            }

        except (ValidationError, IntegrityError):
            return {
                "success": False,
                "error": "No fue posible guardar la plantilla."
            }

        except Exception:
            return {
                "success": False,
                "error": "Ocurrió un error al crear la plantilla."
            }


    # =========================================================
    # 3. EDITAR UNA PLANTILLA DE CONTRATO
    # =========================================================
    @staticmethod
    @require_permission("edit_contract_template")
    @ServiceRegistry.register(
        "contracts.ContractTemplateService.update_contract_template"
    )
    def update_contract_template(user, template_id, data):

        try:
            company = getattr(user, "company", None)

            if not company:
                return {
                    "success": False,
                    "error": "El usuario no tiene una empresa asignada."
                }

            if not isinstance(data, dict):
                return {
                    "success": False,
                    "error": "Los datos proporcionados no son válidos."
                }

            # Buscar exclusivamente dentro de la empresa.
            template = contractTemplates.objects.filter(
                id=template_id,
                company=company
            ).first()

            if not template:
                return {
                    "success": False,
                    "error": "La plantilla no existe o no tienes acceso a ella."
                }

            # Actualizar únicamente los campos permitidos.
            if "name" in data:

                name = data["name"]

                if not isinstance(name, str) or not name.strip():
                    return {
                        "success": False,
                        "error": "El nombre de la plantilla es obligatorio."
                    }

                name = name.strip()

                if len(name) > 255:
                    return {
                        "success": False,
                        "error": "El nombre no puede superar los 255 caracteres."
                    }

                template.name = name

            if "contract_container" in data:

                contract_container = data["contract_container"]

                if not isinstance(contract_container, dict):
                    return {
                        "success": False,
                        "error": "El contenido debe ser un objeto JSON."
                    }

                template.contract_container = contract_container

            # Guardar los cambios.
            template.save(
                update_fields=[
                    "name",
                    "contract_container"
                ]
            )

            return {
                "success": True,
                "message": "La plantilla se actualizó correctamente.",
                "data": {
                    "id": template.id,
                    "name": template.name,
                    "contract_container": template.contract_container,
                    "branch_id": template.branch_id,
                    "created_at": template.created_at.isoformat()
                }
            }

        except Exception:
            return {
                "success": False,
                "error": "Ocurrió un error al actualizar la plantilla."
            }


    # =========================================================
    # 4. ELIMINAR UNA PLANTILLA DE CONTRATO
    # =========================================================
    @staticmethod
    @require_permission("delete_contract_template")
    @ServiceRegistry.register(
        "contracts.ContractTemplateService.delete_contract_template"
    )
    def delete_contract_template(user, template_id):

        try:
            company = getattr(user, "company", None)

            if not company:
                return {
                    "success": False,
                    "error": "El usuario no tiene una empresa asignada."
                }

            # Impedir que se eliminen plantillas de otras empresas.
            template = contractTemplates.objects.filter(
                id=template_id,
                company=company
            ).first()

            if not template:
                return {
                    "success": False,
                    "error": "La plantilla no existe o no tienes acceso a ella."
                }

            template_id_deleted = template.id

            template.delete()

            return {
                "success": True,
                "message": "La plantilla se eliminó correctamente.",
                "data": {
                    "id": template_id_deleted
                }
            }

        except Exception:
            return {
                "success": False,
                "error": "Ocurrió un error al eliminar la plantilla."
            }


    # =========================================================
    # OBTENER EL CONTENIDO DE UNA PLANTILLA POR ID
    # =========================================================
    @staticmethod
    @require_permission("view_contract_templates")
    @ServiceRegistry.register(
        "contracts.ContractTemplateService.get_contract_template"
    )
    def get_contract_template(user, template_id):

        try:
            company = getattr(user, "company", None)

            if not company:
                return {
                    "success": False,
                    "error": "El usuario no tiene una empresa asignada."
                }

            # Buscar la plantilla dentro de la empresa del usuario.
            template = contractTemplates.objects.filter(
                id=template_id,
                company=company
            ).first()

            if not template:
                return {
                    "success": False,
                    "error": "La plantilla no existe o no tienes acceso a ella."
                }

            return {
                "success": True,
                "answer": {
                    "id": template.id,
                    "name": template.name,
                    "contract_container": template.contract_container,
                    "branch_id": template.branch_id,
                    "created_at": template.created_at.isoformat()
                },
                "message": "La plantilla se obtuvo correctamente."
            }

        except Exception:
            return {
                "success": False,
                "error": "Ocurrió un error al obtener la plantilla."
            }
