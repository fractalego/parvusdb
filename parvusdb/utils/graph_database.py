from .aux import create_graph_from_string, convert_graph_to_string
from .node_matcher import StringNodeMatcher
from .graph_builder import GraphBuilder
from .match import MatchException
from .code_container import CodeContainerFactory


def convert_special_characters_to_spaces(line):
    line = line.replace('\t', ' ')
    line = line.replace('\n', ' ')
    return line


class GraphDatabase:
    def __init__(self, g, node_matcher=StringNodeMatcher(), code_container_factory=CodeContainerFactory()):
        """
        This class interprets the commands translates them into operations on a graph by calling GraphBuilder().
        It accepts a graph as an argument and performs operations onto it.

        :param g: The graph to perform operations onto
        :param node_matcher: The class that decides if two nodes match
        :param code_container_factory: the class that creates the object that executes the LISP code
        """
        self.g = g
        self.node_matcher = node_matcher
        self.action_list = ['MATCH ', 'CREATE ', 'DELETE ', 'RETURN', 'SET ', 'WHERE ']
        self.action_dict = {'MATCH': self.__match,
                            'CREATE': self.__create,
                            'DELETE': self.__delete,
                            'SET': self.__set,
                            'WHERE': self.__where,
                            }
        self.code_container_factory = code_container_factory

    def query(self, string, repeat_n_times=None):
        """
        This method performs the operations onto self.g

        :param string: The list of operations to perform. The sequences of commands should be separated by a semicolon
                       An example might be
                         CREATE {'tag': 'PERSON', 'text': 'joseph'}(v1), {'relation': 'LIVES_AT'}(v1,v2),
                                {'tag': 'PLACE', 'text': 'London'}(v2)
                         MATCH {}(_a), {'relation': 'LIVES_AT'}(_a,_b), {}(_b)
                           WHERE (= (get _a "text") "joseph")
                         RETURN _a,_b;
        :param repeat_n_times: The maximum number of times the graph is queried. It sets the maximum length of
                               the return list. If None then the value is set by the function
                               self.__determine_how_many_times_to_repeat_query(string)

        :return: If the RETURN command is called with a list of variables names, a list of JSON with
                 the corresponding properties is returned. If the RETURN command is used alone, a list with the entire
                 graph is returned. Otherwise it returns an empty list
        """
        if not repeat_n_times:
            repeat_n_times = self.__determine_how_many_times_to_repeat_query(string)
        lines = self.__get_command_lines(string)
        return_list = []
        for line in lines:
            lst = self.__query_n_times(line, repeat_n_times)
            if lst and lst[0]:
                return_list = lst
        return return_list

    def get_graph(self):
        return self.g

    # Private

    def __query_n_times(self, line, n):
        rows = []
        for i in range(n):
            try:
                builder = GraphBuilder(self.g, self.node_matcher, self.code_container_factory, match_index=i)
                results = self.__query_with_builder(line, builder)
                rows.append(results)
                if not results:
                    break
            except MatchException:
                break
        return rows

    def __query_with_builder(self, string, builder):
        """
        Uses the builder in the argument to modify the graph, according to the commands in the string

        :param string: The single query to the database
        :return: The result of the RETURN operation
        """
        action_graph_pairs = self.__get_action_graph_pairs_from_query(string)
        for action, graph_str in action_graph_pairs:
            if action == 'RETURN' or action == '':
                return self.__return(graph_str, builder)
            try:
                self.action_dict[action](graph_str, builder)
            except MatchException:
                break
        return {}

    def __get_action_graph_pairs_from_query(self, query):
        """
        Splits the query into command/argument pairs, for example [("MATCH","{}(_a))", ("RETURN","_a")]

        :param query: The string with the list of commands
        :return: the command/argument pairs
        """
        import re

        query = convert_special_characters_to_spaces(query)
        graph_list = re.split('|'.join(self.action_list), query)
        query_list_positions = [query.find(graph) for graph in graph_list]
        query_list_positions = query_list_positions
        query_list_positions = query_list_positions
        action_list = [query[query_list_positions[i] + len(graph_list[i]):query_list_positions[i + 1]].strip()
                       for i in range(len(graph_list) - 1)]
        graph_list = graph_list[1:]
        return zip(action_list, graph_list)

    def __match(self, graph_str, builder):
        graph = create_graph_from_string(graph_str)
        builder.match_graph(graph)

    def __create(self, graph_str, builder):
        graph = create_graph_from_string(graph_str)
        builder.add_graph(graph)

    def __delete(self, graph_str, builder):
        variables = [v for v in graph_str.strip().replace(' ', '').split(',') if v]
        builder.delete_list(variables)

    def __return(self, graph_str, builder):
        variables = [v for v in graph_str.strip().replace(' ', '').split(',') if v]
        if not variables:
            return {'GRAPH': convert_graph_to_string(builder.build())}
        return builder.build_variables(variables)

    def __set(self, graph_str, builder):
        builder.set(graph_str)
        return True

    def __where(self, graph_str, builder):
        builder.where(graph_str)
        return True

    def __get_command_lines(self, string):
        lines = []
        for line in string.split('\n'):
            if not line.strip() or line.strip()[0] == '#':
                continue
            lines.append(line)
        lines = '\n'.join(lines).split(';')
        return lines

    def __determine_how_many_times_to_repeat_query(self, query_string):
        repeat_n_times = len(self.g.vs)
        if query_string.find('CREATE') != -1:
            repeat_n_times = 1
        return repeat_n_times
