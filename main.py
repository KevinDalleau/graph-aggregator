# -*- coding: utf-8 -*-
"""
Created on Thu Jun 23 13:45:22 2016

@author: kevindalleau
"""

import rdflib
import scipy
import numpy
import cProfile
from scipy.sparse import dok_matrix

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
            output[individualIndex] = set()
        if attributeIndex not in output:
            output[attributeIndex] = set()
        output[individualIndex].add(attributeIndex)
        output[attributeIndex].add(individualIndex)
    return output

def gabs(individualsSet,sparseMatrix,depth):
    n = len(individualsSet)
    output = [[0 for x in range(n)] for y in range(n)]
    while len(individualsSet) != 0:
        currentDepth = 1
        individual = individualsSet.pop()
        connectedNodes = list(sparseMatrix[individual])
        visitedAttributes = set()
        visitedAttributes2 = set()
        while len(connectedNodes) !=  0:
            newConnectedNodes = []
            visitedAttributes2 = visitedAttributes
            for i in connectedNodes:
                if i in individualsSet:
                    #print(currentDepth)
                    output[individual-1][i-1] += numpy.float32(1)/numpy.float32(currentDepth)
                elif i not in visitedAttributes2:
                    visitedAttributes.add(i)
                    newConnectedNodes.extend(list(sparseMatrix[i]))
            currentDepth +=1
            connectedNodes = newConnectedNodes
    return output

def checkIndConnection(connectedSet,individualSet):
    return set.intersection(connectedSet,individualSet)

#def deployTree(nodesSet):
#    
#    return ""
    
graph = rdflib.Graph()
graph.load("./data/outputvote.rdf", format="nt")


individualsDict = loadIndividuals(graph)
individualsSet = set(sorted(individualsDict.values()))
offset = len(individualsDict)
attributesDict = loadAttributes(graph,offset)
sparse = getSparseGraph(graph,individualsDict,attributesDict)
result = gabs(individualsSet,sparse,2)
print(result)
