# Tooling

The authors of the [Android-DataSet.pdf](../Readings/Android-DataSet.pdf) rely on Stowaway for their results.  However, that tool was superseded three years before their publication. Similarly, Sonar is now SonarQube. This page exists for tracking the necessary changes to reproducing the results.

## PScout: Analyzing the Android Permission Specification (2012)

Kathy Wain Yee Au, Yi Fan Zhou, Zhen Huang and David Lie.  PScout: Analyzing the Android Permission Specification. In the Proceedings of the 19th ACM Conference on Computer and Communications Security (CCS 2012). October 2012.  [PScout](https://security.csl.toronto.edu/pscout/).

> Stowaway is extremely out of date and will not produce accurate results for a corpus of modern Android apps. You should use PScout instead, which has been updated to handle modern apps. If you still want to see Stowaway for historical reasons, e-mail me (felt at chromium dot org) and I'll share a copy with you

## SonarQube

With version 8.7 engineers can analyze [Java and its Bytecode](https://docs.sonarqube.org/latest/analysis/languages/java/).  Their website contains [Docker compose automation](https://docs.sonarqube.org/latest/setup/install-server/) and other relevant information.

Juneja (2019) has a [blog with screenshots](https://tech.olx.com/sonarqube-integration-in-android-application-part-1-37041b0379) demonstrates setting up an Android project.
