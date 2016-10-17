Ansible lookup plugin

# Installation

Create a directory named <code>lookup\_plugins</code> and copy the csvrecord.py file there.  Declare the path to the directory in the <code>[defaults]</code> section of the ansible.cfg

```
[defaults]
lookup_plugins = ./plugins/lookup_plugins/:/usr/share/ansible_plugins/lookup_plugins:../lookup_plugins:./lookup_plugins
```

For more information regarding plugins check the [plugins documentation](http://docs.ansible.com/ansible/developing_plugins.html).

# Usage

This plugin creates a list of items, each one being a line of the csv file, and provides this list to the task. This allows, a template for example, to iterate over this list of items.

```
- name: generating ap conf files 
  template: "src=ap.cfg.j2 dest=objects/ap.cfg mode=0644"
  with_csvrecord: "file=csv/ap.csv"
```

# Example

Using the file <code>ap.csv</code>:

```
name,ip,alias
SH-2220,10.1.11.23,SH-2220 (RH999)
MN-1005,10.1.11.24,MN-1005 (MN-200)
```

with the file <code>ap.cfg.j2</code>:

```
{% for host in item %}
# -----------------
# System Name: {{ host.name[5:] }}
# -----------------
define host{
       use                     generic-switch  ; Inherit default values from a template
       host_name               {{ host.name }} ; The name we're giving to this server
       alias                   {{ host.name }} ; A longer name for the server
       address                 {{ host.ip }}   ; IP address of the server
       hostgroups   switches        ; Host groups this switch is associated with
       contact_groups          admins
}

{% endfor %}
```

The following output file <code>ap.cfg</code> is obtained:

```
# -----------------
# System Name: SH-2220 (RH999)
# -----------------
define host{
       use                     generic-host-remote
       host_name               SH-2220
       alias                   SH-2220 (RH999)
       address                 10.1.11.23   
       hostgroups              remotes_inet900
       statusmap_image         switch.gd2
       icon_image              switch.gif
       contact_groups          admins
}
# -----------------
# System Name: MN-1005 (MN-200)
# -----------------
define host{
       use                     generic-host-remote  
       host_name               MN-1005 
       alias                   MN-1005 (MN-200) 
       address                 10.1.11.24   
       hostgroups              remotes_inet900
       statusmap_image         switch.gd2
       icon_image              switch.gif
       contact_groups          admins
}
```

