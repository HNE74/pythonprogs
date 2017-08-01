############################################
# boidSwarmMod.py
# Implements logic of swarm of boids.
# by Heiko Nolte / August 2010
# distributed: GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
############################################

from vector2DMod import *
from math import *

# The Boid is an individual entity
class Boid():

    def __init__(self, position, velocity):
        self.pos = position;
        self.vel = velocity;
        self.velChange = None;

# Defines and manages a swarm of boids belonging together
class BoidSwarm():

    def __init__(self, border=None):
        self.target = None
        self.obstacle = None
        self.border = border
        self.boids = []
        self.readBoidDefinitions()

    # Read boid definitions and initialize swarm
    def readBoidDefinitions(self):
        boidPos = Vector2D(300.0, 300.0)
        boidVel = Vector2D(0.2, 0.2)
        boid = Boid(boidPos, boidVel)
        self.boids.append(boid)

        boidPos = Vector2D(300.0, 320.0)
        boidVel = Vector2D(0.3, 0.2)
        boid = Boid(boidPos, boidVel)
        self.boids.append(boid)

        boidPos = Vector2D(380.0, 410.0)
        boidVel = Vector2D(0.2, -0.36)
        boid = Boid(boidPos, boidVel)
        self.boids.append(boid)

        boidPos = Vector2D(390.0, 430.0)
        boidVel = Vector2D(-0.6, 0.2)
        boid = Boid(boidPos, boidVel)
        self.boids.append(boid)
        
        boidPos = Vector2D(100.0, 430.0)
        boidVel = Vector2D(-0.1, 0.2)
        boid = Boid(boidPos, boidVel)
        self.boids.append(boid)
        
        boidPos = Vector2D(200.0, 300.0)
        boidVel = Vector2D(0.2, 0.2)
        boid = Boid(boidPos, boidVel)
        self.boids.append(boid)

        boidPos = Vector2D(200.0, 320.0)
        boidVel = Vector2D(0.3, 0.2)
        boid = Boid(boidPos, boidVel)
        self.boids.append(boid)

        boidPos = Vector2D(480.0, 410.0)
        boidVel = Vector2D(0.2, -0.36)
        boid = Boid(boidPos, boidVel)
        self.boids.append(boid)

        boidPos = Vector2D(320.0, 430.0)
        boidVel = Vector2D(-0.6, 0.2)
        boid = Boid(boidPos, boidVel)
        self.boids.append(boid)
        
        boidPos = Vector2D(150.0, 430.0)
        boidVel = Vector2D(-0.1, 0.2)
        boid = Boid(boidPos, boidVel)
        self.boids.append(boid)

    # Add boid to the swarm
    def addBoid(self, boid):
        self.boids.append(boid)

    # Remove boid from the swarm
    def removeBoid(self, boid):
        self.boids.remove(boid)

    # Update to positions of the boids in the swarm
    def updateBoids(self):
        # Iterate over boids and calculate change vector
        for boid in self.boids:
            # Fetch velocity delta vectors
            v1 = self.calcFlyTowardsCentre(boid)
            v3 = self.calcMatchVelocity(boid)
            if self.target is not None:
                v5 = self.chaseTarget(boid)
            if self.obstacle is not None:
                v6 = self.avoidObstacle(boid)

            # Add velocity deltas to boid velocity vector
            boid.velChange = boid.vel.addVec(v1); 
            boid.velChange = boid.velChange.addVec(v3);
            if self.target is not None:
                boid.velChange = boid.velChange.addVec(v5); 
            if self.obstacle is not None:
                boid.velChange = boid.velChange.addVec(v6);                 
            
            # Limit boid velocity
            self.limitVelocity(boid)  
            
            # Let boids keep their distance
            v2 = self.calcKeepDistance(boid) 
            boid.velChange = boid.velChange.addVec(v2);
            
            # Boids mustn't leave borders
            v4 = self.boundPosition(boid)
            boid.velChange = boid.velChange.addVec(v4); 
      
        # Apply boid's change vectors
        for boid in self.boids:
            # Update boid position according to velocity
            boid.vel = boid.velChange
            boid.pos = boid.pos.addVec(boid.vel);

    # Boids try to fly towards the centre of mass of neighbouring boids
    def calcFlyTowardsCentre(self, boid):
        # Init position total
        totalPos = Vector2D(0, 0)

        # Iterate over boids and calculate their position total
        for other in self.boids:
            # Ignore oneself
            if other == boid:
                continue

            # Add total
            totalPos = totalPos.addVec(other.pos)

        # Calculate average pos
        avPos = totalPos.divScalar(len(self.boids) - 1)
        result = avPos.subVec(boid.pos).divScalar(50.0)
        return result

    # Boids try to keep a small distance away from other boids
    def calcKeepDistance(self, boid):
        # Init position total
        corr = Vector2D(0, 0)

        # Iterate over boids and calculate their position total
        for other in self.boids:
            # Ignore oneself
            if other == boid:
                continue

            # Calculate correction amount
            diff = boid.pos.subVec(other.pos)
            diff = diff.mulScalar(2)
            if diff.mag() < 10:
                corr = corr.subVec(diff)

        return corr

    # Boids try to match velocity with near boids
    def calcMatchVelocity(self, boid):
        # Init position total
        perceivedVel = Vector2D(0, 0)

        # Iterate over boids and calculate their volicity total
        for other in self.boids:
            # Ignore oneself
            if other == boid:
                continue

            # Add perceived velocity
            perceivedVel = perceivedVel.addVec(other.vel)
            
        # Calculate total velocity adaption
        perceivedVel = perceivedVel.divScalar(len(self.boids) - 1)
        result = perceivedVel.subVec(boid.vel).divScalar(20.0)
            
        return result
    
    # Bound boid position in accordance with border rect member
    def boundPosition(self, boid):
        xmin = self.border.x
        ymin = self.border.y
        xmax = self.border.width
        ymax = self.border.height
        corrVel = Vector2D(0,0)
        
        # Check horizontal bounds
        if boid.pos.x < xmin:
            corrVel.x = 10
        elif boid.pos.x > xmax:
            corrVel.x = -10
            
        # Check vertical bounds
        if boid.pos.y < ymin:
            corrVel.y = 10
        elif boid.pos.y > ymax:
            corrVel.y = -10
        
        return corrVel  
    
    # Limits the boids overall movement speed
    def limitVelocity(self, boid):
        # Speed limit
        vlim = 10.0
        
        # The boids current speed as magnitude of velocity vector
        speed = boid.vel.mag()
        
        # Limit speed if necessary
        if speed > vlim:
            boid.velChange = boid.vel.divScalar(speed).mulScalar(vlim)
            
    # Chase a particular target
    def chaseTarget(self, boid):
        result = (self.target.subVec(boid.pos)).divScalar(100.0)
        return result
    
    # Avoid a particular obstacle
    def avoidObstacle(self, boid):
        dist = (boid.pos.subVec(self.obstacle)).divScalar(100.0)
        magnitude = dist.mag();
        direction = dist.divScalar(dist.mag());
        absVel = 5.0 - magnitude
        if absVel < 0.0:
            absVel = 0.0
        else:
            absVel = pow(absVel, 2) / 3
        result = direction.mulScalar(absVel)
        
        return result
            








