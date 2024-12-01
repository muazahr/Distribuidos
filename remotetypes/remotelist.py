import Ice
import RemoteTypes as rt

from remotetypes.iterable import RListIteratorI


class RListI(rt.RList):
    """Implementación de una lista remota que cumple con los requisitos especificados."""

    def __init__(self):
        """Inicializa una lista remota."""
        self._data = []
        self._original_hash = self._compute_hash()

    def _compute_hash(self):
        """Calcula un hash basado en el contenido actual de la lista."""
        return hash(tuple(self._data))

    def append(self, value, current=None):
        """Agrega un elemento al final de la lista."""
        self._data.append(value)
        self._original_hash = self._compute_hash()

    def pop(self, index=-1, current=None):
        """Elimina y devuelve un elemento de la lista por índice."""
        if index < 0 or index >= len(self._data):
            raise IndexError(f"Índice '{index}' fuera de rango.")
        value = self._data.pop(index)
        self._original_hash = self._compute_hash()
        return value

    def remove(self, value, current=None):
        """Elimina un elemento por valor, lanzando KeyError si no existe."""
        if value not in self._data:
            raise KeyError(f"El valor '{value}' no existe en la lista.")
        self._data.remove(value)
        self._original_hash = self._compute_hash()

    def getItem(self, index, current=None):
        """Devuelve el elemento en el índice especificado."""
        if index < 0 or index >= len(self._data):
            raise IndexError(f"Índice '{index}' fuera de rango.")
        return self._data[index]

    def length(self, current=None):
        """Devuelve la cantidad de elementos en la lista."""
        return len(self._data)

    def contains(self, value, current=None):
        """Devuelve True si el valor existe en la lista, de lo contrario False."""
        return value in self._data

    def hash(self, current=None):
        """Devuelve el hash actual de la lista."""
        return self._original_hash

    def iter(self, current=None):
        """Devuelve un iterador sobre los elementos de la lista."""
        return RListIteratorI(self._data)

    def getAllItems(self, current=None):
        return self._data.copy()





