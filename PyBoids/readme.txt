PyBoids Version 1.0
by Heiko Nolte, written August 2010
===============================================

This code is distributed under GNU GENERAL PUBLIC LICENSE, Version 3.

To use install Python 2.x and PyGame API.

Implements more or less the boids algorithm introduced by Conrad Parker under 
http://www.vergenet.net/~conrad/boids/pseudocode.html.

Use left mouse button to set a target the boids have to chase. The right
mouse button sets an obstacle the boids are trying to avoid.

The file boidViewMod ist the entrypoint for the boid demo. It's used to render
the boids on screen using the PyGame API. The file boidSwarmMod implements 
the boids algorithm. In vector2DMod a 2 dimensional vector with basic operations
is implemented.



