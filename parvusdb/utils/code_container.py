import hy


class CodeContainer:
    def __init__(self):
        self.code_strings = []
        self.namespace = {'result': True}

    def add_line(self, string):
        """
        Adds a line to the LISP code to execute

        :param string: The line to add
        :return: None
        """
        self.code_strings.append(string)

    def add_graph_to_namespace(self, graph):
        """
        Adds the variables name to the namespace of the local LISP code

        :param graph: the graph to add to the namespace
        :return: None
        """
        for node in graph.vs:
            attributes = node.attributes()
            self.namespace[node['name']] = attributes
        for node in graph.es:
            attributes = node.attributes()
            self.namespace[node['name']] = attributes

    def execute(self, vertices_substitution_dict={}):
        """
        Executes the code

        :param vertices_substitution_dict: aliases of the variables in the code
        :return: True/False, depending on the result of the code (default is True)
        """
        code = '(setv result True)'
        if len(self.code_strings) == 1:
            code = '(setv result ' + self.code_strings[0] + ')'
        if len(self.code_strings) > 1:
            code = '(setv result (and ' + ' '.join(self.code_strings) + '))'
        code = self.__substitute_names_in_code(code, vertices_substitution_dict)
        x = hy.lex.tokenize(code)
        try:
            hy.importer.hy_eval(x, self.namespace, "__main__")
        except:
            pass
        return self.namespace['result']

    def substitute_namespace_into_graph(self, graph):
        """
        Creates a graph from the local namespace of the code (to be used after the execution of the code)

        :param graph: The graph to use as a recipient of the namespace
        :return: the updated graph
        """
        for key, value in self.namespace.items():
            try:
                nodes = graph.vs.select(name=key)
                for node in nodes:
                    for k, v in value.items():
                        node[k] = v
            except:
                pass
            try:
                nodes = graph.es.select(name=key)
                for node in nodes:
                    for k, v in value.items():
                        node[k] = v
            except:
                pass
        return graph

    def __substitute_names_in_code(self, code, vertices_substitution_dict):
        for k, v in vertices_substitution_dict.items():
            code = code.replace(' ' + k + ' ', ' ' + v + ' ')
        return code
