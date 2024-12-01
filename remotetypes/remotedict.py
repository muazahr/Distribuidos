import Ice
import RemoteTypes as rt
from remotetypes.iterable import RDictIteratorI

class RDictI(rt.RDict):
    """Implementación de un diccionario remoto que cumple con los requisitos especificados."""

    def __init__(self):
        """Inicializa un diccionario remoto."""
        self._data = {}
        self._original_hash = self._compute_hash()

    def _compute_hash(self):
        """Calcula un hash basado en el contenido actual del diccionario."""
        return hash(frozenset(self._data.items()))

    def setItem(self, key, value, current=None):
        """Agrega o actualiza un elemento en el diccionario."""
        self._data[key] = value
        self._original_hash = self._compute_hash()

    def getItem(self, key, current=None):
        """Obtiene un valor por clave, lanzando KeyError si no existe."""
        if key not in self._data:
            raise KeyError(f"La clave '{key}' no existe en el diccionario.")
        return self._data[key]

    def remove(self, key, current=None):
        """Elimina un elemento por clave, lanzando KeyError si no existe."""
        if key not in self._data:
            raise KeyError(f"La clave '{key}' no existe en el diccionario.")
        del self._data[key]
        self._original_hash = self._compute_hash()

    def pop(self, key, current=None):
        """Elimina y devuelve un elemento por clave, lanzando KeyError si no existe."""
        if key not in self._data:
            raise KeyError(f"La clave '{key}' no existe en el diccionario.")
        value = self._data.pop(key)
        self._original_hash = self._compute_hash()
        return value

    def length(self, current=None):
        """Devuelve la cantidad de elementos en el diccionario."""
        return len(self._data)

    def contains(self, key, current=None):
        """Devuelve True si la clave existe en el diccionario, de lo contrario False."""
        return key in self._data

    def hash(self, current=None):
        """Devuelve el hash actual del diccionario."""
        return self._original_hash

    def iter(self, current=None):
        """Devuelve un iterador sobre las claves del diccionario."""
        return RDictIteratorI(self._data.keys())

    def getAllItems(self, current=None):
        return self._data.copy()