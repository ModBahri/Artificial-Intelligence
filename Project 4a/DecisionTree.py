from math import log
from scipy.stats.distributions import chi2
import sys

class Node:
  """
  A simple node class to build our tree with. It has the following:
  
  children (dictionary<str,Node>): A mapping from attribute value to a child node
  attr (str): The name of the attribute this node classifies by. 
  islead (boolean): whether this is a leaf. False.
  """
  
  def __init__(self,attr):
    self.children = {}
    self.attr = attr
    self.isleaf = False

class LeafNode(Node):
    """
    A basic extension of the Node class with just a value.
    
    value (str): Since this is a leaf node, a final value for the label.
    islead (boolean): whether this is a leaf. True.
    """
    def __init__(self,value):
        self.value = value
        self.isleaf = True
    
class Tree:
  """
  A generic tree implementation with which to implement decision tree learning.
  Stores the root Node and nothing more. A nice printing method is provided, and
  the function to classify values is left to fill in.
  """
  def __init__(self, root=None):
    self.root = root

  def prettyPrint(self):
    print str(self)
    
  def preorder(self,depth,node):
    if node is None:
      return '|---'*depth+str(None)+'\n'
    if node.isleaf:
      return '|---'*depth+str(node.value)+'\n'
    string = ''
    for val in node.children.keys():
      childStr = '|---'*depth
      childStr += '%s = %s'%(str(node.attr),str(val))
      string+=str(childStr)+"\n"+self.preorder(depth+1, node.children[val])
    return string    

  def count(self,node=None):
    if node is None:
      node = self.root
    if node.isleaf:
      return 1
    count = 1
    for child in node.children.values():
      if child is not None:
        count+= self.count(child)
    return count  

  def __str__(self):
    return self.preorder(0, self.root)
  
  def classify(self, classificationData):
    """
    Uses the classification tree with the passed in classificationData.`
    
    Args:
        classificationData (dictionary<string,string>): dictionary of attribute values
    Returns:
        str
        The classification made with this tree.
    """
    #YOUR CODE HERE
    if self.root.isleaf:
        return self.root.value
    curr = Tree(self.root.children[classificationData[self.root.attr]])
    return curr.classify(classificationData)

  
def getPertinentExamples(examples,attrName,attrValue):
    """
    Helper function to get a subset of a set of examples for a particular assignment 
    of a single attribute. That is, this gets the list of examples that have the value 
    attrValue for the attribute with the name attrName.
    
    Args:
        examples (list<dictionary<str,str>>): list of examples
        attrName (str): the name of the attribute to get counts for
        attrValue (str): a value of the attribute
    Returns:
        list<dictionary<str,str>>
        The new list of examples.
    """
    newExamples = []
    #YOUR CODE HERE
    for example in examples:
        if attrName in example.keys():
            if example[attrName] == attrValue:
                newExamples.append(example)
    return newExamples
  
def getClassCounts(examples,className):
    """
    Helper function to get a dictionary of counts of different class values
    in a set of examples. That is, this returns a dictionary where each key 
    in the list corresponds to a possible value of the class and the value
    at that key corresponds to how many times that value of the class 
    occurs.
    
    Args:
        examples (list<dictionary<str,str>>): list of examples
        className (str): the name of the class
    Returns:
        dictionary<string,int>
        This is a dictionary that for each value of the class has the count
        of that class value in the examples. That is, it maps the class value
        to its count.
    """
    classCounts = {}
    #YOUR CODE HERE
    for example in examples:
        if className in example.keys():
            if example[className] not in classCounts.keys():
                classCounts[example[className]] = 1
            else:
                classCounts[example[className]] += 1
    return classCounts

def getMostCommonClass(examples,className):
    """
    A freebie function useful later in makeSubtrees. Gets the most common class
    in the examples. See parameters in getClassCounts.
    """
    counts = getClassCounts(examples,className)
    return max(counts, key=counts.get) if len(examples)>0 else None

def getAttributeCounts(examples,attrName,attrValues,className):
    """
    Helper function to get a dictionary of counts of different class values
    corresponding to every possible assignment of the passed in attribute. 
	  That is, this returns a dictionary of dictionaries, where each key  
	  corresponds to a possible value of the attribute named attrName and holds
 	  the counts of different class values for the subset of the examples
 	  that have that assignment of that attribute.
    
    Args:
        examples (list<dictionary<str,str>>): list of examples
        attrName (str): the name of the attribute to get counts for
        attrValues (list<str>): list of possible values for the attribute
        className (str): the name of the class
    Returns:
        dictionary<str,dictionary<str,int>>
        This is a dictionary that for each value of the attribute has a
        dictionary from class values to class counts, as in getClassCounts
    """
    attributeCounts={}
    #YOUR CODE HERE
    for str in attrValues:
        dict = {}
        for example in examples:
            if example[attrName] == str:
                if example[className] not in dict:
                    dict[example[className]] = 1
                else:
                    dict[example[className]] += 1
        attributeCounts[str] = dict
    return attributeCounts
        

