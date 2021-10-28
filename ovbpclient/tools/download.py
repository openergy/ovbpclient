import os
import logging

import slugify

from ovbpclient.models import oteams as oteams_models
from ovbpclient.json import json_dump


def sanitize_name(name):
    # https://newbedev.com/regular-expression-for-valid-filename
    return slugify.slugify(name, regex_pattern=r"[^\w\-.\s]")


logger = logging.getLogger(__name__)


def download_organization(organization: "oteams_models.Organization", target_dir_path):
    if not os.path.isdir(target_dir_path):
        os.mkdir(target_dir_path)
    if len(os.listdir(target_dir_path)) > 0:
        raise ValueError("Target directory is not empty, can't download.")
    for project in organization.list_all_projects():
        logger.info(f"Downloading project {project.name}.")
        download_project(project, os.path.join(target_dir_path, sanitize_name(project.name)))


def download_project(project: "oteams_models.Project", target_dir_path):
    if not os.path.isdir(target_dir_path):
        os.mkdir(target_dir_path)
    if len(os.listdir(target_dir_path)) > 0:
        raise ValueError("Target directory is not empty, can't download.")

    # gates
    logger.info("Downloading gates.")
    gates_path = os.path.join(target_dir_path, "1-gates")
    os.mkdir(gates_path)
    for gate in project.list_all_gates():
        data = gate.data.copy()
        if gate.base_feeder is not None:
            base_feeder = gate.get_base_feeder()
            data["base_feeder"] = base_feeder.data
            child_feeder = base_feeder.get_child()
            if child_feeder is not None:
                data["base_feeder"]["child_data"] = child_feeder.data.copy()
        json_dump(data, os.path.join(gates_path, f"{sanitize_name(gate.name)}.json"), indent=4)

    # importers
    logger.info("Downloading importers.")
    importers_path = os.path.join(target_dir_path, "2-importers")
    os.mkdir(importers_path)
    for importer in project.list_all_importers():
        json_dump(importer.data, os.path.join(importers_path, f"{sanitize_name(importer.name)}.json"), indent=4)

    # cleaners
    logger.info("Downloading cleaners.")
    cleaners_path = os.path.join(target_dir_path, "3-cleaners")
    os.mkdir(cleaners_path)
    for cleaner in project.list_all_cleaners():
        cleaner_dir_path = os.path.join(cleaners_path, sanitize_name(cleaner.name))
        os.mkdir(cleaner_dir_path)
        json_dump(cleaner.data, os.path.join(cleaner_dir_path, "#cleaner.json"), indent=4)
        for unitcleaner in cleaner.list_all_unitcleaners():
            json_dump(
                unitcleaner.data,
                os.path.join(cleaner_dir_path, f"{sanitize_name(unitcleaner.name)}.json"), indent=4)

    # analyses
    logger.info("Downloading analyses.")
    analyses_path = os.path.join(target_dir_path, "4-analyses")
    os.mkdir(analyses_path)
    for analysis in project.list_all_analyses():
        # download analysisconfig
        analysis.reload()

        # prepare data
        data = analysis.data.copy()

        # inputs
        data["inputs"] = [i.data.copy() for i in analysis.list_all_analysis_inputs()]

        # outputs
        data["outputs"] = [o.data.copy() for o in analysis.list_all_analysis_outputs()]

        json_dump(data, os.path.join(analyses_path, f"{sanitize_name(analysis.name)}.json"), indent=4)
