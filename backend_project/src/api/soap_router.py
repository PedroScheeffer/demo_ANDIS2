from fastapi import APIRouter, Body, HTTPException, Depends
from sqlalchemy.orm import Session
from services.project_service import ProjectService
from config.database import get_db

import xml.etree.ElementTree as ET

soap_router = APIRouter(prefix="/api/projects/soap", tags=["projects-soap"])


def get_project_service(db: Session = Depends(get_db)) -> ProjectService:
    return ProjectService(db)


@soap_router.post("/getProject")
def get_project_soap(
    xml_body: str = Body(..., media_type="application/xml"),
    service: ProjectService = Depends(get_project_service)
):
    """
    Endpoint SOAP para obtener un proyecto por ID.
    Recibe XML, extrae el projectId y devuelve XML en formato SOAP.
    """

    try:
        # Parseamos el XML recibido
        root = ET.fromstring(xml_body)

        # Extraemos el ID: Envelope -> Body -> GetProject -> projectId
        project_id = int(
            root.find(".//projectId").text
        )
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="XML inválido o falta <projectId>"
        )

    # Buscamos el proyecto usando la lógica real del backend
    project = service.get_project_by_id(project_id)

    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")

    # Construimos respuesta XML estilo SOAP
    response_xml = f"""
        <Envelope>
            <Body>
                <GetProjectResponse>
                    <id>{project.id}</id>
                    <name>{project.name}</name>
                    <ownerId>{project.user_id}</ownerId>
                </GetProjectResponse>
            </Body>
        </Envelope>
    """

    return Response(content=response_xml, media_type="application/xml")
