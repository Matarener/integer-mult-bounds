"""Single-use observations of two complete, independently computed passes.

Chris R / Clear1nsight with substantial OpenAI Codex assistance. Apache-2.0.
"""
from copy import deepcopy


def need(ok, why):
    if not ok:
        raise ValueError(why)


class Observation:
    def __init__(self, backend, digest, word):
        self.backend, self.digest = backend, digest
        self.word_key = digest(word)
        self.values = {}
        self.closed = self.failed = self.used = False

    def __getattr__(self, name):
        return getattr(self.backend, name)

    def _call(self, name, word, *args):
        need(not self.closed and not self.failed, 'observation closed')
        actual = self.digest(word) == self.word_key
        def input_key():
            normalized = (args[0], sorted(args[1])) if name == 'error_trace' else args
            return self.digest((word, normalized))
        before = input_key()
        if actual:
            need(name not in self.values, 'duplicate actual observation')
            if name == 'error_trace':
                need('ideal' in self.values, 'missing ideal observation')
                ideal, weights = self.values['ideal'][0]
                need(self.digest(args[0]) == self.digest(weights), 'changed observation weights')
                need(set(args[1]) == set(ideal['counts']), 'changed observation rounding')
        try:
            value = getattr(self.backend, name)(word, *args)
            need(before == input_key(), 'input changed during observation')
        except BaseException:
            if actual:
                self.failed = True
                self.values.clear()
            raise
        if actual:
            saved = deepcopy(value)
            self.values[name] = (saved, self.digest(saved))
        return value

    def ideal(self, word):
        return self._call('ideal', word)

    def error_trace(self, word, weights, rounded):
        return self._call('error_trace', word, weights, rounded)

    def finish(self):
        need(not self.closed and not self.failed, 'observation closed')
        need(set(self.values) == {'ideal', 'error_trace'}, 'missing complete observation')
        self.closed = True

    def abort(self):
        self.failed = self.closed = True
        self.values.clear()

    def take(self, word):
        need(self.closed and not self.failed and not self.used, 'observation unavailable')
        need(self.digest(word) == self.word_key, 'changed observation word')
        need(all(self.digest(value) == key for value, key in self.values.values()), 'observation output drift')
        self.used = True
        result = {name: value for name, (value, key) in self.values.items()}
        self.values.clear()
        return result
