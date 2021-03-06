@ECHO OFF
@ECHO ==================================
@ECHO Deployment Tool
@ECHO Nate Bachmeier - Amazon Solutions
@ECHO ==================================

@SETLOCAL enableextensions enabledelayedexpansion
@SET base_path=%~dp0
@PUSHD %base_path%

@CALL docker build -t fdroid-scrape %cd%
@CALL docker run -it -v %userprofile%\.aws:/root/.aws -v %cd%:/files -v /var/run/docker.sock:/var/run/docker.sock -w /files fdroid-scrape bash

@POPD