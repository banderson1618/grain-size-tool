# README #

The Grain Size Distribution Tool is a spatially explicit network model that estimates grain size (substrate size) at the watershed level at the reach scale. 

### What is this repository for? ###

* This program is meant to model the grain size of the substrate in a reach using the equation found in Snyder et al (2013).

### What inputs do I need to run this tool? ###

* You need a stream network, a precipitation map, and a DEM of the area that you want to analyze. Attempting to run the tool on a stream network that does not have an underlying DEM for the entirety of the network will result in a crash. As such, depending on your inputs, you may also need a polygon that clips your stream network to the extent of the DEM. I suggest using HUC regions.

* In addition, you will need to know what values you want to use for t_c and n. We used n = .04 for most regions, but we found that t_c values vary significantly from region to region.

* Finally, you will need to know what region's Q_2 equation is appropriate for your analysis. The program currently supports Washington Q_2 equations. There are no plans in the future to expand this support to other states. If you want to use this program for an area outside of Washington, you can modify the code yourself to use the Q_2 equation desired. Simply go to the function findQ_2() and modify it as desired. If you need to use variables besides flow accumulation and precipitation, you will have to add support for them yourself. Otherwise, the function is entirely modular, and should work fine as long as it returns a number.

In order to use the function properly, you will need to enter your "region number", a number that's identified with a particular Q_2 equation. You can find your region at the link below:

https://pubs.usgs.gov/fs/fs-016-01/

### Who do I talk to? ###

* Braden Anderson
	banderson1618@gmail.com
