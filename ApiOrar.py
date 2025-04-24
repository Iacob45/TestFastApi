from enum import Enum
import uvicorn
from fastapi import FastAPI, HTTPException, Path, Query
from pydantic import BaseModel, Field

app = FastAPI(
    title="Api Parser",
    description="Api care face legatura intre baza de date SQL si front end, ofera acces la datele aplicatiei si diverse informatii",
    version="0.1"
)

def next_id_funct():
    """Ia lista sortata cu toate id-urile activitatilor
    si gaseste cel mai mic id nefolosit inca, pentru a putea fi alocat"""
    prec = -1
    sortat = sorted(activitati)
    for x in sortat:
        if x > prec+1:
            return prec+1
        prec = x
    return x+1

class Zile(Enum):
    """Zilele saptamanii"""
    LUNI = "luni"
    MARTI = "marti"
    MIERCURI = "miercuri"
    JOI = "joi"
    VINERI = "vineri"
    SAMBATA = "sambata"
    DUMINICA = "duminica"

class Categorie(Enum):
    """Categoria activitatii"""
    CURS = "curs"
    SEMINAR = "seminar"
    LABORATOR ="laborator"

class Activitate(BaseModel):
    """Structura unei activitati"""
    id: int = Field(description="Id-ul activitatii, generat automat in mod implicit cu functia next_id_funct", default_factory=next_id_funct, ge=0)
    nume: str = Field(description="Numele activitatii")
    durata: int = Field(description="Durata activitatii", gt=0)
    profesor: str = Field(description="Profesorul care se ocupa de activitate")
    sala: str = Field(description="Sala in care se desfasoara activitatea")
    zi: Zile = Field(description="Ziua saptamanii in care se desfasoara activitatea")
    ora: int = Field(description="Ora la care incepe activitatea", ge=1, le=24)
    categorie: Categorie = Field(description="Categoria activitatii (curs,seminar sau laborator)")

def verifica_exista(
    id: int | None = Query(default=None, ge=0),
    nume: str | None = None,
    durata: int | None = Query(default=None, gt=0),
    profesor: str | None = None,
    sala: str | None = None,
    zi: Zile | None = None,
    ora: int | None = Query(default=None, ge=1, le=24),
    categorie: Categorie | None = None,
):
    """Daca este oferit un ID, cauta activitatea dupa ID.
    Daca nu, o cauta dupa parametri"""
    if id is not None and id in activitati:
        return id
    else:
        exista = -1
        for id_curent, existing in activitati.items():
            if (
                    existing.nume == nume and
                    existing.durata == durata and
                    existing.profesor == profesor and
                    existing.sala == sala and
                    existing.zi == zi and
                    existing.ora == ora and
                    existing.categorie == categorie
            ):
                exista = id_curent
        return exista

def adauga_activitate(
    id: int | None = Query(default=None, ge=0),
    nume: str | None = None,
    durata: int | None = Query(default=None, gt=0),
    profesor: str | None = None,
    sala: str | None = None,
    zi: Zile | None = None,
    ora: int | None = Query(default=None, ge=1, le=24),
    categorie: Categorie | None = None,
):
    """Verifica daca deja exista o activitate cu aceeasi parametri,
     daca nu exista o creeaza ori cu id-ul dat, ori cu urmatorul id care nu a fost folosit"""
    exista = verifica_exista(id=id, nume=nume, durata=durata, profesor=profesor, sala=sala, zi=zi, ora=ora, categorie=categorie)
    if exista != -1:
        return -1
    if any(info is None for info in (nume, durata, profesor, sala, zi, ora, categorie)):
        return -2
    if id is None:
        id = next_id_funct()

    activitati[id] = Activitate(id=id, nume=nume, durata=durata, profesor=profesor, sala=sala, zi=zi, ora=ora, categorie=categorie)
    return id

def update_activitate(
    id_vechi: int = Field(ge=0),
    id: int | None = Query(default=None, ge=0),
    nume: str | None = None,
    durata: int | None = Query(default=None, gt=0),
    profesor: str | None = None,
    sala: str | None = None,
    zi: Zile | None = None,
    ora: int | None = Query(default=None, ge=1, le=24),
    categorie: Categorie | None = None,
):
    """Update activitate dupa ID"""
    #Verificare mai intai daca id-ul nou nu exista deja
    if id is not None and id in activitati:
        return -1

    #Verificare daca exista o activitate cu restul din noii parametrii
    exista = verifica_exista(id=id, nume=nume, durata=durata, profesor=profesor, sala=sala, zi=zi, ora=ora, categorie=categorie)
    if exista != -1:
        return -2

    activitate = activitati[id_vechi]
    if id is not None:
        #daca este oferit un update pentru vechiul id, vechia intrare este stearsa si mutata pe noul id
        activitate = activitati.pop(id_vechi)
        activitati[id] = activitate
        activitate.id = id
    if nume is not None:
        activitate.nume = nume
    if durata is not None:
        activitate.durata = durata
    if profesor is not None:
        activitate.profesor = profesor
    if sala is not None:
        activitate.sala = sala
    if zi is not None:
        activitate.zi = zi
    if ora is not None:
        activitate.ora = ora
    if categorie is not None:
        activitate.categorie = categorie

    return id


