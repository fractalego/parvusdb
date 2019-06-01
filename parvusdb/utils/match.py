import functools


class MatchException(Exception):
    def __init__(self):
        pass


class Match:
    def __init__(self, matching_code_container, node_matcher, match_index=0):
        self.matching_code_container = matching_code_container
        self.node_matcher = node_matcher
        self._match_index = match_index

    def get_variables_substitution_dictionaries(self, lhs_graph, rhs_graph):
        """
        Looks for sub-isomorphisms of rhs into lhs

        :param lhs_graph: The graph to look sub-isomorphisms into (the bigger graph)
        :param rhs_graph: The smaller graph
        :return: The list of matching names
        """
        if not rhs_graph:
            return {}, {}, {}
        self.matching_code_container.add_graph_to_namespace(lhs_graph)
        self.matching_code_container.add_graph_to_namespace(rhs_graph)
        return self.__collect_variables_that_match_graph(lhs_graph, rhs_graph)

    def __collect_variables_that_match_graph(self, lhs_graph, rhs_graph):
        match_info = {}
        self._vertices_substitution_list = []
        self._edges_substitution_list = []
        self._is_match = False
        lhs_graph.subisomorphic_vf2(other=rhs_graph,
                                    node_compat_fn=self.__node_compare,
                                    edge_compat_fn=self.__edge_compare,
                                    callback=self.__callback)
        if not self._is_match:
            raise MatchException()

        match_info['__RESULT__'] = self._is_match

        max_return_length = len(self._vertices_substitution_list)

        return self._vertices_substitution_list[self._match_index%max_return_length], \
               self._edges_substitution_list[self._match_index%max_return_length], \
               match_info

    def __substitute_names_in_list(self, lst, substitution_dict):
        for i, v in enumerate(lst):
            name = lst[i]
            try:
                new_name = substitution_dict[name]
                lst[i] = new_name
                continue
            except:
                pass
        return lst

    @functools.lru_cache(10)
    def __node_compare(self, lhs_graph, rhs_graph,
                       lhs_graph_index, rhs_graph_index):
        lhs_attr = lhs_graph.vs[lhs_graph_index].attributes()
        rhs_attr = rhs_graph.vs[rhs_graph_index].attributes()
        lhs_name = lhs_attr.pop('name')
        rhs_name = rhs_attr.pop('name')

        if not self.matching_code_container.execute({lhs_name: rhs_name}):
            return False
        rhs_attr = {k: v for k, v in rhs_attr.items() if v}
        if self.node_matcher.left_contains_right(rhs_attr, lhs_attr):
            return True
        return False

    @functools.lru_cache(10)
    def __edge_compare(self, lhs_graph, rhs_graph,
                       lhs_graph_index, rhs_graph_index):
        lhs_attr = lhs_graph.es[lhs_graph_index].attributes()
        rhs_attr = rhs_graph.es[rhs_graph_index].attributes()
        lhs_name = lhs_attr.pop('name')
        rhs_name = rhs_attr.pop('name')

        if not self.matching_code_container.execute({lhs_name: rhs_name}):
            return False
        rhs_attr = {k: v for k, v in rhs_attr.items() if v}
        if self.node_matcher.left_contains_right(rhs_attr, lhs_attr):
            return True
        return False

    def __callback(self, lhs_graph, rhs_graph, map12, map21):
        vertices_substitution_dict = {}
        edges_substitution_dict = {}

        if all([item == -1 for item in map12]):
            return False

        for lhs, rhs in enumerate(map12):
            if rhs == -1:
                continue
            lhs_name = lhs_graph.vs[lhs]['name']
            rhs_name = rhs_graph.vs[rhs]['name']
            vertices_substitution_dict[rhs_name] = lhs_name
        for rhs_edge in rhs_graph.es:
            source_target_list = self.__substitute_names_in_list([rhs_graph.vs[rhs_edge.tuple[0]]['name'],
                                                                  rhs_graph.vs[rhs_edge.tuple[1]]['name']],
                                                                 vertices_substitution_dict)
            source_index = lhs_graph.vs.select(name=source_target_list[0])[0].index
            target_index = lhs_graph.vs.select(name=source_target_list[1])[0].index
            lhs_edges = lhs_graph.es.select(_source=source_index, _target=target_index)
            for lhs_edge in lhs_edges:
                lhs_name = lhs_edge['name']
                rhs_name = rhs_edge['name']
                edges_substitution_dict[rhs_name] = lhs_name

        self._is_match = True
        self._vertices_substitution_list.append(vertices_substitution_dict)
        self._edges_substitution_list.append(edges_substitution_dict)

        return True
