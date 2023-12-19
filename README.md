# 2023 IEEE SciVis Contest
### Neuronal Network Simulations of the Human Brain

Authors: Seda den Boer, Dominique Weltevreden

Course: Scientific Visualisation and Virtual Reality, UvA

Semester: Fall 2023

#### Research question
How does setting individual calcium targets for neurons influence the general brain activity and connectivity?

#### Data preparation
This repository contains code to prepare the contest data for visualisation in ParaView. The full instructions and code are included in `data_preparation.ipynb`. 

### Requirements
Required packages and correct versions can be downloaded with `pip install -r requirements.txt`

### Prerequisites
* Create an empty `data` filemap.
* Download the 2023 IEEE SciVis Contest `viz-no-network` and `viz-calcium` data from the following page https://rwth-aachen.sciebo.de/s/KNTo1vgT0JZyGJx, and store it in `data` filemap.
* Unzip the monitors files.
* Make sure to create two new empty folders `monitors_extracted` and `files` in each simulation filemap.

Below the necessary data (filemaps) are shown:
```
└───data
    ├───viz-calcium
    │   ├───files
    │   ├───monitors
    │   │   • 0_{neuron_id}.csv
    │   ├───monitors_extracted
    │   └───positions
    │       • rank_0_positions.txt
    │   • calcium_targets.txt
    └───viz-no-network
        ├───files
        ├───monitors
        │   • 0_{neuron_id}.csv
        ├───monitors_extracted
        └───positions
            • rank_0_positions.txt
```
### Visualisation videos 
In the filemap `vis_vids` the visualisation videos of the final visualisation from ParaView are stored.

### Extra: vtk visualisation try-out
The `vtk_connection_vis.py` file contains code to render a visualisation of the brain with its neurons and connections.