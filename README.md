# PyJot - A CLI To-Do Application

The classic to-do application now built around the Command-Line Interface.  
```
$ pyjot add finish up this project already
task added: 'finish up this project already' (priority: 2)
$ pyjot add go outside -p 4
task added: 'go outside' (priority: 4)
$ pyjot list
                          To-Do List                          
+------------------------------------------------------------+
| ID | Priority | Completed | Task                           |
|----+----------+-----------+--------------------------------|
| 1  | 2        | True      | write the README.md            |
| 2  | 4        | False     | finish up this project already |
| 3  | 4        | False     | go outside                     |
+------------------------------------------------------------+
```
You can check out other commands using `pyjot --help` command. 

### Setup and Installation

If you have python(version>=3.12) already installed in your system,  
you can use either of the commands in your terminal:
```
# for ssh
pip install git+ssh://git@github.com:Orykz/PyJot.git

# for https
pip install git+https://github.com/Orykz/PyJot.git
```

**`NOTE: This project is not installed in PyPI (yet)`**

### License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

Copyright (c) 2025 Jero Pardo