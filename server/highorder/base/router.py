import re

class Router(object):
    def __init__(self, strict=False):
        self.static_routes = {}  # Search structure for static routes
        self.dynamic_patterns = []
        self.dynamic_routes = {}
        #: If true, static routes are no longer checked first.
        self.strict_order = strict

    rule_syntax = re.compile('(?:{([a-zA-Z_][a-zA-Z_0-9]*)?})')

    def _itertokens(self, rule):
        offset, prefix = 0, ''
        for match in self.rule_syntax.finditer(rule):
            prefix += rule[offset:match.start()]
            g = match.groups()
            if prefix:
                yield prefix, None
            variable = g[0]
            yield None, variable
            offset, prefix = match.end(), ''
        if offset <= len(rule) or prefix:
            yield prefix + rule[offset:], None

    def add(self, rule, endpoint):
        """ Add a new rule or replace the endpoint for an existing rule. """
        pattern = ''  # Regular expression pattern with named groups
        builder = []  # Data structure for the URL builder
        is_static = True

        for key, variable in self._itertokens(rule):
            if variable:
                is_static = False
                mask = r'[^/]+'
                pattern += '(?P<%s>%s)' % (variable, mask)
                builder.append((variable, str))
            elif key:
                pattern += re.escape(key)
                builder.append((None, key))

        rule_args = dict(endpoint=endpoint, rule=rule,
                        builder=builder, pattern=pattern)
        if is_static and not self.strict_order:
            self.static_routes[rule] = rule_args
            return

        try:
            re_pattern = re.compile('^(%s)$' % pattern)
            re_match = re_pattern.match
        except re.error as _e: # pragma: no cover
            raise Exception("Could not add Route: %s (%s)" %
                                   (rule, _e))

        rule_args['match'] = re_match

        self.dynamic_patterns.append(re_pattern)
        self.dynamic_routes[re_pattern] = rule_args



    def match(self, path):
        """ Return a (endpoint, url_args) tuple. """
        rule_args = self.static_routes.get(path)
        url_args = {}
        if not rule_args:
            for re_pattern in self.dynamic_patterns:
                matched = re_pattern.match(path)
                if matched:
                    url_args = matched.groupdict()
                    rule_args = self.dynamic_routes[re_pattern]
                    break

        if not rule_args:
            raise Exception("Not found: " + repr(path))

        return rule_args['endpoint'], url_args


if __name__ == '__main__':
    r = Router()
    r.add("/daily", "daily")
    r.add("/daily/{daystr}", "daily_detail")
    r.add("/daily/{daystr}/sss", "daily_detail_sss")
    print(r.match('/daily'))
    print(r.match('/daily/2022-10-22'))
    print(r.match('/daily/2022-09-09/sss'))