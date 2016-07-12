# -*- coding: utf-8 -*-
"""
Created on Thu Jun 23 13:45:22 2016

@author: kevindalleau
"""

import rdflib
import time
import numpy

data = numpy.loadtxt("/Users/kevindalleau/Documents/workspace/GraphAggregator/aggvote4.csv",delimiter=",")

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

def getSymetric(matrix):
    n = len(matrix)
    for i in range(0,n):
        for j in range(0,i):
            matrix[i][j] = matrix[j][i]
    return matrix

def gabs(individualsSet,sparseMatrix,depth):
    n = len(individualsSet)
    output = [[0]*n for x in range(n)]
    while len(individualsSet) != 0:
        tree = [[],[],[]]
        individual = individualsSet.pop()
        tree[0].append([individual])
        tree[1].extend([list(sparseMatrix[individual])])
        for currentDepth in range(2,depth+1):
            parentListSize = len(tree[1])
            for i in range(0,parentListSize):
                parentList = tree[1][i]
                for parent in parentList:
                    tree[2].extend([list(sparseMatrix[parent])])
            while len(tree[2]) != 0:
                nodeList = tree[2].pop(0)
                nodeGrandParent = tree[0]
                for node in nodeList:
                    if node in individualsSet and node not in nodeGrandParent:
                        output[individual-1][node-1] += float(1)/currentDepth
            tree.pop(0)
            tree.append([])

    return output
    
def customProduct(kMult, matrix, attributes,avoidMemory):
    n = len(kMult)
    output = [[0]*n for x in range(n)]
    for row in range(0,n):
        for col in range(0,n):
            value = 0
            if (row-1) not in attributes and (col-1) not in attributes:
                if col > row:
                    for k in attributes:
                        localValue = kMult[row][k-1]*matrix[k-1][col]
                        if localValue >=1:
                            value += localValue
                else:
                    value = output[col][row]
            else:
                if avoidMemory[row][col] == 0:
                    if col>row:
                        for k in attributes:
                            localValue = kMult[row][k-1]*matrix[k-1][col]
                            if localValue >=1:
                                value += localValue
            output[row][col] = value
            
    return output
                        
def aggregateMatrix(matrix, individuals, attributes, depth):
    n = len(individuals)
    output = [[0]*n for x in range(0,n)]
    kMult = matrix
    avoidMemory = matrix
    avoidMemory2 = matrix
    oldMatrix = list()
    for it in range(2,depth+1):
        oldMatrix = output
        avoidMemory = avoidMemory2
        avoidMemory2 = kMult
        if it <= 3:
            kMult = customProduct(kMult, matrix, attributes, matrix)
        else:
            kMult = customProduct(kMult, matrix, attributes, avoidMemory)
        #print kMult
        for i in range(0, n):
            for j in range(0,n):
                if j >= i:
                    valueAtDepth = kMult[individuals[i]-1][individuals[j]-1]
                    if valueAtDepth >= 1 and i != j:
                        oldValue = oldMatrix[i][j]
                        output[i][j] = float(oldValue) + float(valueAtDepth)/it
                else:
                    output[i][j] = output[j][i]
    return output

def sparseToDense(sparse,individuals,attributes):
    n = len(individuals)+len(attributes)
    
    output = [[0]*n for x in range(0,n)]
    
    for key in sparse.keys():
        values = sparse[key]
        for value in values:
            output[key-1][value-1] = 1
            output[value-1][key-1] = 1
    return output
        
graph = rdflib.Graph()
graph.load("./data/outputvote.rdf", format="nt")

individualsDict = loadIndividuals(graph)
individualsSet = set(sorted(individualsDict.values()))
offset = len(individualsDict)
attributesDict = loadAttributes(graph,offset)
sparse = getSparseGraph(graph,individualsDict,attributesDict)
dense = sparseToDense(sparse, individualsSet,set(attributesDict))
start_time = time.time()
resultAgg1 = aggregateMatrix(dense,list(individualsSet),list(sorted(attributesDict.values())),4)
print("--- %s seconds ---" % (time.time() - start_time))
start_time = time.time()
resultAgg2 = getSymetric(gabs(individualsSet,sparse,4))
print("--- %s seconds ---" % (time.time() - start_time))
print(resultAgg2==resultAgg1)
