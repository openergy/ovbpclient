import logging

from ovbpclient.models import oteams as oteams_models

logger = logging.getLogger(__name__)


def clear_project(project: "oteams_models.Project"):
    logging.info(f"clear project: {project.name}")

    logging.info(" |  clearing project")
    for importer in project.list_all_importers():
        if importer.gate is None:
            logging.info(f" |    no gate, clear action was not triggered: {importer.name}")
        else:
            importer.clear()
            logging.info(f" |    clear action was triggered: {importer.name}")
    logging.info("")


def clear_organization(organization: "oteams_models.Organization"):
    for project in organization.list_all_projects():
        clear_project(project)
