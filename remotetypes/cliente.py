import sys
import Ice
import RemoteTypes as rt

from typing import List

class ClientApp(Ice.Application):
    """Aplicación del cliente."""

    def run(self, args: List[str]) -> int:
        # Configurar el proxy del servidor
        proxy = self.communicator().stringToProxy("factory:default -p 60000")
        factory = rt.FactoryPrx.checkedCast(proxy)

        if not factory:
            print("No se pudo conectar al servidor.")
            return 1

        # Probar RDict
        print("Obteniendo un RDict remoto...")
        rdictProxy = factory.get(rt.TypeName.RDict, "MiDiccionario")
        rDict = rt.RDictPrx.checkedCast(rdictProxy)
        rDict.setItem("clave1", "valor1")
        rDict.setItem("clave2", "valor2")
        print(f"Valor de clave1: {rDict.getItem('clave1')}")
        print(f"Longitud de RDict: {rDict.length()}")

        # Probar RList
        print("\nObteniendo un RList remoto...")
        rlictProxy = factory.get(rt.TypeName.RList, "MiLista")
        rList = rt.RListPrx.checkedCast(rlictProxy)        
        rList.append("elemento1")
        rList.append("elemento2")
        print(f"Primer elemento en RList: {rList.getItem(0)}")
        print(f"Longitud de RList: {rList.length()}")

        # Probar RSet
        print("\nObteniendo un RSet remoto...")
        rSetProxy = factory.get(rt.TypeName.RSet, "MiSet")
        rSet = rt.RSetPrx.checkedCast(rSetProxy)           
        rSet.add("valor1")
        rSet.add("valor2")
        print(f"Contiene 'valor1': {rSet.contains('valor1')}")
        print(f"Longitud de RSet: {rSet.length()}")

        return 0


if __name__ == "__main__":
    app = ClientApp()
    sys.exit(app.main(sys.argv))
