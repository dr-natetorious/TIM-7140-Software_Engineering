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

@CALL %base_path%..\..\notebook\launch.bat %cd%