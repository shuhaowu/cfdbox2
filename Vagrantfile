# -*- mode: ruby -*-
# vi: set ft=ruby :

REQUIRED_PACKAGES = %w{
   git
   tar
   gcc
   make
   gcc-c++
   python-devel
   python-argparse
   vim
   ncurses-devel
   libselinux-python
   zlib-devel
   bzip2-devel
   openssl-devel
   ncurses-devel
   sqlite-devel
   readline-devel
   gdbm-devel
   db4-devel
}

Vagrant.configure(2) do |config|
  config.vm.define "server" do |server|
    server.vm.box = "centos/6"
    server.vm.provision :shell, :inline => "mkdir -p /home/vagrant/.ssh && echo -e '#{File.read("#{Dir.home}/.ssh/id_rsa.pub")}' >> '/home/vagrant/.ssh/authorized_keys'"
    # workaround centos yum problems
    server.vm.provision :shell, :inline => "yum remove -y centos-release-SCL && yum install -y centos-release-SCL"
    server.vm.provision :shell, :inline => "yum install -y #{REQUIRED_PACKAGES.join(' ')}"

    server.vm.synced_folder ".", "/vagrant", disabled: true
    server.vm.synced_folder ".", "/home/vagrant/cfdbox2"

    unless ENV["NO_ANSIBLE"]
      server.vm.provision "ansible" do |ansible|
        ansible.verbose = "vv"
        ansible.playbook = "provisioning/all.yml"
      end
    end
  end
end
