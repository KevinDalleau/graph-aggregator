# -*- coding: utf-8 -*-
"""
Created on Thu Jun 23 13:45:22 2016

@author: kevindalleau
"""

import numpy
from scipy.sparse import csr_matrix
from scipy.io import mmwrite
import csv
import rdflib

def loadIndividuals(graph):
    queryString = "SELECT ?individuals ?individualId WHERE {?individuals <http://www.graph.com/nodeType/>  \"individual\" . ?individuals <http://graph.com/identifier> ?individualId.}"
    res = graph.query(queryString)
    output = {}
    for row in res:
        name =  str(row[0]).replace("http://graph.com/individual/","")
        indId = int(row[1])
        output[name] = indId
    return output

def loadAttributes(graph,offset):
    queryString = "SELECT ?attributes WHERE {?attributes <http://www.graph.com/nodeType/>  \"attribute\".}"
    res = graph.query(queryString)
    output = {}
    i=1
    for row in res:
        name = str(row[0]).replace("http://graph.com/","")
        output[name] = i+offset
        i+=1
    return output

def getSparseGraph(graph, individuals, attributes):
    queryString = "SELECT DISTINCT ?individual ?attribute WHERE {?individual <http://www.graph.com/nodeType/> \"individual\". ?individual <http://graph.com/relation/linked> ?attribute. ?attribute <http://www.graph.com/nodeType/> \"attribute\"}"
    res= graph.query(queryString)
    output = {}
    for row in res:
        individualName = str(row[0]).replace("http://graph.com/individual/","")
        attributeName = str(row[1]).replace("http://graph.com/","")
        individualIndex = individuals[individualName]
        attributeIndex = attributes[attributeName]
        if individualIndex not in output:
            output[individualIndex] = []
        if attributeIndex not in output:
            output[attributeIndex] = []
        output[individualIndex].append(attributeIndex)
        output[attributeIndex].append(individualIndex)
    return output


    
graph = rdflib.Graph()
graph.load("./data/outputvote.rdf", format="nt")


individualsDict = loadIndividuals(graph)
individualsList = sorted(individualsDict.values())
offset = len(individualsDict)
attributesDict = loadAttributes(graph,offset)
sparse = getSparseGraph(graph,individualsDict,attributesDict)

