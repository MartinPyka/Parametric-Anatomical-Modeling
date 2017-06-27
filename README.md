PAM (Parametric Anatomical Modeling)
====================================

Parametric Anatomical Modeling is a method to translate large-scale anatomical data into spiking neural networks.
PAM is implemented as a [Blender](http://www.blender.org) addon.

![hippocampus_rat_01.png](https://bitbucket.org/repo/EaAEne/images/3662544291-hippocampus_rat_01.png)

![spiking.png](https://bitbucket.org/repo/EaAEne/images/4173479826-spiking.png)

[blender]: http://www.blender.org

Features
--------

### Complex connection patterns between neurongroups are described by layers and a combination of simple mapping techniques between layers

![Mapping process](https://bitbucket.org/repo/EaAEne/images/3024196489-mapping.png)

2d layers define the location of neurons and their projection directions.
Probability functions for pre- and post-synaptic neurons are applied on the surface of the synaptic layer to determine connections between two neuron groups.

### Anatomical properties can be defined along global and local anatomical axes

![3d to 2d translation](https://bitbucket.org/repo/EaAEne/images/3750354801-local_global_axes.png)

A layer is defined as a 2d manifold (a deformed 2d surface).
Each point on a layer is described by x, y, and z coordinates and u,v-coordinates which may correspond to anatomical axes.

### Spatial distances within and between layers can be combined to calculate connection distances

![Distance/delay mapping methods](https://bitbucket.org/repo/EaAEne/images/730784673-delays.png)

In order to create axonal and dendritic connections in 3d space, neuron positions are mapped between layers.
When the internal mesh-structure between layers is identical, neurons can be directly mapped using topological mapping.
Otherwise, normal-, Euclidean- and random-based mapping are available.

### Conversion into an artificial neural network simulation

* CVS-export of connection/distance matrix for external use
* Python data-import module for [NEST Framework](nest) available at https://github.com/MartinPyka/Pam-Utils.

[nest]: http://www.nest-initiative.org

Installation
------------

Automatic installation: 
  1. Download the [latest release](https://github.com/MartinPyka/Parametric-Anatomical-Modeling/releases) as a zip file
  2. Open up the Add-on Preferences screen (File -> User Preferences -> Add-ons)
  3. Click `Install from File` and choose the downloaded zip
  4. Make sure the add-on is activated in the list of add-ons
  5. Click `Save User Settings` to always load the add-on on startup

Manual installation:
  1. Clone the [git repository](https://github.com/MartinPyka/Parametric-Anatomical-Modeling) to your computer
  2. Copy the folder `pam` to Blenders add-on folder
    - On Windows 7 and above, the add-on folder is located in `C:\Users\%username%\AppData\Roaming\Blender Foundation\Blender\2.7x\scripts\addons`
    - On Linux, the add-on folder is located in `/home/$user/.config/blender/$version/scripts/addons`
  3. Start up Blender and activate the add-on in the Add-on Preferences (File -> User Preferences -> Add-ons)
  5. Click `Save User Settings` to always load the add-on on startup

In the 3d view three new panels should appear on the left side, called "PAM Mapping", "PAM Modeling" and "PAM Animate. These panels contains functions to load and save connectivity data and to visualize them.


Usage
-----

The repository contains two examples, a very simple one and the hippocampal model, which could help to understand how to use PAM.

The [Wiki](https://github.com/MartinPyka/Parametric-Anatomical-Modeling/wiki) contains a list of all mapping techniques and a description of the approach used to generate synapses.

Here is a list of videos that introduce PAM and show some features of it.

An importer of with PAM generated data to [NEST](http://www.nest-initiative.org/) can be found [here](https://github.com/MartinPyka/Pam-Utils)

Contribute
----------
PAM is continuously under development. Any support and active participation in the development of PAM is very much welcome.

One long-term goal of our research is to structurally and functionally compare brain structures across different species using PAM. Therefore, we are looking for people who can assist us in creating the anatomical layout of brain structures and the projections of neurons across neural layers.

License
-------

Source code and documentation copyright (c) 2013-2015 Martin Pyka, Sebastian Klatt  
pam is licensed under the GNU GPL v2 License (GPLv2). See license file for full text.
