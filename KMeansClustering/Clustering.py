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

    def train(self, inputs, figure):
        # Initialize cluster points randomly from input
        self.means = random.sample(inputs, self.k)
        
        it_cnt = 0
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
            
            if figure != None and it_cnt < 8:
                it_cnt = it_cnt + 1
                plot_clusters(inputs, self.means, self.assignments, figure, it_cnt)
    
    def squared_clustering_errors(self, inputs, k_param):
        # Calculates the total error of all input points for a certain number of cluster points (k)
        self.k = k_param
        self.train(inputs, None)
        assignments = map(self.classify, inputs)
        total_error = sum(Vectorops.squared_distance(input, self.means[cluster]) for input, cluster in zip(inputs, assignments))
        return total_error
    
def plot_clusters(input_points, cluster_points, assignments, figure, subplot_id):

    if figure != None:
        figure.add_subplot(2,4,subplot_id)
        figure.settitle = 'Iteration: ' + str(subplot_id)

    # Create dictionary with cluster point index numbers and empty assignments
    c_dict = {}
    k_cnt = len(cluster_points)
    for c_ndx in range(k_cnt):
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
            
    if figure != None:
        plt.grid(True)

def plot_error_graph(inputs, clusterer):
    # Plots graph of total squared error for k cluster points and the given input points    
    k_cnt = range(1, len(inputs) + 1)    
    errors = [clusterer.squared_clustering_errors(inputs, k) for k in k_cnt]

    plt.plot(k_cnt, errors)
    plt.xticks(k_cnt)
    plt.xlabel('k')
    plt.ylabel('total squared error')
    plt.title('Total Error by Number of Clusters')
    print errors

def onclick(event):
    print event

def main():
    #inputs = [ (-50, 20), (-50, 0), (-52, 5), (-40, 10), (20, 10), (15, 5)]
    inputs = [(random.randint(0,100), random.randint(0,100)) for num in range(25)]
    
    random.seed(0)    
    clusterer = KMeans(1)  
    clusterer.train(inputs, None)
    plot_error_graph(inputs, clusterer) 
    plt.show(block=True) 
    print 'Enter K Value>'
    try:
        k_select = int(raw_input())   
    except:
        print 'Invalid K Value entered. Setting k to 3.'
        k_select = 3
    
    clusterer = KMeans(k_select)
    figure = plt.figure(1)
    plt.title("K Means Clustering Algorithm Iterations - K=" + str(k_select)) 
    clusterer.train(inputs, figure)
    plt.show(block=True)
    
    plt.title("K Means Clustering Algorithm Result - K=" + str(k_select))
    plot_clusters(inputs, clusterer.means, clusterer.assignments, None, 0)   
    plt.show(block=True)

if __name__ == '__main__':
    main()