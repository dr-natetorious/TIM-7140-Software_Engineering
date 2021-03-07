@ECHO OFF
@ECHO ==================================
@ECHO Launch jupyter notebooks
@ECHO (c) 2020.01.11 Nate Bachmeier
@ECHO ==================================
@REM https://jupyter-docker-stacks.readthedocs.io/en/latest/using/common.html
@REM https://jupyter-docker-stacks.readthedocs.io/en/latest/using/selecting.html#jupyter-scipy-notebook

@SETLOCAL enableextensions enabledelayedexpansion
@SET base_path=%~dp0
@PUSHD %base_path%

@SET local_home_dir=%base_path%home
@IF NOT "%1"=="" (
    @SET local_home_dir=%1
    @ECHO Using custom home directory
)



@SET run_flags=run --rm --name notebook -it -p 8888:8888 --cpus %NUMBER_OF_PROCESSORS%
@SET mount_home=-v %local_home_dir%:/home/jovyan/work
@SET mount_start=-v %base_path%start-notebook.d:/usr/local/bin/start-notebook.d/
@SET notebook_flags=-e RESTARTABLE=yes -e 


@SET notebook_args=%mount_home% %mount_start%
@CALL docker %run_flags% %notebook_args% jupyter/tensorflow-notebook
@rem docker exec -it notebook cat /home/jovyan/.local/share/jupyter/runtime/nbserver-6.json