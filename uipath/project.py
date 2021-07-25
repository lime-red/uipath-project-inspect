from typing import List, Dict

import json
import os
import glob
import logging

from uipath.xaml import UiPathXaml

class UiPathProject:

    project_json: str = None
    project_data: Dict = None
    project_root: str = None
    xaml_filenames: List[str] = None
    sequences: List[UiPathXaml] = None
    libraries: Dict[str, str] = None

    PROJECT_JSON_FILENAME = 'project.json'

    def __init__(self, project_root: str, load_sequences: bool = True):
        self.logger = logging.getLogger(__name__)
        self.logger.debug(f"Loading project_root %s", project_root)
        self.project_root = project_root

        self.project_json = self.read_project_json(self.project_root)
        self.project_data = self.parse_project_json(self.project_json)

        self.xaml_filenames = self.list_xamls(self.project_root)

        if load_sequences:
            self.sequences = self.load_xamls(self.project_root, self.xaml_filenames)
            self.libraries = self.extract_libraries(self.project_data)

    def __str__(self):
        return self.project_root

    def __repr__(self):
        return f"<{str(self.__class__)} project_root='{self.project_root}''>"


    def read_project_json(self, project_root):
        with open(os.path.join(project_root, self.PROJECT_JSON_FILENAME), 'r') as project_data:
            project_json = project_data.read()

        return project_json


    def parse_project_json(self, project_json):
        # parse file
        project_data = json.loads(project_json)

        return project_data


    def list_xamls(self, project_root):
        xaml_glob = os.path.join(project_root, "**", "*.xaml")
        xamls = glob.glob(xaml_glob, recursive=True)

        return(xamls)

    def load_xamls(self, project_root, xaml_filenames):
        sequences = {}
        for xaml_filename in xaml_filenames:
            sequences[xaml_filename] = UiPathXaml(project_root=project_root, xaml_path=xaml_filename, project_studio_version=None)

        return sequences

    def extract_libraries(self, project_data) -> Dict[str, str]:
        libraries: List = project_data['dependencies']

        return libraries