def setEntropy(classCounts):
    """
    Calculates the set entropy value for the given list of class counts.
    This is called H in the book. Note that our labels are not binary,
    so the equations in the book need to be modified accordingly. Note
    that H is written in terms of B, and B is written with the assumption 
    of a binary value. B can easily be modified for a non binary class
    by writing it as a summation over a list of ratios, which is what
    you need to implement.
    
    Args:
        classCounts (list<int>): list of counts of each class value
    Returns:
        float
        The set entropy score of this list of class value counts.
    """
    #YOUR CODE HERE
    entropy = 0
    total = sum(classCounts)
    for classCount in classCounts:
        prob = float(classCount) / total
        entropy += - prob * log(prob, 2)
    return entropy
   

def remainder(examples,attrName,attrValues,className):
    """
    Calculates the remainder value for given attribute and set of examples.
    See the book for the meaning of the remainder in the context of info 
    gain.
    
    Args:
        examples (list<dictionary<str,str>>): list of examples
        attrName (str): the name of the attribute to get remainder for
        attrValues (list<string>): list of possible values for attribute
        className (str): the name of the class
    Returns:
        float
        The remainder score of this value assignment of the attribute.
    """
    #YOUR CODE HERE
    classCounts = getClassCounts(examples, className)
    total = sum(classCounts.values())
    ret = 0
    for attrValue in attrValues:
        currExamples = getPertinentExamples(examples, attrName, attrValue)
        currClassCounts = getClassCounts(currExamples, className)
        ret += float(sum(currClassCounts.values())) / total * setEntropy(currClassCounts.values())
    return ret

def infoGain(examples,attrName,attrValues,className):
    """
    Calculates the info gain value for given attribute and set of examples.
    See the book for the equation - it's a combination of setEntropy and
    remainder (setEntropy replaces B as it is used in the book).
    
    Args:
        examples (list<dictionary<str,str>>): list of examples
        attrName (str): the name of the attribute to get remainder for
        attrValues (list<string>): list of possible values for attribute
        className (str): the name of the class
    Returns:
        float
        The gain score of this value assignment of the attribute.
    """
    #YOUR CODE HERE
    classCounts = getClassCounts(examples, className)
    return setEntropy(classCounts.values()) - remainder(examples, attrName, attrValues, className)

def giniIndex(classCounts):
    """
    Calculates the gini value for the given list of class counts.
    See equation in instructions.
    
    Args:
        classCounts (list<int>): list of counts of each class value
    Returns:
        float
        The gini score of this list of class value counts.
    """
    #YOUR CODE HERE
    ret = 1
    total = sum(classCounts)
    for classCount in classCounts:
        ret -= pow((float(classCount) / total), 2)
    return ret
  
def giniGain(examples,attrName,attrValues,className):
    """
    Return the inverse of the giniD function described in the instructions.
    The inverse is returned so as to have the highest value correspond 
    to the highest information gain as in entropyGain. If the sum is 0,
    return sys.maxint.
    
    Args:
        examples (list<dictionary<str,str>>): list of examples
        attrName (str): the name of the attribute to get counts for
        attrValues (list<string>): list of possible values for attribute
        className (str): the name of the class
    Returns:
        float
        The summed gini index score of this list of class value counts.
    """
    #YOUR CODE HERE
    ret = 0
    for attrValue in attrValues:
        currExamples = getPertinentExamples(examples, attrName, attrValue)
        classCounts = getClassCounts(currExamples, className)
        ret += float(len(currExamples)) / len(examples) * giniIndex(classCounts.values())
    if ret == 0:
        import sys
        return sys.maxint
    else:
        return 1.0 / ret
    
def makeTree(examples, attrValues,className,setScoreFunc,gainFunc):
    """
    Creates the classification tree for the given examples. Note that this is implemented - you
    just need to imeplement makeSubtrees.
    
    Args:
        examples (list<dictionary<str,str>>): list of examples
        attrValues (dictionary<string,list<string>>): list of possible values for attribute
        className (str): the name of the class
        classScoreFunc (func): the function to score classes (ie setEntropy or giniIndex)
        gainFunc (func): the function to score gain of attributes (ie infoGain or giniGain)
    Returns:
        Tree
        The classification tree for this set of examples
    """
    remainingAttributes=attrValues.keys()
    return Tree(makeSubtrees(remainingAttributes,examples,attrValues,className,getMostCommonClass(examples,className),setScoreFunc,gainFunc))
    
