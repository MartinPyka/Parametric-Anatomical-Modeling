# PAM - Parametric Anatomical Modeling in Blender

Parametric Anatomical Modeilng is a method to translate large-scale anatomical data into spiking neural networks.

![hippocampal_model.png](https://bitbucket.org/repo/EaAEne/images/1007682870-hippocampal_model.png)

## Features ##

### Complex connection patterns between neurongroups are described by layers and a combination of simple mapping techniques between layers ###

![mapping.png](https://bitbucket.org/repo/EaAEne/images/3024196489-mapping.png)

2d layers define the location of neurons and their projection directions. Probability functions for pre- and post-synaptic neurons are applied on the surface of the synaptic layer to determine connections between two neuron groups.

### Anatomical properties can be defined along global and local anatomical axes ###

![local_global_axes.png](https://bitbucket.org/repo/EaAEne/images/3750354801-local_global_axes.png)

A layer is defined as a 2d manifold (a deformed 2d surface). Each point on a layer is described by x, y, and z coordinates and u,v-coordinates which may correspond to anatomical axes.

### Spatial distances within and between layers can be combined to calculate connection distances ###

![delays.png](https://bitbucket.org/repo/EaAEne/images/730784673-delays.png)

In order to create axonal and dendritic connections in 3d space, neuron positions are mapped between layers. When the internal mesh-structure between layers is identical, neurons can be directly mapped using topological mapping. Otherwise, normal-, Euclidean- and random-based mapping are available.

### Conversion into an artificial neural network simulation

* CVS-export of connections and distances for usage in an arbitrary neural network simulator
* Importer for [NEST](www.nest-initiative.org) available