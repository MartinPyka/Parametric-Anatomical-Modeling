pam-blender - PAM (Parametric Anatomical Modeling)
==================================================

Parametric Anatomical Modeling is a method to translate large-scale anatomical data into spiking neural networks.
PAM is implemented as a [Blender](http://www.blender.org) addon.

![Hippocampal model](https://bitbucket.org/repo/EaAEne/images/1007682870-hippocampal_model.png)

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
* Python data-import module for [NEST Framework](nest) available at **missing link**.

[nest]: http://www.nest-initiative.org

Installation
------------

1. Download the latest official release ([a complete list can be found here](https://bitbucket.org/rub-hippo/parametric-anatomical-modeling/downloads)) or get a snapshot of [this GIT repository](https://bitbucket.org/rub-hippo/parametric-anatomical-modeling/src)

2. Install PAM as Add-On in Blender ([how to install an Add-On](http://wiki.blender.org/index.php/Doc:2.6/Manual/Extensions/Python/Add-Ons)). If you downloaded the ZIP-file, you can directly select the ZIP-file in Blender to install the Add-On.

3. In the 3d view a new panel should appear on the left side, called "PAM". This panel contains function to load and save connectivity data and to visualize them.


Usage - getting started
-----------------------

The repository contains two examples, a very simple one and the hippocampal model, which could help to understand how to use PAM.

The [Wiki](https://bitbucket.org/rub-hippo/parametric-anatomical-modeling/wiki/Home) contains a list of all mapping techniques and a description of the approach used to generate synapses.

Here is a list of videos that introduce PAM and show some features of it.

An importer of with PAM generated data to [NEST](http://www.nest-initiative.org/) can be found [here](https://bitbucket.org/rub-hippo/pam-utils)

Contribute
----------
PAM is continuously under development. Any support and active participation in the development of PAM is very much welcome.

One long-term goal of our research is to structurally and functionally compare brain structures across different species using PAM. Therefore, we are looking for people who can assist us in creating the anatomical layout of brain structures and the projections of neurons across neural layers.

Contact
-------

Dr. Martin Pyka
Mercator Research Group "Structure of Memory", Ruhr-University Bochum

m.pyka at rub.de
+49-234- 32 24682


License
-------

Source code and documentation copyright (c) 2013-2014 Martin Pyka, Sebastian Klatt  
pam-blender is licensed under the GNU GPL v2 License (GPLv2). See `LICENSE.md` for full license text.