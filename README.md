#Printer-Installer Server

A django website for the [Printer-Installer client][pi_client]

###Front Page

![front][front]

--

###Manage Printers
![manage][manage]

--

##Auto Install Script
For the simplest installation on OS X Server 10.7 or higher, run the auto install script by copy and pasting this into your terminal.
```
curl -L https://raw.github.com/eahrold/printerinstaller-server/master/OSX/osx_auto_install.command > /tmp/run.sh; chmod u+x /tmp/run.sh ; /tmp/run.sh

```

The script is also avaliable from the OSX folder in the root of this repo.

###Quick Start
To manually setup and configure, you can use [this quick start guide][quick-start]

[add_list]:./docs/images/add_list.png
[add_printer]:./docs/images/add_printer.png
[front]:./docs/images/index.png
[manage]:./docs/images/manage.png
[quick-start]:./docs/quick_start.md
[pi_client]:https://github.com/eahrold/Printer-Installer