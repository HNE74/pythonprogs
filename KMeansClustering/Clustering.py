'''
Created on 09.03.2018
Implementation and demonstration of the KMeans algorithm. 
Based on chapter 19 of the book "Einfuehrung in Data Science" 
written by Joel Grus / Publisher O'Reilly

Required libraries: Matplotlib
@author: Heiko Nolte
'''

import Vectorops
import random
from matplotlib import pyplot as plt
from matplotlib import colors

class KMeans:
    # This class implements the KMeans algorithm for clustering point by their
    # squared distances to cluster points
    
    def __init__(self, kpoints, verbose = False):
        self.k = kpoints
        self.means = None
        self.verbose = verbose
        self.assignments = None

    def classify(self, input):
        # Assigns input points to cluster points
        return min(range(self.k), key=lambda i: Vectorops.squared_distance(input, self.means[i]))

    def train(self, inputs):
        # Initialize cluster points randomly from input
        self.means = random.sample(inputs, self.k)
        
        while True:
            # Assign input points to cluster points by squared distance calculation
            new_assignments = map(self.classify, inputs)
            if self.verbose:
                print 'Assignments: ' + new_assignments
                print 'Means: ' + self.means
            
            # Return assignment result if no assignements were changed in iteration
            if self.assignments == new_assignments:
                return
            
            self.assignments = new_assignments
            
            # Shift cluster points based on assigned input points
            for i in range(self.k):
                i_points = [p for p, a in zip(inputs, self.assignments) if a == i]
                
                if i_points:
                    self.means[i] = Vectorops.vector_mean(i_points)
    
    def squared_clustering_errors(self, inputs, k_param):
        # Calculates the total error of all input points for a certain number of cluster points (k)
        self.k = k_param
        self.train(inputs)
        assignments = map(self.classify, inputs)
        total_error = sum(Vectorops.squared_distance(input, self.means[cluster]) for input, cluster in zip(inputs, assignments))
        return total_error
    
def plot_clusters(input_points, cluster_points, assignments):

    # Create dictionary with cluster point index numbers and empty assignments
    c_dict = {}
    for c_ndx in range(len(cluster_points)):
        c_dict[c_ndx] = []
    
    # Related assigned input point to cluster point index numbers
    assigned_input_points = zip(assignments, input_points)
    for assigned_point in assigned_input_points:
        c_dict.get(assigned_point[0]).append(assigned_point[1])
 
    colornames = [name for name in colors.cnames.iterkeys()]
     
    color_ndx = 0
    for cluster_ndx in range(len(cluster_points)): 
        color_ndx = color_ndx + 1 
        plt.scatter(cluster_points[cluster_ndx][0], cluster_points[cluster_ndx][1], 100, color=colornames[color_ndx], edgecolor='black')
        for input_point in c_dict.get(cluster_ndx):
            plt.scatter(input_point[0], input_point[1], 40, color=colornames[color_ndx], edgecolor='black')
        
    plt.title("K Means Clustering Algorithm")
    plt.show()    

def plot_error_graph(inputs, clusterer):
    # Plots graph of total squared error for k cluster points and the given input points    
    k_cnt = range(1, len(inputs) + 1)    
    errors = [clusterer.squared_clustering_errors(inputs, k) for k in k_cnt]

    plt.plot(k_cnt, errors)
    plt.xticks(k_cnt)
    plt.xlabel('k')
    plt.ylabel('total squared error')
    plt.title('Total Error by Number of Clusters')
    plt.show()

def main():
    #inputs = [ (-50, 20), (-50, 0), (-52, 5), (-40, 10), (20, 10), (15, 5)]
    inputs = [(random.randint(0,20), random.randint(0,20)) for num in range(20)]
    
    random.seed(0)    
    clusterer = KMeans(1)
    clusterer.train(inputs)
    plot_error_graph(inputs, clusterer) 
    
    clusterer = KMeans(3)
    clusterer.train(inputs)
    result = clusterer.means    
    plot_clusters(inputs, result, clusterer.assignments)

if __name__ == '__main__':
    main()