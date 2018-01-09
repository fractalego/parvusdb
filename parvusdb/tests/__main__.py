from igraph import Graph
from parvusdb.utils import convert_graph_to_string, create_graph_from_string, GraphDatabase


class Tests:
    def __print_test_title(self, string):
        print(string)

    def test_graph_to_string(self):
        self.__print_test_title('The string-graph conversion works')
        expected_str = "{'tag': 'NN'}(v1), {'tag': None}(2), {'tag': 'VBZ'}(v4), {'type': 'AGENT76'}(v4,v1), {'type': 'ANOTHER_AGENT'}(v1,2)"
        g2 = create_graph_from_string(expected_str)
        if convert_graph_to_string(g2) == expected_str:
            return True
        return False

    def test_insertion_into_database(self):
        self.__print_test_title('A graph can be inserted into the database')
        g = Graph(directed=True)
        db = GraphDatabase(g)
        lst = db.query(
            "CREATE {'word': 'alberto', 'tag':'NNP'}(a), {'word': 'WRITES'}(a,b), {'word': 'documentation', 'tag':'NN'}(b) RETURN a")
        expected_dict = {'word': 'alberto', 'name': 'a', 'tag': 'NNP'}
        if lst[0]['a'] == expected_dict:
            return True
        return False

    def test_vertex_matching_in_database(self):
        self.__print_test_title('The vertices of a graph can matched')
        g = Graph(directed=True)
        db = GraphDatabase(g)
        lst = db.query(
            """
             CREATE {'word': 'alberto', 'tag':'NNP'}(1), {'word': 'WRITES'}(1,2), {'word': 'documentation', 'tag':'NN'}(2),
                    {'word': 'BE'}(2,3), {'word': 'good', 'tag':'NN'}(3)
             MATCH {'tag':'NNP'}(a), {'word': 'WRITES'}(a,b), {'word': 'documentation'}(b)
             RETURN a, b
             """)
        expected_dicts = [{'word': 'alberto', 'tag': 'NNP', 'name': '1'},
                          {'word': 'documentation', 'tag': 'NN', 'name': '2'}]
        if lst[0]['a'] == expected_dicts[0] and lst[0]['b'] == expected_dicts[1]:
            return True
        return False

    def test_edge_matching_in_database(self):
        self.__print_test_title('The edge of a graph can be matched')
        g = Graph(directed=True)
        db = GraphDatabase(g)
        lst = db.query(
            """
             CREATE {'word': 'alberto', 'tag':'NNP'}(1), {'word': 'WRITES'}(1,2), {'word': 'documentation', 'tag':'NN'}(2),
                    {'name': 'edge1', 'word': 'BE'}(2,3), {'word': 'good', 'tag':'NN'}(3)
             MATCH {'tag':'NN'}(a), {'name': '_edge'}(a,b), {'word': 'good'}(b)
             RETURN _edge
             """)
        expected_dict_1 = {'word': 'BE'}
        if lst[0]['_edge']['word'] == expected_dict_1['word']:
            return True
        return False

    def test_edge_deletion_in_database(self):
        self.__print_test_title('The edge of a graph can be deleted')
        g = Graph(directed=True)
        db = GraphDatabase(g)
        lst = db.query(
            """
             CREATE {'word': 'alberto', 'tag':'NNP'}(1), {'word': 'WRITES'}(1,2), {'word': 'documentation', 'tag':'NN'}(2),
                    {'name': 'edge1', 'word': 'BE'}(2,3), {'word': 'good', 'tag':'NN'}(3)
             MATCH {'tag':'NN'}(a), {'name': '_edge'}(a,b), {'word': 'good'}(b)
             DELETE _edge
             RETURN
             """)
        expected_graph_str = "{'word': 'alberto', 'tag': 'NNP'}(1), {'word': 'documentation', 'tag': 'NN'}(2), {'word': 'good', 'tag': 'NN'}(3), {'word': 'WRITES'}(1,2)"
        if lst[0]['GRAPH'] == expected_graph_str:
            return True
        return False

    def test_code_work_is_applied_to_a_matching_graph_vertex(self):
        self.__print_test_title('The code can create a tag in a matching graph vertex')
        g = Graph(directed=True)
        db = GraphDatabase(g)
        lst = db.query(
            """
             CREATE {'word': 'alberto', 'tag':'NN'}(1), {'word': 'WRITES'}(1,2), {'word': 'documentation', 'tag':'NN'}(2),
                    {'name': 'edge1', 'word': 'BE'}(2,3), {'word': 'good', 'tag':'NN'}(3)
             MATCH {'tag':'NN'}(a), {'name': '_edge'}(a,b), {'tag': 'NN'}(b)
             SET (assoc a "word" "documentation")
             DELETE _edge
             RETURN
             """)
        expected_graph_str = "{'word': 'alberto', 'tag': 'NN'}(1), {'word': 'documentation', 'tag': 'NN'}(2), {'word': 'good', 'tag': 'NN'}(3), {'word': 'WRITES'}(1,2)"
        if lst[0]['GRAPH'] == expected_graph_str:
            return True
        return False

    def test_code_work_is_applied_to_a_matching_graph_edge(self):
        self.__print_test_title('The code can create a tag in a matching graph edge')
        g = Graph(directed=True)
        db = GraphDatabase(g)
        lst = db.query(
            """
             CREATE {'word': 'alberto', 'tag':'NN'}(1), {'word': 'WRITES'}(1,2), {'word': 'documentation', 'tag':'NN'}(2),
                    {'name': 'edge1', 'word': 'BE'}(2,3), {'word': 'good', 'tag':'NN'}(3)
             MATCH {'tag':'NN'}(a), {'name': '_edge'}(a,b), {'tag': 'NN'}(b)
             SET (assoc _edge "word" "NEW_EDGE_NAME")
             RETURN _edge
             """)
        expected_new_edge_name = 'NEW_EDGE_NAME'
        if lst[0]['_edge']['word'] == expected_new_edge_name:
            return True
        return False

    def test_graph_creation_works_after_matching(self):
        self.__print_test_title('The code can create a new graph after matching')
        g = Graph(directed=True)
        db = GraphDatabase(g)
        lst = db.query(
            """
             CREATE {'word': 'alberto', 'tag':'NNP'}(1), {'word': 'WRITES'}(1,2), {'word': 'documentation', 'tag':'NN'}(2),
                    {'name': 'edge1', 'word': 'BE'}(2,3), {'word': 'good', 'tag':'NN'}(3)
             MATCH {'tag':'NN'}(a), {'name': '_edge'}(a,b), {'tag': 'NN'}(b)
             DELETE _edge
             CREATE {}(a), {'name': 'edge1', 'word': 'BE2'}(a,4), {'word': 'good2', 'tag':'NN'}(4)
             RETURN
             """)
        expected_graph_str = "{'tag': 'NNP', 'word': 'alberto'}(1), {'tag': 'NN', 'word': 'documentation'}(2), {'tag': 'NN', 'word': 'good'}(3), {'tag': 'NN', 'word': 'good2'}(4), {'word': 'WRITES'}(1,2), {'word': 'BE2'}(2,4)"
        if lst[0]['GRAPH'] == expected_graph_str:
            return True
        return False

    def test_code_works_for_created_graph(self):
        self.__print_test_title('The code can modify a graph that has just been created')
        g = Graph(directed=True)
        db = GraphDatabase(g)
        lst = db.query(
            """
             CREATE {'word': 'alberto', 'tag':'NNP'}(v1), {'word': 'WRITES'}(v1,v2), {'word': 'documentation', 'tag':'NN'}(v2),
                    {'name': 'edge1', 'word': 'BE'}(v2,v3), {'word': 'good', 'tag':'NN'}(v3)
             MATCH {'tag':'NN'}(a), {'name': '_edge'}(a,b), {'tag': 'NN'}(b)
             DELETE _edge
             CREATE {}(a), {'name': 'edge1', 'word': 'BE2'}(a,d), {'word': 'good2', 'tag':'NN'}(d)
             SET (assoc d "word" (+ (get a "word") (get b "word")))
             RETURN d
             """)
        expected_dict = {'tag': 'NN', 'word': 'documentationgood', 'name': 'd'}
        if lst[0]['d'] == expected_dict:
            return True
        return False

    def test_code_works_while_matching_graphs(self):
        self.__print_test_title('The code can decide if two graphs match')
        g = Graph(directed=True)
        db = GraphDatabase(g)
        lst = db.query(
            """
             CREATE {'word': 'alberto', 'tag':'NN'}(v1), {'word': 'WRITES'}(v1,v2), {'word': 'documentation', 'tag':'NN'}(v2),
                    {'name': 'edge1', 'word': 'BE'}(v2,v3), {'word': 'good', 'tag':'NN'}(v3);
             """)
        lst = db.query(
            """
             MATCH {'tag':'NN'}(a), {'name': '_edge'}(a,b), {'tag': 'NN'}(b)
             WHERE (= (get a "word") "documentation")
             RETURN b
             """)
        expected_dict = {'word': 'good', 'name': 'v3', 'tag': 'NN'}
        if lst[0]['b'] == expected_dict:
            return True
        return False

    def test_code_works_while_matching_graphs_with_keyword_IN(self):
        self.__print_test_title('The code can decide if two graphs match using keyword IN')
        g = Graph(directed=True)
        db = GraphDatabase(g)
        lst = db.query(
            """
             CREATE {'word': 'alberto', 'tag':'NN'}(v1), {'word': 'WRITES'}(v1,v2), {'word': 'documentation', 'tag':'NN'}(v2),
                    {'name': 'edge1', 'word': 'BE'}(v2,v3), {'word': 'good', 'tag':'NN'}(v3);
             """)
        lst = db.query(
            """
             MATCH {'tag':'NN'}(a), {'name': '_edge'}(a,b), {'tag': 'NN'}(b)
             WHERE (in (get a "word") ["documentation" "Doc"])
             RETURN b
             """)
        expected_dict = {'word': 'good', 'name': 'v3', 'tag': 'NN'}
        if lst[0]['b'] == expected_dict:
            return True
        return False

    def test_creation_after_deletion(self):
        self.__print_test_title('A new edge can be created after deleting one between the same vertices')
        g = Graph(directed=True)
        db = GraphDatabase(g)
        lst = db.query(
            """
            CREATE {'word': 'alberto', 'tag':'NN'}(v1), {'type': 'nsubj'}(v1,v2), {'word': 'documentation', 'tag':'NN'}(v2)
            MATCH {}(a), {'name': 'r', 'type':'nsubj'}(a,b), {}(b)
            DELETE r
            CREATE {}(a), {'name': 'r2', 'type': 'AGENT'}(a,b), {}(b)
            RETURN r2
            """)
        expected_dict = {'type': 'AGENT'}
        if lst[0]['r2']['type'] == expected_dict['type']:
            return True
        return False

    def test_multiple_match_on_vertex(self):
        self.__print_test_title('A match command is applied multiple times on a vertex')
        g = Graph(directed=True)
        db = GraphDatabase(g)
        db.query(
            """
            CREATE {'word': 'alberto', 'tag':'NN'}(v1), {'type': 'nsubj'}(v1,v2), {'word': 'write', 'tag':'VB'}(v2),
                   {'type': 'dobj'}(v2,v3), {'word': 'documentation', 'tag':'NN'}(v3)
            """)
        lst = db.query(
            """
            MATCH {}(a), {'name': 'r'}(a,b), {}(b)
            RETURN a
            """)
        expected_dict1 = {'word': 'alberto', 'tag': 'NN', 'name': 'v1'}
        expected_dict2 = {'word': 'write', 'tag': 'VB', 'name': 'v2'}
        if lst[0]['a'] == expected_dict1 and lst[1]['a'] == expected_dict2:
            return True
        return False

    def test_multiple_match_on_an_edge(self):
        self.__print_test_title('A match command is applied multiple times on an edge')
        g = Graph(directed=True)
        db = GraphDatabase(g)
        db.query(
            """
            CREATE {'word': 'alberto', 'tag':'NN'}(v1), {'type': 'nsubj'}(v1,v2), {'word': 'write', 'tag':'VB'}(v2),
                   {'type': 'dobj'}(v2,v3), {'word': 'documentation', 'tag':'NN'}(v3)
            """)
        lst = db.query(
            """
            MATCH {}(a), {'name': 'r'}(a,b), {}(b)
            RETURN r
            """)
        expected_dict1 = {'type': 'nsubj'}
        expected_dict2 = {'type': 'dobj'}
        if lst[0]['r']['type'] == expected_dict1['type'] and lst[1]['r']['type'] == expected_dict2['type']:
            return True
        return False


if __name__ == "__main__":
    tests = Tests()
    for test_name in dir(Tests):
        if test_name.find("__") != -1:
            continue
        test = getattr(Tests, test_name)
        result_is_true = test(tests)
        if result_is_true:
            print("True")
        else:
            print("False")
        print()
