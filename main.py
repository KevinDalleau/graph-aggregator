# -*- coding: utf-8 -*-
"""
Created on Thu Jun 23 13:45:22 2016

@author: kevindalleau
"""

import numpy
from scipy.sparse import csr_matrix
from scipy.io import mmwrite
import csv

actors = numpy.loadtxt("./actors.csv",delimiter=",", dtype="string")[1:]
movies = numpy.loadtxt("./movies.csv",delimiter=",", dtype="string")[1:]
offset = len(movies)
size = len(actors)+len(movies)
line = [0] * size
print(range(offset,len(actors)))
#adj = csr_matrix((size,size), dtype = numpy.int8)
def get_actor_id(actor_name):
    try:
        actor_id = numpy.nonzero(actors=='"'+actor_name+'"')[0][0]+offset
    except IndexError:
        actor_id=-1
    return actor_id

def get_movie_id(movie_name):
    try:
        movie_id = numpy.nonzero(movies=='"'+movie_name+'"')[0][0]
    except IndexError:
        movie_id = -1
    return movie_id

links = numpy.loadtxt("./imdb_sss.csv",delimiter=",", dtype="string")[1:]
i=0
movie = -1

for x in links:
    if get_movie_id(x[0]) != movie:
	with open("adjmovie.csv", "a") as f:
	    writer = csv.writer(f, delimiter=",", lineterminator="\n")
	    writer.writerow(line)
        movie = get_movie_id(x[0])
        line[get_actor_id(x[1])] = 1
    else:
        line[get_actor_id(x[1])] = 1
    i += 1
    print(i)


