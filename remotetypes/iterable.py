import Ice
import RemoteTypes as rt



class RDictIteratorI(rt.Iterable):
    """Iterador remoto para RDict."""

    def __init__(self, keys):
        """Inicializa el iterador con las claves del diccionario."""
        self._keys = list(keys)
        self._index = 0

    def next(self, current=None):
        """Devuelve la siguiente clave en el iterador."""
        if self._index >= len(self._keys):
            raise rt.StopIteration("No hay más elementos para iterar.")
        key = self._keys[self._index]
        self._index += 1
        return key
    
class RListIteratorI(rt.Iterable):
    """Iterador remoto para RList."""

    def __init__(self, data):
        """Inicializa el iterador con los elementos de la lista."""
        self._data = list(data)
        self._index = 0

    def next(self, current=None):
        """Devuelve el siguiente elemento en la iteración."""
        if self._index >= len(self._data):
            raise rt.StopIteration("No hay más elementos para iterar.")
        value = self._data[self._index]
        self._index += 1
        return value