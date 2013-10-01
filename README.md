ChangesCheckstyle
=================
This script allows you to use more strict check style rules on added changes keeping general rules for legacy code.

- Run [Checkstyle](http://checkstyle.sourceforge.net/) on files changed in last commit.
- Report errors introduced only in last git commit in changed lines.

Prerequisites
-----

- Download [checkstyle.jar][1]
- Install python if needed
- download checkstyle.py
- add execution permission: chmod +x checkstyle.py

Run
---

- ./checkstyle.py -c checkstyle_rules.xml -d path/to/project


[1]: http://checkstyle.sourceforge.net/

