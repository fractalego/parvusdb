from .code_container import CodeContainer
from .match import Match


class GraphBuilder:
    def __init__(self, g):
        """
        This class performs the operations into the graph g.

        :param g: The graph to modify
        """
        self.g = g
        self.vertices_substitution_dict = {}
        self.edges_substitution_dict = {}
        self.matching_graph = None
        self.matching_code_container = CodeContainer()
        self.match = Match(self.matching_code_container)
        self.update = True

    def add_graph(self, rhs_graph):
        """
        Adds a graph to self.g

        :param rhs_graph: the graph to add
        :return: itself
        """
        rhs_graph = self.__substitute_names_in_graph(rhs_graph)
        self.g = self.__merge_graphs(self.g, rhs_graph)
        return self

    def set(self, code):
        """
        Executes the code and apply it to the self.g

        :param code: the LIST code to execute
        :return: True/False, depending on the result of the LISP code
        """
        if self.update:
            self.vertices_substitution_dict, self.edges_substitution_dict \
                = self.match.get_variables_substitution_dictionaries(self.g, self.matching_graph)
        try:
            self.matching_graph = self.__apply_code_to_graph(code, self.matching_graph)
        except:
            pass
        try:
            code = self.__substitute_names_in_code(code)
            self.g = self.__apply_code_to_graph(code, self.g)
        except:
            pass
        return True

    def match_graph(self, rhs_graph):
        """
        Sets the graph to match with self.g

        :param rhs_graph: The graph to match
        :return: None
        """
        self.matching_graph = rhs_graph

    def where(self, code_string):
        """
        It sets the LISP code to execute upon matching graphs

        :param code_string: The code to execute
        :return: None
        """
        self.matching_code_container.add_line(code_string)

    def delete_list(self, variables):
        """
        Deletes a list of vertices/edges from self.g

        :param variables: the names of the variables to delete
        :return:
        """
        variables = set(self.__substitute_names_in_list(variables))
        self.update = False
        self.g.delete_vertices(self.g.vs.select(name_in=variables))
        self.g.delete_edges(self.g.es.select(name_in=variables))

    def build(self):
        """
        Return the graph

        :return: self.g
        """
        return self.g

    def build_variables(self, variables):
        """
        :param variables: The list of vertices/edges to return
        :return: the JSON of the properties of the variables to return
        """
        variables = set(self.__substitute_names_in_list(variables))
        attributes = []
        for variable in variables:
            try:
                vertices = self.g.vs.select(name=variable)
                attributes.append(vertices[0].attributes())
                continue
            except:
                pass
            try:
                edges = self.g.es.select(name=variable)
                edge_attr = edges[0].attributes()
                edge_attr.pop('name')
                attributes.append(edge_attr)
            except:
                pass
        return attributes

    # Private

    def __apply_code_to_graph(self, code_string, graph):
        code_container = CodeContainer()
        code_container.add_line(code_string)
        code_container.add_graph_to_namespace(graph)
        code_container.execute()
        code_container.substitute_namespace_into_graph(graph)
        return graph

    def __substitute_names_in_code(self, code):
        for k, v in self.vertices_substitution_dict.items():
            code = code.replace(' ' + k + ' ', ' ' + v + ' ')
        for k, v in self.edges_substitution_dict.items():
            code = code.replace(' ' + k + ' ', ' ' + v + ' ')
        return code

    def __substitute_names_in_graph(self, g):
        if self.update:
            self.vertices_substitution_dict, self.edges_substitution_dict \
                = self.match.get_variables_substitution_dictionaries(self.g, self.matching_graph)
        for i, v in enumerate(g.vs):
            name = v['name']
            try:
                new_name = self.vertices_substitution_dict[name]
                g.vs[i]['name'] = new_name
            except:
                pass
        for i, e in enumerate(g.es):
            name = e['name']
            try:
                new_name = self.edges_substitution_dict[name]
                g.es[i]['name'] = new_name
            except:
                pass
        return g

    def __substitute_names_in_list(self, lst):
        if self.update:
            self.vertices_substitution_dict, self.edges_substitution_dict \
                = self.match.get_variables_substitution_dictionaries(self.g, self.matching_graph)
        for i, v in enumerate(lst):
            name = lst[i]
            try:
                new_name = self.vertices_substitution_dict[name]
                lst[i] = new_name
                continue
            except:
                pass
            try:
                new_name = self.edges_substitution_dict[name]
                lst[i] = new_name
            except:
                pass

        return lst

    def __merge_graphs(self, lhs, rhs):
        for v in rhs.vs:
            lhs.add_vertex(**v.attributes())
        for e in rhs.es:
            lhs.add_edge(rhs.vs[e.tuple[0]]['name'],
                         rhs.vs[e.tuple[1]]['name'],
                         **e.attributes())
        mapping = []
        name_to_index_dict = {}
        mapped_index = 0
        for v in lhs.vs:
            name = v['name']
            try:
                mapping.append(name_to_index_dict[name])
            except:
                name_to_index_dict[name] = mapped_index
                mapping.append(mapped_index)
                mapped_index += 1
        lhs.contract_vertices(mapping=mapping, combine_attrs='first')
        return lhs
