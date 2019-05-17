from parvusdb.utils.cache import forbidden_dict


class MatchException(Exception):
    def __init__(self):
        pass


class Match:
    def __init__(self, matching_code_container, node_matcher):
        self.matching_code_container = matching_code_container
        self.node_matcher = node_matcher

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
        is_match, mapping, _ = lhs_graph.subisomorphic_vf2(other=rhs_graph,
                                                           return_mapping_12=True,
                                                           node_compat_fn=self.__node_compare,
                                                           edge_compat_fn=self.__edge_compare)
        if not is_match:
            raise MatchException()
        vertices_substitution_dict = {}
        edges_substitution_dict = {}
        for lhs, rhs in enumerate(mapping):
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

        match_info['__RESULT__'] = is_match

        return vertices_substitution_dict, edges_substitution_dict, match_info

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

    def __node_compare(self, lhs_graph, rhs_graph,
                       lhs_graph_index, rhs_graph_index):
        lhs_attr = lhs_graph.vs[lhs_graph_index].attributes()
        rhs_attr = rhs_graph.vs[rhs_graph_index].attributes()
        lhs_name = lhs_attr.pop('name')
        rhs_name = rhs_attr.pop('name')

        if self.__nodes_are_in_cache(lhs_name, rhs_name):
            return False
        if not self.matching_code_container.execute({lhs_name: rhs_name}):
            return False
        rhs_attr = {k: v for k, v in rhs_attr.items() if v}
        if self.node_matcher.left_contains_right(rhs_attr, lhs_attr):
            return True
        return False

    def __edge_compare(self, lhs_graph, rhs_graph,
                       lhs_graph_index, rhs_graph_index):
        lhs_attr = lhs_graph.es[lhs_graph_index].attributes()
        rhs_attr = rhs_graph.es[rhs_graph_index].attributes()
        lhs_name = lhs_attr.pop('name')
        rhs_name = rhs_attr.pop('name')

        if self.__nodes_are_in_cache(lhs_name, rhs_name):
            return False
        if not self.matching_code_container.execute({lhs_name: rhs_name}):
            return False
        rhs_attr = {k: v for k, v in rhs_attr.items() if v}
        if self.node_matcher.left_contains_right(rhs_attr, lhs_attr):
            return True
        return False

    def __nodes_are_in_cache(self, lhs_name, rhs_name):
        if lhs_name in forbidden_dict and rhs_name in forbidden_dict[lhs_name]:
            forbidden_dict.clear()
            return True
        return False
