'''
Created on 08.10.2017

@author: hnema
'''
from __future__ import division
import math

def vector_add(v, w):
    return [ v_i + w_i for v_i, w_i in zip(v, w)]

def vector_subtract(v, w):
    return [ v_i - w_i for v_i, w_i in zip(v, w)]

def vector_sum(vectors):
    return reduce(vector_add, vectors)

def vector_diff(vectors):
    return reduce(vector_subtract, vectors)

def scalar_multiply(c, v):  
    return [ c * v_i for v_i in v]

def vector_mean(vectors):
    n = len(vectors)
    return scalar_multiply(1/n, vector_sum(vectors))

def dot(v, w):
    return sum(v_i * w_i for v_i, w_i in zip(v, w))

def sum_of_squares(v):
    return dot(v, v)

def magnitude(v):
    return math.sqrt(sum_of_squares(v))

def squared_distance(v, w):
    return sum_of_squares(vector_subtract(v, w))

def distance(v, w):
    return magnitude(vector_subtract(v, w))

def shape(A):
    num_rows = len(A)
    num_cols = len(A[0])
    return num_rows, num_cols

def get_row(A, i):
    return A[i]

def get_column(A, j):
    return [A_i[j] for A_i in A]

def make_matrix(num_rows, num_cols, entry_fn):
    return [[entry_fn(i, j)
            for j in range(num_cols)]
            for i in range(num_rows)]
    
def set_matrix_value(row, col, matrix, value):
    r_l = get_row(matrix, row)
    del r_l[col]
    r_l.insert(col, value)
    del matrix[row]
    matrix.insert(row, r_l)

def is_diagonal(i, j):
    return 1 if i == j else 0

def empty(i, j):
    return 0

def main():
    v1 = [5, 6]
    v2 = [3, 2]
    print vector_add(v1, v2)
    print vector_subtract(v1, v2)
    print scalar_multiply(2, v2)
    print
    
    print dot(v1, v2)
    print sum_of_squares(v1)
    print magnitude(v1)
    print squared_distance(v1, v2)
    print distance(v1, v2)
    print 

    vl = [[1.0, 2.0], [3.0, 5.0], [6.0, -2.0]]
    print vector_sum(vl)
    print vector_diff(vl)
    print vector_mean(vl)
    print
    
    identity_matrix = make_matrix(10, 10, is_diagonal)
    for row in identity_matrix:
        print row
 
    print
    empty_matrix = make_matrix(10, 10, empty)
    set_matrix_value(3, 4, empty_matrix, 5)
    for row in empty_matrix:
        print row  


if __name__ == '__main__':
    main()