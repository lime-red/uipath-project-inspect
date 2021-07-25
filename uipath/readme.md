# UiPath Project Inspect

This project contains helpers that will allow you to quickly inspect details about a UiPath project.

The files themselves are relatively simple and are designed so you can chop and change, inspect and composite them as much as you like.

This way, if there is something the library does not do for you, you can easily pick up the data it has read and crunch it the way you want to.

## Usage/Examples

Supply a project root, and the library will load the project.json.  

By default it will also read and interpret all the .xaml files it can find under the project root folder.  This can be disabled with `load_sequences=False`.

Example:
```python
import uipath.project
import uipath.xaml

project = uipath.project.UiPathProject('path/to/uipath-project-folder')

print(project.libraries)
print(project.sequences)

for seq in project.sequences:
    print(f'Arguments for {seq.xaml_path}:')
    print(seq.arguments)
```

The library is written to scratch two specific itches:
- To automatically generate documentation for UiPath projects (using arguments lists and top-level annotations)
- To audit library + library version usage over a fleet of bots