activitati = {
    0: Activitate(id=0, nume="Matematica", durata=2, profesor="Catalin", sala="A101", zi=Zile.MARTI, ora=14, categorie=Categorie.CURS),
    1: Activitate(id=1, nume="Limba romana", durata=2, profesor="Mihai", sala="A102", zi=Zile.MIERCURI, ora=12, categorie=Categorie.SEMINAR),
    2: Activitate(id=2, nume="Limba engleza", durata=2, profesor="Ion", sala="A103", zi=Zile.LUNI, ora=8, categorie=Categorie.CURS),
    3: Activitate(id=3, nume="Sport", durata=2, profesor="Catalin", sala="B003", zi=Zile.JOI, ora=10, categorie=Categorie.LABORATOR),
}

Selectie = dict[str,str|int|Categorie|Zile|None]

#GET------------------------------------------------------------------------
@app.get("/")
@app.get("/activitati")
def index() -> dict[str,dict[int, Activitate]]:
    try:

        return {"activitati":activitati}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Eroare in cerere de tip get: {e}")


@app.get("/activitati/{activitate_id}")
def query_activitate_by_id(activitate_id: int = Path(ge=0)) -> Activitate:
    try:

        if activitate_id not in activitati:
            raise HTTPException(status_code=404, detail=f"Activitatea cu {activitate_id=} nu exista.")
        return activitati[activitate_id]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Eroare in cerere de tip get: {e}")


