import logging

from ovbpclient.models import oteams as oteams_models

logger = logging.getLogger(__name__)


def deactivate_project(project: "oteams_models.Project"):
    logging.info(f"deactivating project: {project.name}")

    logging.info(" |  deactivating gates")
    for gate in project.list_all_gates():
        feeder = gate.get_base_feeder()
        if (feeder is not None) and feeder.active:
            gate.deactivate()
            logging.info(f" |    deactivated: {gate.name}")
        else:
            logging.info(f" |    already deactivated: {gate.name}")

    logging.info(" |  deactivating importers")
    for importer in project.list_all_importers():
        if importer.active:
            importer.deactivate()
            logging.info(f" |    deactivated: {importer.name}")
        else:
            logging.info(f" |    already deactivated: {importer.name}")
    logging.info("")



def deactivate_organization(organization: "oteams_models.Organization"):
    for project in organization.list_all_projects():
        deactivate_project(project)
