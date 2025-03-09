# region Pre-Defined

import os
from pydantic import BaseModel
from crimson.templator import format_insert, format_indent, format_insert_loop
from typing import List
import shutil
import json

topics_t = r""""\\[topic\\]",
"""

dependencies_t = r'"\\[dependency\\]",'

template = r"""[build-system]
requires = ["setuptools>=61.0.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "\[name_space\]-\[module_name\]"
version = "\[version\]"
description = "\[description\]"
readme = "README.md"
authors = [
  { name="\[name\]", email="\[email\]" },
]

classifiers = [
    "Development Status :: 2 - Pre-Alpha",

    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",

    "Intended Audience :: Developers",

    \{topics_f\}
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",

    "Typing :: Typed",

]
dependencies = [
    \{dependencies_f\}
]
requires-python = ">=3.9"

[project.urls]
"Homepage" = "https://github.com/\[github_id\]/\[repo_name\]"
"Bug Tracker" = "https://github.com/\[github_id\]/\[repo_name\]/issues"
"""


class Kwargs(BaseModel):
    name: str = "Sisung Kim"
    email: str = "sisung.kim1@gmail.com"
    github_id: str = "crimson206"
    repo_name: str
    version: str
    name_space: str
    module_name: str
    description: str
    topics: List[str]
    dependencies: List[str]


class Options(BaseModel):
    discussion: bool = False


def add_options(template: str, options: Options) -> str:

    if options.discussion:
        discussion_block = r'''"Discussion" = "https://github.com/\[github_id\]/\[module_name\]/discussions"'''
        template += discussion_block

    return template


# endregion

# ******************************************************
# region Utils


def create_skeleton(name_space: str, module_name: str, base_dir: str) -> None:
    module_name = module_name.replace("-", "_")

    path = os.path.join(
        base_dir,
        f"src/{name_space}/{module_name}",
    )

    os.makedirs(path, exist_ok=True)
    with open(f"{path}/__init__.py", "w") as f:
        f.write("# Init file for the module")


setup_env_template = r"""\[bin_bash\]

read -p "Please enter the Python version you want to use (e.g., 3.9): " PYTHON_VERSION

conda create --name \[module_name\] python=$PYTHON_VERSION -y

conda activate \[module_name\]

pip install -r requirements.txt
pip install -r requirements_test.txt
pip install -r requirements_dev.txt

"""


def generate_setup_env_script(
    module_name: str, setup_env_template: str, base_dir: str
) -> None:
    dir = os.path.join(base_dir, "scripts")

    os.makedirs(dir, exist_ok=True)
    path = f"{dir}/setup_env.sh"

    with open(path, "w") as file:
        script = format_insert(
            setup_env_template, module_name=module_name, bin_bash="# !bin/bash"
        )
        file.write(script)

    print(
        f"Now, you can access the module name {module_name} in your terminal by $MODULE_NAME"
    )
    print("To generate an conda env for your new module, run following command.")
    print(f"cd {base_dir}")
    print("source scripts/setup_env.sh")


def generate_requirements(dependencies_f: str, base_dir: str):
    os.makedirs(base_dir, exist_ok=True)

    dependencies_f = dependencies_f.replace('"', "").replace(",", "")
    with open(f"{base_dir}/requirements.txt", "w") as file:
        file.write(dependencies_f)


def generate_toml(template: str, kwargs: Kwargs, base_dir: str):

    template: str = add_options(template, options=options)

    pyproject_body: str = format_insert(template, **kwargs.model_dump())

    topics_f: str = format_insert_loop(topics_t, kwargs_list={"topic": kwargs.topics})
    dependencies_f: str = format_insert_loop(
        dependencies_t, kwargs_list={"dependency": kwargs.dependencies}
    )

    if dependencies_f == '"",':
        dependencies_f = ""

    pyproject_body: str = format_indent(
        pyproject_body,
        topics_f=topics_f,
        dependencies_f=dependencies_f,
    )

    os.makedirs(base_dir, exist_ok=True)

    path = os.path.join(base_dir, "pyproject.toml")

    with open(path, "w") as file:
        file.write(pyproject_body)


def copy_and_paste_extra_requirements(base_dir: str):
    files = ["requirements_dev.txt", "requirements_test.txt"]

    for file in files:
        dest = os.path.join(base_dir, file)
        shutil.copy(file, dest)


def build_setup(template: str, kwargs: Kwargs, base_dir: str) -> None:

    kwargs_skeleton = kwargs.model_copy()
    kwargs_skeleton.name_space = kwargs_skeleton.name_space.replace("-", "/")
    dependencies_f: str = format_insert_loop(
        dependencies_t, kwargs_list={"dependency": kwargs.dependencies}
    )

    generate_toml(template=template, kwargs=kwargs, base_dir=base_dir)

    create_skeleton(
        name_space=kwargs_skeleton.name_space,
        module_name=kwargs_skeleton.module_name,
        base_dir=base_dir,
    )

    generate_setup_env_script(
        module_name=kwargs.module_name,
        setup_env_template=setup_env_template,
        base_dir=base_dir,
    )

    generate_requirements(
        dependencies_f=dependencies_f,
        base_dir=base_dir,
    )

    copy_and_paste_extra_requirements(base_dir)


def generate_repo_info(github_id: str, repo_name: str, **kwarg_safe) -> None:
    info_to_env_json = {
        "repo-folder-root": f"https://github.com/{github_id}/{repo_name}/blob/main/"
    }

    json_string = json.dumps(info_to_env_json, indent=2)

    os.makedirs("env", exist_ok=True)
    open("env/env.json", "w").write(json_string)


# endregion

# ******************************************************
# region User Setup


options = Options(
    # Will you use the discussion session in your repo?
    discussion=False
)

dependencies = """

"""


def split_dependencies(dependencies: str):
    return dependencies.strip().split("\n")


dependencies = split_dependencies(dependencies)

# Define the general information of your package

repo_name = module_name = "module_name"

kwargs = Kwargs(
    name="Sisung Kim",
    email="sisung.kim1@gmail.com",
    github_id="crimson206",
    repo_name=repo_name,
    version="0.1.0",
    name_space="crimson",
    module_name=module_name,
    description="Your package description.",
    topics=["Topic :: Software Development :: Libraries :: Python Modules"],
    dependencies=dependencies,
)


# endregion

# ******************************************************
# region Execution


build_setup(template, kwargs, base_dir=".")

