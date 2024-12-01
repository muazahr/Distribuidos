import Ice
import RemoteTypes as rt
from remotetypes.remotedict import RDictI
from remotetypes.remotelist import RListI
from remotetypes.remoteset import RemoteSet
import json
import os
import atexit

class Factory(rt.Factory):
    def __init__(self, adapter):
        self.adapter = adapter
        # Inicializar las instancias remotas y los servants
        self._instances = {
            rt.TypeName.RDict: {},
            rt.TypeName.RList: {},
            rt.TypeName.RSet: {},
        }
        self._servants = {
            rt.TypeName.RDict: {},
            rt.TypeName.RList: {},
            rt.TypeName.RSet: {},
        }
        # Diccionario para almacenar los datos
        self._data_storage = {
            'RDict': {},
            'RList': {},
            'RSet': {},
        }
        # Cargar datos desde el archivo JSON
        self.load_data()
        # Registrar save_data para que se llame al salir del programa
        atexit.register(self.save_data)

    def load_data(self):
        """Carga los datos desde el archivo JSON y recrea las instancias remotas."""
        if os.path.exists('data.json'):
            with open('data.json', 'r') as f:
                self._data_storage = json.load(f)
            for type_name_str, instances in self._data_storage.items():
                type_name = getattr(rt.TypeName, type_name_str)  # Convertir cadena a TypeName
                for identifier, instance_data in instances.items():
                    if type_name == rt.TypeName.RDict:
                        instance = RDictI()
                        instance._data = instance_data  # Cargar datos directamente
                        identity = self.adapter.getCommunicator().stringToIdentity(f"RDict_{identifier}")
                        self.adapter.add(instance, identity)
                        proxy = rt.RDictPrx.uncheckedCast(self.adapter.createProxy(identity))
                        self._instances[type_name][identifier] = proxy
                        self._servants[type_name][identifier] = instance
                    elif type_name == rt.TypeName.RList:
                        instance = RListI()
                        instance._data = instance_data  # Cargar datos directamente
                        identity = self.adapter.getCommunicator().stringToIdentity(f"RList_{identifier}")
                        self.adapter.add(instance, identity)
                        proxy = rt.RListPrx.uncheckedCast(self.adapter.createProxy(identity))
                        self._instances[type_name][identifier] = proxy
                        self._servants[type_name][identifier] = instance
                    elif type_name == rt.TypeName.RSet:
                        instance = RemoteSet(identifier)
                        instance._storage_ = set(instance_data)
                        identity = self.adapter.getCommunicator().stringToIdentity(f"RSet_{identifier}")
                        self.adapter.add(instance, identity)
                        proxy = rt.RSetPrx.uncheckedCast(self.adapter.createProxy(identity))
                        self._instances[type_name][identifier] = proxy
                        self._servants[type_name][identifier] = instance
        else:
            # No hay datos para cargar
            pass

    def save_data(self):
        """Guarda los datos de las instancias remotas en un archivo JSON."""
        # Actualizar _data_storage con los datos actuales de los servants
        for type_name, servants in self._servants.items():
            type_name_str = type_name.name  # Convertir TypeName a cadena
            self._data_storage[type_name_str] = {}
            for identifier, servant in servants.items():
                try:
                    if type_name == rt.TypeName.RDict:
                        self._data_storage[type_name_str][identifier] = servant._data.copy()
                    elif type_name == rt.TypeName.RList:
                        self._data_storage[type_name_str][identifier] = servant._data.copy()
                    elif type_name == rt.TypeName.RSet:
                        self._data_storage[type_name_str][identifier] = list(servant._storage_)
                except Exception as e:
                    print(f"Error al obtener datos del servant: {e}")
        # Guardar los datos en el archivo JSON
        with open('data.json', 'w') as f:
            json.dump(self._data_storage, f)

    def get(self, type_name, identifier, current=None):
        """Devuelve un proxy del tipo solicitado."""
        # Si no se proporciona un identificador, usar uno por defecto
        identifier = identifier or "default"

        if type_name == rt.TypeName.RDict:
            if identifier not in self._instances[rt.TypeName.RDict]:
                instance = RDictI()
                identity = self.adapter.getCommunicator().stringToIdentity(f"RDict_{identifier}")
                self.adapter.add(instance, identity)
                proxy = rt.RDictPrx.uncheckedCast(self.adapter.createProxy(identity))
                self._instances[rt.TypeName.RDict][identifier] = proxy
                self._servants[rt.TypeName.RDict][identifier] = instance
            return self._instances[rt.TypeName.RDict][identifier]

        elif type_name == rt.TypeName.RList:
            if identifier not in self._instances[rt.TypeName.RList]:
                instance = RListI()
                identity = self.adapter.getCommunicator().stringToIdentity(f"RList_{identifier}")
                self.adapter.add(instance, identity)
                proxy = rt.RListPrx.uncheckedCast(self.adapter.createProxy(identity))
                self._instances[rt.TypeName.RList][identifier] = proxy
                self._servants[rt.TypeName.RList][identifier] = instance
            return self._instances[rt.TypeName.RList][identifier]

        elif type_name == rt.TypeName.RSet:
            if identifier not in self._instances[rt.TypeName.RSet]:
                instance = RemoteSet(identifier)
                identity = self.adapter.getCommunicator().stringToIdentity(f"RSet_{identifier}")
                self.adapter.add(instance, identity)
                proxy = rt.RSetPrx.uncheckedCast(self.adapter.createProxy(identity))
                self._instances[rt.TypeName.RSet][identifier] = proxy
                self._servants[rt.TypeName.RSet][identifier] = instance
            return self._instances[rt.TypeName.RSet][identifier]

        else:
            raise ValueError(f"Tipo '{type_name}' no soportado por la fábrica.")
