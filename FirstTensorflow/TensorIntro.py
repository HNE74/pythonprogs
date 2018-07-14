# -*- coding: utf-8 -*-
"""
Created on Sat Jul 14 15:24:32 2018

@author: Nolti
"""

import tensorflow as tf

node_const_1 = tf.constant(3.0, tf.float32, name='const_1')
node_const_2 = tf.constant(3.0, tf.float32, name='const_2')
node_add = tf.add(node_const_1, node_const_2)

a = tf.placeholder(tf.float32, name='a')
node_mul = node_add*a

b = tf.Variable(1.0, tf.float32, name='b')
node_sub = node_mul-b

session = tf.Session()
with tf.Session() as session:
    writer = tf.summary.FileWriter('c:/temp/first_step', session.graph)
    init = tf.global_variables_initializer()
    session.run(init)
    print(session.run(node_sub, {a: 2.0}))

writer.close()
    