@app.get("/alegeactivitate")
def cautare_activitate_cu_parametru(
        id: int | None = Query(default=None, ge=0),
        nume: str | None = None,
        durata: int | None = Query(default=None,gt=0),
        profesor: str | None = None,
        sala: str | None = None,
        zi: Zile | None = None,
        ora: int | None = Query(default=None, ge=1, le=24),
        categorie: Categorie | None = None
) -> dict[str, list[Selectie] | Selectie]:
    try:

        def verifica_activitate(activitate: Activitate) -> bool:
            return all(
                (
                    id is None or activitate.id == id,
                    nume is None or activitate.nume == nume,
                    durata is None or activitate.durata == durata,
                    profesor is None or activitate.profesor == profesor,
                    sala is None or activitate.sala == sala,
                    zi is None or activitate.zi == zi,
                    ora is None or activitate.ora == ora,
                    categorie is None or activitate.categorie is categorie
                )
            )
        selectie = [x for x in activitati.values() if verifica_activitate(x)]
        return {
            "cautare": {"nume": nume, "durata": durata, "profesor": profesor, "sala": sala, "zi": zi, "ora": ora, "categorie": categorie},
            "selectie": selectie
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Eroare in cerere de tip get: {e}")

#POST------------------------------------------------------------------------
@app.post("/activitati")
def add_activitate(activitate: Activitate) -> dict[str, Activitate]:
    try:

        adaugare = adauga_activitate(id=activitate.id, nume=activitate.nume, durata=activitate.durata, profesor=activitate.profesor, sala=activitate.sala, zi=activitate.zi, ora=activitate.ora, categorie=activitate.categorie)
        if adaugare == -1:
            raise HTTPException(status_code=400, detail=f"Activitatea deja exista.")
        if adaugare == -2:
            raise HTTPException(status_code=400, detail=f"Nu toti parametrii necesari pentru crearea unei activitati au fost specificati.")
        else:
            return {"added":activitate}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Eroare in cerere de tip post: {e}")


#PUT------------------------------------------------------------------------
@app.put("/activitati")
def updateoradd(
        id_vechi: int | None = Query(default=None, ge=0),
        nume_vechi: str | None = None,
        durata_vechi: int | None = Query(default=None, gt=0),
        profesor_vechi: str | None = None,
        sala_vechi: str | None = None,
        zi_vechi: Zile | None = None,
        ora_vechi: int | None = Query(default=None, ge=1, le=24),
        categorie_vechi: Categorie | None = None,
        id: int | None = Query(default=None, ge=0),
        nume: str | None = None,
        durata: int | None = Query(default=None, gt=0),
        profesor: str | None = None,
        sala: str | None = None,
        zi: Zile | None = None,
        ora: int | None = Query(default=None, ge=1, le=24),
        categorie: Categorie | None = None
) -> dict[str, Activitate]:
    try:

        #Cazul in care cineva a uitat sa puna datele care trebuie inlocuite
        if all(info is None for info in (id, nume, durata, profesor, sala, zi, ora, categorie)):
            raise HTTPException(status_code=400, detail=f"Nu a fost scris niciun parametru pentru actualizare sau adaugare.")

        #Cazul in care cineva nu a pus datele activitatii vechi => vrea sa adauge o activitate noua
        if all(info is None for info in (id_vechi, nume_vechi, durata_vechi, profesor_vechi, sala_vechi, zi_vechi, ora_vechi, categorie_vechi)):
            adaugare = adauga_activitate(id=id, nume=nume, durata=durata, profesor=profesor, sala=sala, zi=zi, ora=ora, categorie=categorie)
            if adaugare == -1:
                raise HTTPException(status_code=400, detail=f"Exista deja o activitate cu noii parametrii.")
            if adaugare == -2:
                raise HTTPException(status_code=400, detail=f"Nu toti noii parametrii au fost adaugati pentu creerea unei noi activitati, si nici nu a fost gasita o activitate cu vechii parametrii")
            else:
                return {"added": activitati[adaugare]}

        #Cazul in care exista datele activitatii vechi, verificam daca activitatea chiar exista
        exista = verifica_exista(id=id_vechi, nume=nume_vechi, durata=durata_vechi, profesor=profesor_vechi, sala=sala_vechi, zi=zi_vechi, ora=ora_vechi, categorie=categorie_vechi)
        if exista == -1:
            raise HTTPException(status_code=400, detail=f"Activitatea nu a fost gasita dupa acesti parametrii")
        else:
            actualizat = update_activitate(id_vechi=exista, id=id, nume=nume, durata=durata, profesor=profesor, sala=sala, zi=zi, ora=ora, categorie=categorie)
            if actualizat == -1:
                raise HTTPException(status_code=400, detail=f"Exista deja o activitate cu noul ID")
            if actualizat == -2:
                raise HTTPException(status_code=400, detail=f"Exista deja o activitate cu noii parametrii")
            else:
                return {"updated": activitati[actualizat]}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Eroare in cerere de tip put: {e}")



#PATCH------------------------------------------------------------------------
@app.patch("/activitati")
def update(
        id_vechi: int | None = Query(default=None, ge=0),
        nume_vechi: str | None = None,
        durata_vechi: int | None = Query(default=None, gt=0),
        profesor_vechi: str | None = None,
        sala_vechi: str | None = None,
        zi_vechi: Zile | None = None,
        ora_vechi: int | None = Query(default=None, ge=1, le=24),
        categorie_vechi: Categorie | None = None,
        id: int | None = Query(default=None, ge=0),
        nume: str | None = None,
        durata: int | None = Query(default=None, gt=0),
        profesor: str | None = None,
        sala: str | None = None,
        zi: Zile | None = None,
        ora: int | None = Query(default=None, ge=1, le=24),
        categorie: Categorie | None = None
) -> dict[str, Activitate]:
    try:

        # Cazul in care cineva a uitat sa puna datele care trebuie inlocuite
        if all(info is None for info in (id, nume, durata, profesor, sala, zi, ora, categorie)):
            raise HTTPException(status_code=400, detail=f"Nu a fost scris niciun parametru pentru actualizare sau adaugare.")

        # Cazul in care exista datele activitatii vechi, verificam daca activitatea chiar exista
        exista = verifica_exista(id=id_vechi, nume=nume_vechi, durata=durata_vechi, profesor=profesor_vechi, sala=sala_vechi, zi=zi_vechi, ora=ora_vechi, categorie=categorie_vechi)
        if exista == -1:
            raise HTTPException(status_code=400, detail=f"Activitatea nu a fost gasita dupa acesti parametrii")
        else:
            actualizat = update_activitate(id_vechi=exista, id=id, nume=nume, durata=durata, profesor=profesor, sala=sala, zi=zi, ora=ora, categorie=categorie)
            if actualizat == -1:
                raise HTTPException(status_code=400, detail=f"Exista deja o activitate cu noul ID")
            if actualizat == -2:
                raise HTTPException(status_code=400, detail=f"Exista deja o activitate cu noii parametrii")
            else:
                return {"updated": activitati[actualizat]}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Eroare in cerere de tip patch: {e}")



#DELETE------------------------------------------------------------------------
@app.delete("/activitati")
def delete_activitate(
        id: int | None = Query(default=None, ge=0),
        nume: str | None = None,
        durata: int | None = Query(default=None, gt=0),
        profesor: str | None = None,
        sala: str | None = None,
        zi: Zile | None = None,
        ora: int | None = Query(default=None, ge=1, le=24),
        categorie: Categorie | None = None
) -> dict[str, Activitate]:
    try:

        exista = verifica_exista(id=id, nume=nume, durata=durata, profesor=profesor, sala=sala, zi=zi, ora=ora, categorie=categorie)


        if exista == -1 and id is None and any(info is None for info in (nume, durata, profesor, sala, zi, ora, categorie)):
            raise HTTPException(status_code=400, detail=f"Este necesar ori un ID al activitatii, ori toti parametrii acesteia.")
        elif exista == -1:
            raise HTTPException(status_code=400, detail=f"Activitatea specificata nu a fost gasita")
        else:
            activitate = activitati.pop(id)
            return {"deleted": activitate}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Eroare in cerere de tip delete: {e}")


print("Working")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5050)