import logging

from ovbpclient.models import oteams as oteams_models

logger = logging.getLogger(__name__)


def delete_project(project: "oteams_models.Project"):
    logging.info(f"deleting project: {project.name}")

    for list_all, plural_name in (
            (project.list_all_analyses, "analyses"),
            (project.list_all_importers, "importers"), # cleaners will be deleted with importers
            (project.list_all_gates, "gates")
    ):
        logging.info(f" | deleting {plural_name}")
        for record in list_all():
            record.delete()
            logging.info(f" |    deleted: {record.name}")

    project.delete()
    logging.info(f"project was deleted: {project.name}")
    logging.info("")


def delete_organization(organization: "oteams_models.Organization"):
    for project in organization.list_all_projects():
        delete_project(project)
