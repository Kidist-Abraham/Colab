# Colab

Check out the [Collab Website](https://collabk.herokuapp.com/)

A collaboration platform for open source projects.

This we application facilitates collaboration on open source projects among developers around the world.
It helps people to have a place to announce a project that they make open for collaboration. It also helps people who want to collaborate on open source projects to have a place to find projects that align with their needs

## Run the app

1. Create db

`createdb colab`


2. Create Python virtual environment and install libraries.

Run the following

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirement.txt 
```

3. initialize stack and sector tables

Run

```
python add_git_stack_to_db.py
python add_sectors_to_db.py
```

4. Run the app

`flask run`



## Features 

- Register/login as a user

- Post a project by defining the description, sector

- Filter projects by sector, programming language/framework

- Being able to set a preference and have an option to show only preffered projects

- Display a collaboration information on a user profile (like the projects that they collaborated to). This is done via scheduled task

- Display collaborators of a project that are also users of this Web app. This is done via scheduled task


## Schema

[See schema](https://dbdiagram.io/d/624c4d07d043196e39fd1b67)


## External API

[GitHub API](https://docs.github.com/en/rest)


