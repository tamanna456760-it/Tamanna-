# build_project.py
from akon_tamanna_sync import AkonBuildSystem

# Build entire project
builder = AkonBuildSystem(project_root=".")
builder.build_project()
