import sys
import Ice
import RemoteTypes as rt
from typing import List


class ClientApp(Ice.Application):
    """Aplicación del cliente para probar RemoteTypes."""

    def run(self, args: List[str]) -> int:
        proxy = self.communicator().stringToProxy("factory:default -p 60000")
        factory = rt.FactoryPrx.checkedCast(proxy)

        if not factory:
            print("No se pudo conectar al servidor.")
            return 1

        # Operaciones de ejemplo
        print("Probando operaciones remotas con RDict, RList y RSet...")

        rdict_proxy = factory.get(rt.TypeName.RDict, "MiDiccionario")
        rdict = rt.RDictPrx.checkedCast(rdict_proxy)
        rdict.setItem("clave1", "valor1")
        print(f"Clave1: {rdict.getItem('clave1')}")

        rlist_proxy = factory.get(rt.TypeName.RList, "MiLista")
        rlist = rt.RListPrx.checkedCast(rlist_proxy)
        rlist.append("elemento1")
        print(f"Primer elemento de RList: {rlist.getItem(0)}")

        rset_proxy = factory.get(rt.TypeName.RSet, "MiSet")
        rset = rt.RSetPrx.checkedCast(rset_proxy)
        rset.add("valor1")
        print(f"RSet contiene 'valor1': {rset.contains('valor1')}")

        return 0


if __name__ == "__main__":
    app = ClientApp()
    sys.exit(app.main(sys.argv))
