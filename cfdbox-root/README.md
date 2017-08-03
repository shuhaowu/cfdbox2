Server CFDBox Utilities
=======================

All software here are written to target Python 2.6 as machines may be on ancient RHEL/CentOS installations.

Furthur, all software are designed to run from your home directory without the need of root privileges. This is actually quite a challenging task to accomplish given how Linux distributions usually operate. The environment must be setup correctly. Part of this document will describe the assumed setup. A separate repository is offered to setup the environment via [Ansible][ansible].

[ansible]: http://www.ansible.com/

Server Environment
------------------

All software will be installed into the user's home directory. Inside the $HOME directory, the presumed structure is as follows:

    cfdbox-server/ # contains all files from this directory ()
        venv/ # the virtual environment will be installed here
        cfx/
        ...
    bin/  # executable here can be directly called from shell
        cfdbox-server
        cfxbox
    cfdboxrc.d/ # Store anything that you want to be sourced into your env
        sourceall # sources everything recursively in this directory
        pathrc # modifies the path so we can compile/invoke support programs
        cfxrc
        sftprc
        towncrierrc
        ...
    support/ # support programs like tmux and what not, in LSB format, almost
        bin/
        include/
        lib/
        share/
        sources/ # here lives the sources of all the programs we compile

The script `bootstrap` will setup this structure. Furthermore it is recommended that you use the ansible provisioning system for this rather than setting it up manually. See the `provisioning` directory for detail.

CFX
---

These are software I've written for running and examining CFX simulations.

### runner ###

For running CFX.

### monitor ###

For monitoring CFX runs.

### trnmover ###

For automatically moving transient files periodically.

### exporter ###

Software that helps exporting data from CFX simulations. It can take transient files from SFTP and export it one step at a time, or export everything all at once.