def makeSubtrees(remainingAttributes,examples,attributeValues,className,defaultLabel,setScoreFunc,gainFunc):
    """
    Creates a classification tree Node and all its children. This returns a Node, which is the root
    Node of the tree constructed from the passed in parameters. This should be implemented recursively,
    and handle base cases for zero examples or remainingAttributes as covered in the book.    

    Args:
        remainingAttributes (list<string>): the names of attributes still not used
        examples (list<dictionary<str,str>>): list of examples
        attrValues (dictionary<string,list<string>>): list of possible values for attribute
        className (str): the name of the class
        defaultLabel (string): the default label
        setScoreFunc (func): the function to score classes (ie setEntropy or giniIndex)
        gainFunc (func): the function to score gain of attributes (ie infoGain or giniGain)
    Returns:
        Node or LeafNode
        The classification tree node optimal for the remaining set of attributes.
    """
    #YOUR CODE HERE
    if not examples:
        return LeafNode(defaultLabel)
    firstClassVal = examples[0][className]
    if len(examples) < 2:
        return LeafNode(firstClassVal)
    isSame = True
    for example in examples:
        isSame &= example[className] == firstClassVal
        if not isSame:
            break
    if isSame:
        return LeafNode(firstClassVal)
    if not remainingAttributes:
        root = LeafNode(getMostCommonClass(examples, className))
        return root
    maxArg = remainingAttributes[0]
    for attr in remainingAttributes:
        if gainFunc(examples, attr, attributeValues[attr], className) > gainFunc(examples, maxArg, attributeValues[maxArg], className):
            maxArg = attr
    root = Node(maxArg)
    currAttributes = list(remainingAttributes)
    currAttributes.remove(maxArg)
    for attrValue in attributeValues[maxArg]:
        currExamples = getPertinentExamples(examples, maxArg, attrValue)
        root.children[attrValue] = makeSubtrees(currAttributes, currExamples, attributeValues, className, getMostCommonClass(examples, className), setScoreFunc, gainFunc)
    return root

def makePrunedTree(examples, attrValues,className,setScoreFunc,gainFunc,q):
    """
    Creates the classification tree for the given examples. Note that this is implemented - you
    just need to imeplement makeSubtrees.
    
    Args:
        examples (list<dictionary<str,str>>): list of examples
        attrValues (dictionary<string,list<string>>): list of possible values for attribute
        className (str): the name of the class
        classScoreFunc (func): the function to score classes (ie setEntropy or giniIndex)
        gainFunc (func): the function to score gain of attributes (ie infoGain or giniGain)
        q (float): the Chi-Squared pruning parameter
    Returns:
        Tree
        The classification tree for this set of examples
    """
    remainingAttributes=attrValues.keys()
    return Tree(makePrunedSubtrees(remainingAttributes,examples,attrValues,className,getMostCommonClass(examples,className),setScoreFunc,gainFunc,q))
    
def makePrunedSubtrees(remainingAttributes,examples,attributeValues,className,defaultLabel,setScoreFunc,gainFunc,q):
    """
    Creates a classification tree Node and all its children. This returns a Node, which is the root
    Node of the tree constructed from the passed in parameters. This should be implemented recursively,
    and handle base cases for zero examples or remainingAttributes as covered in the book.    

    Args:
        remainingAttributes (list<string>): the names of attributes still not used
        examples (list<dictionary<str,str>>): list of examples
        attrValues (dictionary<string,list<string>>): list of possible values for attribute
        className (str): the name of the class
        defaultLabel (string): the default label
        setScoreFunc (func): the function to score classes (ie classEntropy or gini)
        gainFunc (func): the function to score gain of attributes (ie entropyGain or giniGain)
        q (float): the Chi-Squared pruning parameter
    Returns:
        Node or LeafNode
        The classification tree node optimal for the remaining set of attributes.
    """
    #YOUR CODE HERE (Extra Credit)
    if len(examples) == 0:
        node = LeafNode(defaultLabel)
        return node

    classificationAllSame = True
    check = examples[0][className]
    for example in examples:
        if example[className] != check:
            classificationAllSame = False
    if classificationAllSame == True:
        node = LeafNode(check)
        return node

    if len(remainingAttributes) == 0:
        return LeafNode(getMostCommonClass(examples, className))

    maxA = None
    maxGain = -99999999999
    for attr in remainingAttributes:
        if gainFunc(examples, attr, attributeValues[attr], className) > maxGain:
            maxGain = gainFunc(examples, attr, attributeValues[attr], className)
            maxA = attr
    dict = getAttributeCounts(examples, maxA, attributeValues[maxA], className)
    anotherdict = {}
    for key in dict.keys():
        subsum = 0
        for item in dict[key].keys():
            subsum = subsum + dict[key][item]
        anotherdict[key] = subsum

    classCounts = getClassCounts(examples, className)
    dev = 0
    for key in dict.keys():
        chi = 0
        for item in dict[key].keys():
            pi = dict[key][item] * 1.0
            pih = (classCounts[item] / (len(examples) * 1.0)) * anotherdict[key]
            chi += (pi - pih) * (pi - pih) / pih
        dev = dev + chi

    v = len(attributeValues[maxA]) - 1

    if chi2.sf(dev, v) > q:
        return LeafNode(getMostCommonClass(examples, className))

    newNode = Node(maxA)
    newRemain = []
    for remAttr in remainingAttributes:
        if remAttr != maxA:
            newRemain.append(remAttr)

    mostCommon = getMostCommonClass(examples, className)
    dict = {}
    for value in attributeValues[maxA]:
        newExamples = getPertinentExamples(examples, maxA, value)
        subtreeNode = makePrunedSubtrees(newRemain, newExamples, attributeValues, className, mostCommon, setScoreFunc, gainFunc, q)
        dict[value] = subtreeNode
    newNode.children = dict

    return newNode
