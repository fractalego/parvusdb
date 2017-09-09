class StringNodeMatcher(object):
    """
    Checks whether one dict is contained into another one.
    All the values are matched upon using exact match.
    """

    def _match(self, key, lhs, rhs):
        if lhs != rhs:
            return False
        return True

    def left_contains_right(self, lhs, rhs):
        for key in lhs.keys():
            try:
                lvalue = lhs[key]
                rvalue = rhs[key]
                if not self._match(key, lvalue, rvalue):
                    return False
            except:
                return False
        return True
