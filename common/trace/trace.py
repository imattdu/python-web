import copy
import random
import string
from typing import Optional, Dict


def random_id(length=16):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


HEADER_TRACE_ID = 'X-Trace-Id'
HEADER_SPAN_ID = 'X-Span-Id'
HEADER_PARENT_SPAN_ID = 'X-Parent-Span-Id'


class Trace:
    def __init__(self, headers: Optional[Dict[str, str]] = None):
        if headers is None:
            headers = {}
        self._trace_id = headers.get(HEADER_TRACE_ID, random_id(16))
        self._span_id = headers.get(HEADER_PARENT_SPAN_ID, random_id(16))
        self._parent_span_id = ''

    def __deepcopy__(self, memo=None):
        import copy
        t = Trace()
        t._trace_id = copy.deepcopy(self._trace_id, memo)
        t._span_id = copy.deepcopy(self._span_id, memo)
        t._parent_span_id = copy.deepcopy(self._parent_span_id, memo)
        return t

    @property
    def trace_id(self):
        return self._trace_id

    @property
    def span_id(self):
        return self._span_id

    @span_id.setter
    def span_id(self, value: str):
        self._span_id = value

    @property
    def parent_span_id(self):
        return self._parent_span_id

    @parent_span_id.setter
    def parent_span_id(self, value: str):
        self._parent_span_id = value

    def __str__(self):
        arr = [
            f"trace_id={self._trace_id}",
            f"span_id={self._span_id}",
            f"parent_span_id={self._parent_span_id}",
        ]
        return '||'.join(arr)


if __name__ == '__main__':
    h = {HEADER_TRACE_ID: 'abc', HEADER_PARENT_SPAN_ID: 'cc'}
    t1 = Trace(h)
    t2 = t1.__deepcopy__()
    t1.parent_span_id = 'a'
    print(t2.parent_span_id)
