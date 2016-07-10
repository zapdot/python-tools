# python-tools
A set of scripts and tools that can be useful for dev machines or cronjobs.

We're not professional python developers by any means, but we hope they can be useful for you too!

## Dependencies!
Before you get any further, you should probably grab the following projects too!

Our internal version of Siesta (branch: dev)
* https://github.com/zapdot/siesta

zaplib: the basis for most of these scripts.
* https://github.com/zapdot/zaplib

## Installation
None for these set of tools. Follow the installation guides for the dependencies.

It may be useful to add the "scripts" folder to your PATH variable in your environment if you'll be using them often. 

## Overview

### cron/ucb_daily.py
Rather than elect for Unity's continuous builds on any changes, we have a script check to see if there have been commits to our develop branch since the last build every morning. If there have been, we kick a build so the team will have something fresh by the time they start their day.

### scripts/bump_version.py
Bump the version numbers on our projects. Not only updates the file, but safely commits the file to git as well, stashing/restoring any changes you may have currently had.

#### Usage
    $ bump_version.py [-h] (--major | --minor | --patch | --set version)
        --major        bump the major version.
        --minor        bump the minor version.
        --patch        bump the patch version.
        --set version  set the version to a higher number

- Absence of all arguments will print the current version.
- Expects to find `version_data.json`, with a parent path of `Resources/AppInfo`
- `version_data.json` should be formatted as such:
```
{
    "majorVersion": 0,
    "minorVersion": 0,
    "patchVersion": 0
}
```

### scripts/cbox.py
Terminal-based json editor for ConfigBox.

#### Usage
    $ cbox.py [-h] id [key [key ...]] 
        positional arguments:
          id                    alphanumeric id for your config.
          key                   key(s) to traverse the data
        optional arguments:
          --value val           set the path to a value
          --list val [val ...]  set the path to a list of values
          --template name       merges in any new keys from template, warns of
                                obsolete keys.
          --setup path          setup the given path for ConfigBox.

#### Examples:

##### List entire config

    $ cbox.py api
    api:
      github: c5e8048185139f8ab01f27b77375daa0
      pivotal: dc5fc33420ca2aedde8887dd7a901810
      slack: ** NOT SET **
      cloudbuild: 7d84dbef159cbc5f6d1052262ae962da

##### List specific variable

    $ cbox.py api github
    api[github]:
      c5e8048185139f8ab01f27b77375daa0

##### Set specific variable

    $ cbox.py api github --value somethingnew
    > api updated.

    $ cbox.py api github
    api[github]:
      somethingnew

##### Create a project based on a template

    $ cbox.py great_project --template project
    > great_project created.

    $ cbox.py great_project
    great_project:
      git:
        owner: ** NOT SET **
        repo: ** NOT SET **
      pivotal:
        project_id: ** NOT SET **
      slack:
        channel: ** NOT SET **
      cloudbuild:
        project_id: ** NOT SET **
        org_id: ** NOT SET **

    $ cbox.py great_project git owner --value zapdot
    > great_project updated.

    $ cbox.py great_project git repo --value great_project
    > great_project updated.

##### List group (and subsequent children)

    $ cbox.py great_project git
    great_project[git]:
      owner: zapdot
      repo: great_project
