import ast
import copy

import hy
from hy._compat import string_types
from hy.compiler import hy_compile
from hy.errors import HyTypeError
from hy.importer import ast_compile
from hy.models import HyObject, replace_hy_obj


class CodeContainer:
    def __init__(self):
        self.code_strings = []
        self.namespace = {'result': True}
        self._compiled_ast_and_expr = None, None

    def add_line(self, string):
        """
        Adds a line to the LISP code to execute

        :param string: The line to add
        :return: None
        """
        self.code_strings.append(string)
        code = ''
        if len(self.code_strings) == 1:
            code = '(setv result ' + self.code_strings[0] + ')'
        if len(self.code_strings) > 1:
            code = '(setv result (and ' + ' '.join(self.code_strings) + '))'
        self._compiled_ast_and_expr = self.__compile_code(code_string=code)

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

        if not self.code_strings:
            return True

        if vertices_substitution_dict:
            namespace = self.__substitute_names_in_namespace(self.namespace, vertices_substitution_dict)
        else:
            namespace = self.namespace
        try:
            self.__execute_code(self._compiled_ast_and_expr, namespace)
        except:
            pass
        return namespace['result']

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

    def __substitute_names_in_namespace(self, old_namespace, vertices_substitution_dict):
        new_namespace = {}
        for k, v in old_namespace.items():
            if k in new_namespace:
                continue
            if k in vertices_substitution_dict:
                new_k = vertices_substitution_dict[k]
                new_namespace[new_k] = old_namespace[k]
                new_namespace[new_k]['name'] = k
            else:
                new_namespace[k] = old_namespace[k]
        return new_namespace

    def __compile_code(self, code_string):
        hytree = hy.lex.tokenize(code_string)

        module_name = '__main__'

        foo = HyObject()
        foo.start_line = 0
        foo.end_line = 0
        foo.start_column = 0
        foo.end_column = 0
        replace_hy_obj(hytree, foo)

        if not isinstance(module_name, string_types):
            raise HyTypeError(foo, "Module name must be a string")

        _ast, expr = hy_compile(hytree, module_name, get_expr=True)

        # Spoof the positions in the generated ast...
        for node in ast.walk(_ast):
            node.lineno = 1
            node.col_offset = 1

        for node in ast.walk(expr):
            node.lineno = 1
            node.col_offset = 1

        return _ast, expr

    def __execute_code(self, compiled_code, namespace):
        _ast, expr = compiled_code

        # Two-step eval: eval() the body of the exec call
        eval(ast_compile(_ast, "<eval_body>", "exec"), namespace)

        # Then eval the expression context and return that
        return eval(ast_compile(expr, "<eval>", "eval"), namespace)


class DummyCodeContainer:
    def add_line(self, string):
        pass

    def add_graph_to_namespace(self, graph):
        pass

    def execute(self, vertices_substitution_dict={}):
        return True

    def substitute_namespace_into_graph(self, graph):
        return graph


class CodeContainerFactory:
    def create(self):
        return CodeContainer()


class DummyCodeContainerFactory:
    def create(self):
        return DummyCodeContainer()
