from typing import List, Dict

import logging

import xmltodict

logger = logging.getLogger(__name__)

class UiPathXaml:

    project_root: str = None
    xaml_path: str = None
    seq_xaml: str = None
    seq_dict: Dict = None
    top_level_annotation: str = None
    arguments: List = None
    
    def __init__(self, project_root: str, xaml_path: str, project_studio_version=None) -> None:
        self.logger = logging.getLogger(__name__)
        self.logger.debug(f"Loading xaml_path %s", xaml_path)

        self.project_root = project_root
        self.xaml_path = xaml_path
        
        self.seq_xaml = self.load_xaml(self.xaml_path)
        self.seq_dict = self.xaml_to_dict(self.seq_xaml)
        self.top_level_annotation = self.extract_top_level_annotation(self.seq_dict)
        self.arguments = self.extract_arguments(self.seq_dict)

    def __str__(self) -> str:
        return self.xaml_path

    def __repr__(self) -> str:
        return f"<{str(self.__class__)} xaml_path='{self.xaml_path}''>"


    def load_xaml(self, xaml_path: str) -> str:
        with open(xaml_path) as fd:
            xaml = fd.read()

        return xaml

    def xaml_to_dict(self, xaml: str) -> Dict:
        doc: Dict = xmltodict.parse(xaml)
        return doc

    def extract_top_level_annotation(self, seq_dict: Dict) -> str:
        # <Activity mc:Ignorable="sap sap2010" x:Class="Main" sap2010:ExpressionActivityEditor.ExpressionActivityEditor="C#" sap:VirtualizedContainerService.HintSize="1208,867" sap2010:WorkflowViewState.IdRef="ActivityBuilder_1" xmlns="http://schemas.microsoft.com/netfx/2009/xaml/activities" xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" xmlns:sap="http://schemas.microsoft.com/netfx/2009/xaml/activities/presentation" xmlns:sap2010="http://schemas.microsoft.com/netfx/2010/xaml/activities/presentation" xmlns:scg="clr-namespace:System.Collections.Generic;assembly=mscorlib" xmlns:sco="clr-namespace:System.Collections.ObjectModel;assembly=mscorlib" xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">
        #     <Sequence sap2010:Annotation.AnnotationText="This is the top-level annotation" sap:VirtualizedContainerService.HintSize="200,125" sap2010:WorkflowViewState.IdRef="Sequence_1">
        #         ...
        #     </Sequence>
        # </Activity>

        #>>> x.seq_dict['Activity']['Sequence']
        #OrderedDict([('@sap2010:Annotation.AnnotationText', 'This is the top-level annotation'), ('@sap:VirtualizedContainerService.HintSize', '200,125'), ('@sap2010:WorkflowViewState.IdRef', 'Sequence_1'), ('sap:WorkflowViewStateService.ViewState', OrderedDict([('scg:Dictionary', OrderedDict([('@x:TypeArguments', 'x:String, x:Object'), ('x:Boolean', [OrderedDict([('@x:Key', 'IsExpanded'), ('#text', 'True')]), OrderedDict([('@x:Key', 'IsAnnotationDocked'), ('#text', 'True')])])]))]))])

        # Sequence and GlobalHandler use ['Activity']['Sequence']
        # StateMachine uses ['Activity']['StateMachine']
        # Flowchart uses ['Activity']['Flowchart']

        annotation_key: str = '@sap2010:Annotation.AnnotationText'
        parent_element: Dict = None
        top_level_annotation: str = None

        if 'Sequence' in seq_dict['Activity']:
            parent_element = seq_dict['Activity']['Sequence']
        elif 'StateMachine' in seq_dict['Activity']:
            parent_element = seq_dict['Activity']['StateMachine']
        elif 'Flowchart' in seq_dict['Activity']:
            parent_element = seq_dict['Activity']['Flowchart']
        else:
            raise Exception("Unable to find an appropriate top-level activity (tried Sequence, StateMachine and Flowchart)")

        for key in parent_element:
            if key == annotation_key:
                top_level_annotation = parent_element[key]
                break
            else:
                logger.debug(f"Skipping element {key}")

        if top_level_annotation is None:
            self.logger.info("Could not locate a top-level annotation for file %s", self.xaml_path)

        return top_level_annotation


    def extract_arguments(self, seq_dict: Dict) -> List:
        # <Activity mc:Ignorable="sap sap2010" x:Class="Sequence" xmlns="http://schemas.microsoft.com/netfx/2009/xaml/activities" xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" xmlns:sap="http://schemas.microsoft.com/netfx/2009/xaml/activities/presentation" xmlns:sap2010="http://schemas.microsoft.com/netfx/2010/xaml/activities/presentation" xmlns:scg="clr-namespace:System.Collections.Generic;assembly=mscorlib" xmlns:sco="clr-namespace:System.Collections.ObjectModel;assembly=mscorlib" xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">
        # <x:Members>
        #     <x:Property Name="in_argument" Type="InArgument(x:String)" />
        # </x:Members>

        # .seq_dict['Activity']['x:Members']['x:Property']
        # if the value is an OrderedDict, then there is only one argument
        # if the value is a list, then there are many arguments

        arguments: List = None

        if 'Activity' in seq_dict and \
            'x:Members' in seq_dict['Activity'] and \
            'x:Property' in seq_dict['Activity']['x:Members']:
            if type(seq_dict['Activity']['x:Members']['x:Property']) == 'OrderedDict':
                arguments = [seq_dict['Activity']['x:Members']['x:Property']]
            else:
                arguments = seq_dict['Activity']['x:Members']['x:Property']
            logging.debug("%d argument%s found in file %s", len(arguments), 's' if len(arguments) != 1 else '', self.xaml_path)
        else:
            logging.debug("No arguments found in file %s", self.xaml_path)

        return arguments

