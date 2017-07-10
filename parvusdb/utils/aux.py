import random
from igraph import Graph


def get_random_name():
    return "dummy" + str(random.randint(1, 10000))


def convert_graph_to_string(g):
    drt_string = ""
    for vertex in g.vs:
        attributes = vertex.attributes()
        attributes.pop('name')
        drt_string += str(attributes)
        drt_string += '('
        drt_string += vertex['name']
        drt_string += ')'
        drt_string += ', '
    for edge in g.es:
        attributes = edge.attributes()
        attributes.pop('name')
        drt_string += str(attributes)
        drt_string += '('
        drt_string += g.vs[edge.tuple[0]]['name']
        drt_string += ','
        drt_string += g.vs[edge.tuple[1]]['name']
        drt_string += ')'
        drt_string += ', '
    drt_string = drt_string[:-2]

    return drt_string


def is_edge(string):
    return string.find(',') != -1


def create_graph_from_string(graph_string, directed=True):
    import ast

    g = Graph(directed=directed)
    line = graph_string.replace(' ', '')
    line = line.replace('\n', '')
    predicates_strings = line.split("),")
    vertices_to_add = []
    edges_to_add = []
    for predicate in predicates_strings:
        predicate = predicate.replace(')', '')
        attributes_str, name_str = predicate.split("(")
        attributes_dict = ast.literal_eval(attributes_str)
        if not is_edge(name_str):
            attributes_dict['name'] = name_str
            vertices_to_add.append(attributes_dict)
        else:
            if 'name' not in attributes_dict:
                attributes_dict['name'] = get_random_name()
            source, target = name_str.split(',')
            edges_to_add.append((source, target, attributes_dict))
    for attributes_dict in vertices_to_add:
        g.add_vertex(**attributes_dict)
    for source, target, attributes_dict in edges_to_add:
        g.add_edge(source, target, **attributes_dict)
    return g
