# ParvusDB a simple, in-memory graph database

## Requirements 
* python-igraph
* hy
* python 3.5

## Installation
pip3 install parvusdb


## What is ParvusDB

ParvusDB is a small python3 library for handling graph operations. It acts as an in-memory 
graph database. It is meant to be used for small graphs (a few hundred nodes)

## Graph format
Graphs are written as a collection of _edges_ and _vertices_. A vertex is written as
```
{}(a)
```

where `a` is the name of the vertex. This name is used for the operations on the vertex iself.
A vertex can have properties written inside the brackets
```
{'tag': 'PERSON', 'text': 'john'}(a)
```

The text inside the brackets is in the JSON format. 
Each of these properties is associated to the node and stored inside the graph

The edges are written as
```
{}(a,b)
```

where `a` is the _source_ node name and `b` is the _target_ node name. 
As for the vertex, properties can be added inside the brackets
```
{'relation': 'LIVES_AT'}(a,b)
```

A vertex can have a name too, though it must be given as a property
 ```
{'relation': 'LIVES_AT', 'name': 'r1'}(a,b)
```


A triplet can therefore be written in the form.
 ```
{'tag': 'PERSON', 'text': 'john'}(a), {'relation': 'LIVES_AT'}(a,b), {'tag': 'PLACE', 'text': 'London'}(b)
```
 
## Keywords of the graph database
There are 6 commands (they must be typed in upper case)
* CREATE
* DELETE
* MATCH
* RETURN
* SET
* WHERE

### The keyword CREATE
This command creates the graph on the right hand side
```
CREATE {'tag': 'PERSON', 'text': 'john'}(a), {'relation': 'LIVES_AT'}(a,b), {'tag': 'PLACE', 'text': 'London'}(b);
```

### The keyword MATCH
This command matches a graph with the topology and properties specified in the right hand side
```
MATCH {'tag': 'PERSON'}(a), {'relation': 'LIVES_AT', 'name': 'r1'}(a,b), {'tag': 'PLACE'}(b);
```

### The keyword DELETE
This keyword deletes the vertex or edge with the names on the right hand side
```
DELETE a, b, r1
```

### The keyword WHERE
This keyword let the user specify a LISP code as a condition for the match. 
For example, if we want the "text" parameter of the node `a` to be in a list of names
```
MATCH {'tag': 'PERSON'}(a), {'relation': 'LIVES_AT', 'name': 'r1'}(a,b), {'tag': 'PLACE'}(b)
  WHERE (in (get a "text") ["john" "joseph" "joachim"]);
```

### The keyword SET
This command let us modify the content of a graph.
For example, if we want to change the text of the node `a`   
```
MATCH {'tag': 'PERSON'}(a), {'relation': 'LIVES_AT', 'name': 'r1'}(a,b), {'tag': 'PLACE'}(b)
SET (assoc a "text" "not john anymore");
```

### The keyword RETURN
This command let returns the properties of a specific node or edge
```
MATCH {'tag': 'PERSON'}(a), {'relation': 'LIVES_AT', 'name': 'r1'}(a,b), {'tag': 'PLACE'}(b)
RETURN a, r1;
```

The return value would be a list of the form
```
[{'a': {'tag': 'PERSON', 'text': 'john'}, 'r1': {'relation': 'LIVES_AT'}}]
```

If no vertex or edge name is specified, the system return the whole graph (in the 'parvusdb format' ).

## Python3 code examples

Let's add a triplet to a graph
```python
from igraph import Graph
from parvusdb import GraphDatabase


if __name__ == '__main__':
    g = Graph(directed=True)
    db = GraphDatabase(g)

    creation_string = """
    CREATE {'tag': 'PERSON', 'text': 'john'}(a), {'relation': 'LIVES_AT'}(a,b), 
           {'tag': 'PLACE', 'text': 'London'}(b) 
    RETURN;
    """
    lst = db.query(creation_string)
    print(lst)
```

which brings the output
```bash
[{'GRAPH': "{'tag': 'PERSON', 'text': 'john'}(a), {'tag': 'PLACE', 'text': 'London'}(b), {'relation': 'LIVES_AT'}(a,b)"}]
```

Then we can try to match elements of the triplet
```python
from igraph import Graph, plot
from parvusdb import GraphDatabase


if __name__ == '__main__':
    g = Graph(directed=True)
    db = GraphDatabase(g)

    creation_string = """
    CREATE {'tag': 'PERSON', 'text': 'john'}(a), {'relation': 'LIVES_AT'}(a,b),
           {'tag': 'PLACE', 'text': 'London'}(b);
    """
    
    match_string = """
    MATCH {}(a), {'relation': 'LIVES_AT'}(a,b), {}(b) 
    RETURN a,b;
    """
    
    lst = db.query(creation_string)
    lst = db.query(match_string)
    print(lst)
```

with output
```bash
[{'a': {'name': 'a', 'tag': 'PERSON', 'text': 'john'}, 'b': {'name': 'b', 'tag': 'PLACE', 'text': 'London'}}]
```

We can limit the matching process by using WHERE

```python
from igraph import Graph, plot
from parvusdb import GraphDatabase


if __name__ == '__main__':
    g = Graph(directed=True)
    db = GraphDatabase(g)

    
    creation_string = """
    CREATE {'tag': 'PERSON', 'text': 'john'}(a), {'relation': 'LIVES_AT'}(a,b),
           {'tag': 'PLACE', 'text': 'London'}(b)
    CREATE {'tag': 'PERSON', 'text': 'joseph'}(v1), {'relation': 'LIVES_AT'}(v1,v2),
           {'tag': 'PLACE', 'text': 'London'}(v2)
    """
    
    match_string = """
    MATCH {}(_a), {'relation': 'LIVES_AT'}(_a,_b), {}(_b)
      WHERE (= (get _a "text") "joseph")
    RETURN _a,_b;
    """
    
    lst = db.query(creation_string)
    lst = db.query(match_string)
    print(lst)
```

with output
```python
[{'_b': {'text': 'London', 'tag': 'PLACE', 'name': 'v2'}, '_a': {'text': 'joseph', 'tag': 'PERSON', 'name': 'v1'}}]
```

## TODO
* Handling of errors in GraphDatabase.query_lines()
* Ability to add LISP code outside WHERE and SET statements
* Create a stand-alone command line for the database
* Ability to match multiple items

## Known issues
* The igraph library does not like multiple edges on the same nodes, 
  therefore the MATCH function would not work correctly in those cases