import argparse
import json
import os
from pathlib import Path

import docker
import docker.errors
import requests
import semver
from jinja2 import Template

DOCKER_IMAGE_NAME = "ncareau/docker-rancher-cli-kubectl"
VERSIONS_PATH = Path("versions.json")

def load_versions():
    with VERSIONS_PATH.open() as fp:
        return json.load(fp)["versions"]

def render_dockerfile(version):

    with open('template.Dockerfile') as f:
        tmpl = Template(f.read())
    
    output = tmpl.render(rancher_cli_version=version["rancher-cli2"], k8s_kubectl_version=version["k8s-kubectl"])

    if not os.path.exists('./dist'):
        os.makedirs('./dist')

    with open('dist/'+version["tag"]+'.Dockerfile', 'w') as fh:
        fh.write(output)

def docker_render(versions):
    versions = {ver["tag"]: ver for ver in versions}

    for key, ver in versions.items():
        render_dockerfile(ver)

def docker_build(versions,dry_run):
    # Login to docker hub
    docker_client = docker.from_env()
    dockerhub_username = os.getenv("DOCKERHUB_USERNAME")
    try:
        docker_client.login(dockerhub_username, os.getenv("DOCKERHUB_PASSWORD"))
    except docker.errors.APIError:
        print(f"Could not login to docker hub with username:'{dockerhub_username}'.")
        print("Is env var DOCKERHUB_USERNAME and DOCKERHUB_PASSWORD set correctly?")
        exit(1)

    # Build, tag and push images
    for version in versions:

        rancher_cli_version = version["rancher-cli2"]
        k8s_kubectl_version = version["k8s-kubectl"]

        print(
            f"Building image {version['tag']} rancher-cli: {rancher_cli_version} k8s-kubectl: {k8s_kubectl_version} ...",
            end="",
            flush=True,
        )
        if not dry_run:
            docker_client.images.build(path='dist/', dockerfile=version["tag"] + '.Dockerfile', tag=version['tag'], rm=True, pull=True)
        print(f" pushing...", flush=True)
        if not dry_run:
            docker_client.images.push(DOCKER_IMAGE_NAME, version["tag"])

def main(dry_run):

    # Get Versions 
    versions = load_versions()

    # TODO Fetch new version
    # TODO Update README, versions.json and push git

    # Render Dockerfile
    docker_render(versions)

    # Build and push Dockerfile
    docker_build(versions, dry_run)

    # Save Version_built.json
    
    print("Done")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(usage="Build k8s-kubectl with rancher-cli2 docker images")
    parser.add_argument(
        "--dry-run", action="store_true", dest="dry_run", help="Skip persisting, README update, and pushing of builds"
    )
    args = vars(parser.parse_args())
    main(**args)