from dotenv import load_dotenv
from os import environ
from os import path
from pathlib import Path

import argparse
import jinja2
import json
import mlflow


# Replace a .json.j2 template file with environment variables
def read_with_env(template, **override_env):
    env = {**environ, **override_env}
    template = Path(template).read_text(encoding="utf-8")
    rendered = jinja2.Template(template).render(**env)
    return json.loads(rendered)


def create_experiment(experiment_name):
    experiment = mlflow.get_experiment_by_name(experiment_name)
    experiment_artifact = experiment.artifact_location if experiment else ""
    experiment_id = experiment.experiment_id if experiment else None
    blob_storage_name = environ.get("AZURE_STORAGE_ACCOUNT_NAME")
    blob_container_name = environ.get("AZURE_STORAGE_CONTAINER_NAME")
    blob_uri = (
        f"wasbs://{blob_container_name}@{blob_storage_name}.blob.core.windows.net"
        if blob_container_name and blob_storage_name
        else None
    )
    if experiment is None:
        print(f"Experiment {experiment_name} doesn't exist, creating new with artifact_location {blob_uri}")
        experiment_id = mlflow.create_experiment(experiment_name, artifact_location=blob_uri)
    # artifact_location are set at the experiment level upon creation
    # if this changes, the experiment needs to be recreated
    elif experiment_artifact != blob_uri and not (experiment_artifact.startswith("dbfs") and blob_uri is None):
        print(f"Experiment {experiment_name} already exist with artifact_location {experiment_artifact}")
        mlflow.delete_experiment(experiment_id)
        experiment_id = mlflow.create_experiment(experiment_name, artifact_location=blob_uri)
        print(f"Experiment {experiment_name} recreated with artifact_location {blob_uri}")
    return experiment_id 


def main(project_entry_point, project_path, project_experiment_folder):
    load_dotenv()
    experiment_id = create_experiment(project_experiment_folder)
    cluster_config = read_with_env(f"{project_path}/cluster.json.j2")
    parameter_file = (
        f"{project_path}/parameters.json.j2"
        if project_entry_point == "main"
        else f"{project_path}/{project_entry_point}/parameters.json.j2"
    )
    parameters = read_with_env(parameter_file) if path.exists(parameter_file) else {}
    mlflow.run(
        project_path,
        experiment_id=experiment_id,
        entry_point=project_entry_point,
        backend="databricks",
        backend_config=cluster_config,
        synchronous=False,
        parameters=parameters,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--projectEntryPoint",
        type=str,
        required=False,
        default="main",
        help="Project entry point for MLFlow run from MLProject.",
    )
    parser.add_argument(
        "--projectPath",
        type=str,
        required=True,
        help="The source folder to where MLProject file is under.",
    )
    parser.add_argument(
        "--projectExperimentFolder",
        type=str,
        required=True,
        help="The destination folder on databricks where the project folder is uploaded.",
    )
    args = parser.parse_args()

    main(args.projectEntryPoint, args.projectPath, args.projectExperimentFolder)
