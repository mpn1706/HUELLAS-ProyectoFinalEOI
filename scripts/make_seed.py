"""Genera el seed Jerez v3 (20 avisos con fotos reales: 7 lost + 13 found).

Cada foto se asigna a un aviso con atributos según rasgos visibles y una
ubicación exacta reciclada del pool validado (Nominatim, S28).
Trazable a REQ-03.8.
"""
import json
import random
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOST = ROOT / "data" / "seed" / "lost"
FOUND = ROOT / "data" / "seed" / "found"
IMG = ROOT / "data" / "seed" / "images"

# (fichero, tipo, animal, raza, color1, color2, marcas, tamaño, collar, collar_desc,
#  descripción, lat, lng, dirección, reported, last_seen, imagen, estado)
# Contacto por aviso: teléfonos variados en algunos, vacío en el resto.
CONTACTOS = {
    "lost_001.json": "610 204 518",
    "lost_002.json": "lucia.chapin.2741@gmail.com",
    "lost_003.json": "656 903 274",
    "lost_004.json": "marcos.soto.8390@gmail.com",
    "lost_005.json": "682 417 930",
    "lost_006.json": "carmen.gris.5517@gmail.com",
    "found_001.json": "617 552 086",
    "found_002.json": "pepe.avista.1974@gmail.com",
    "found_003.json": "ana.torres.6682@gmail.com",
    "found_004.json": "699 318 442",
    "found_005.json": "david.luna.3409@gmail.com",
    "found_006.json": "sara.vega.7128@gmail.com",
    "found_007.json": "640 771 295",
    "found_008.json": "juan.palacios.9045@gmail.com",
    "found_009.json": "674 025 638",
    "found_010.json": "elena.mora.1236@gmail.com",
    "found_011.json": "619 884 203",
    "lost_007.json": "julia.feria.4820@gmail.com",
    "found_012.json": "640 228 417",
    "found_013.json": "pablo.cruz.7719@gmail.com",
}
A = [
    ("lost_001.json", "lost", "cat", "europeo", "naranja", None, ["rayas", "cola anillada"], "small", False, None,
     "Gatito naranja atigrado perdido cerca de la plaza del Arenal. Tiene rayas marcadas y la cola anillada. Muy sociable.",
     36.68152, -6.13829, "Plaza del Arenal, San Miguel, Jerez de la Frontera", "2026-09-20T10:00:00+02:00", "2026-09-19T18:00:00+02:00", "gato 1.jpg", "active"),
    ("lost_002.json", "lost", "dog", "bodeguero", "blanco", "negro", ["mancha negra", "ojo"], "medium", True, "collar rosa con correa",
     "Perra blanca mediana con una mancha negra sobre el ojo. Lleva collar rosa con correa. Se escapó por la zona de Chapín. Muy dócil.",
     36.68934, -6.12052, "Estadio Municipal de Chapín, Avenida Chema Rodríguez, Jerez de la Frontera", "2026-09-18T10:00:00+02:00", "2026-09-17T20:00:00+02:00", "perrete 4.jpg", "active"),
    ("lost_003.json", "lost", "dog", "mestizo", "marrón", None, ["atigrado"], "medium", False, None,
     "Perro marrón atigrado de tamaño mediano perdido en Santiago. Delgado, sin collar, algo asustadizo.",
     36.68787, -6.14329, "Plaza Santiago, Santiago, Jerez de la Frontera", "2026-09-17T10:00:00+02:00", "2026-09-16T19:00:00+02:00", "perrete 3.jpg", "active"),
    ("lost_004.json", "lost", "cat", "mestizo", "blanco", None, ["ojos azules"], "small", False, None,
     "Gatito blanco de ojos azules perdido en San Joaquín. Pequeño, de pelo claro, muy cariñoso.",
     36.69125, -6.13173, "Calle Santo Domingo, Plaza del Caballo, Jerez de la Frontera", "2026-09-19T09:00:00+02:00", "2026-09-18T20:00:00+02:00", "gato 4.jpg", "active"),
    ("lost_005.json", "lost", "dog", "pitbull", "marrón", "blanco", ["pecho blanco"], "medium", False, None,
     "Pitbull marrón y blanco perdido en Vallesequillo. Mediano, fuerte, con el pecho blanco. No es agresivo.",
     36.67981, -6.1261, "Avenida de Medina Sidonia, Vallesequillo, Jerez de la Frontera", "2026-09-16T10:00:00+02:00", "2026-09-15T19:00:00+02:00", "perrete 12.jpg", "active"),
    ("lost_006.json", "lost", "cat", "europeo", "gris", "blanco", ["rayas"], "small", False, None,  # Vuelve a perdidos (S94): el siamés demo es lost_007
     "Gatito gris atigrado que se perdió en La Granja. Apareció al día siguiente en casa.",
     36.69331, -6.1034, "Avenida de Arcos de la Frontera, La Granja, Jerez de la Frontera", "2026-09-11T10:00:00+02:00", "2026-09-10T09:00:00+02:00", "gato 3.jpg", "active"),
    ("found_001.json", "found", "cat", "europeo", "naranja", "blanco", ["pecho blanco"], "small", False, None,
     "Gata naranja y blanca encontrada en la calle Larga. Joven, con el pecho blanco, maúlla mucho. Está a salvo.",
     36.68366, -6.13661, "Calle Larga, San Pedro, Jerez de la Frontera", "2026-09-20T12:00:00+02:00", None, "gato 5.jpg", "active"),
    ("found_002.json", "found", "dog", "pointer", "blanco", "negro", ["mancha negra", "moteado"], "large", False, None,
     "Perra blanca con manchas negras encontrada en La Plata. Grande, sin collar, moteada en el lomo. Tranquila.",
     36.6937, -6.14194, "La Plata, Jerez de la Frontera", "2026-09-18T15:00:00+02:00", None, "perrete 11.jpg", "active"),
    ("found_003.json", "found", "dog", "mestizo", "marrón", None, [], "medium", False, None,
     "Perro marrón claro encontrado en El Pelirón. Mediano, sin collar, bueno con la gente.",
     36.68714, -6.12447, "El Pelirón, Jerez de la Frontera", "2026-09-17T11:00:00+02:00", None, "perrete 8.jpg", "active"),
    ("found_004.json", "found", "cat", "europeo", "blanco", "gris", ["manchas grises"], "small", False, None,
     "Gato blanco con manchas grises recogido de noche en el parque González Hontoria. Pequeño y manso.",
     36.69524, -6.12599, "Parque González Hontoria, Jerez de la Frontera", "2026-09-19T15:00:00+02:00", None, "gato 7.jpg", "active"),
    ("found_005.json", "found", "dog", "bodeguero", "blanco", "marrón", ["manchas marrones"], "small", False, None,
     "Bodeguero blanco con manchas marrones encontrado de noche en Icovesa. Pequeño, movido, sin collar.",
     36.69404, -6.14574, "Icovesa, Jerez de la Frontera", "2026-09-16T15:00:00+02:00", None, "perrete 9.jpg", "active"),
    ("found_006.json", "found", "dog", "mestizo", "gris", None, ["pelo rizado"], "small", False, None,
     "Perrito joven gris de pelo rizado encontrado junto al aeropuerto. Macho joven. Lo llevan a la perrera.",
     36.7446, -6.0606, "Aeropuerto de Jerez, Jerez de la Frontera", "2026-09-19T11:00:00+02:00", None, "perrete 6.jpg", "active"),
    ("found_007.json", "found", "dog", "pastor", "marrón", "negro", ["lomo negro"], "large", True, "collar de cadena",
     "Pastor marrón y negro de tamaño grande visto en Puerta del Sur. Lleva collar de cadena. Imponente pero bueno.",
     36.66871, -6.13587, "Avenida Puerta del Sur, Santo Tomás, Jerez de la Frontera", "2026-09-18T10:00:00+02:00", None, "perrete 5.jpg", "active"),
    ("found_008.json", "found", "dog", "galgo", "negro", "blanco", ["pecho blanco", "patas blancas"], "medium", False, None,
     "Perro negro esbelto con pecho y patas blancas visto en Santiago. Mediano, sin collar, huidizo.",
     36.68787, -6.14329, "Plaza Santiago, Santiago, Jerez de la Frontera", "2026-09-17T10:00:00+02:00", None, "perrete 10.jpg", "active"),
    ("found_009.json", "found", "cat", "europeo", "blanco", "marrón", ["mancha negra", "máscara oscura"], "small", False, None,
     "Gata blanca con manchas marrones y máscara oscura encontrada en la calle Larga. Estaba tras una reja.",
     36.68366, -6.13661, "Calle Larga, San Pedro, Jerez de la Frontera", "2026-09-18T15:00:00+02:00", None, "gato 6.jpg", "active"),
    ("found_010.json", "found", "other", None, "verde", None, ["cabeza amarilla"], "small", False, None,
     "Loro verde visto en un árbol del parque González Hontoria. No se deja coger.",
     36.69524, -6.12599, "Parque González Hontoria, Jerez de la Frontera", "2026-09-19T14:00:00+02:00", None, "loro 1.jpg", "active"),
    ("found_011.json", "found", "cat", "europeo", "naranja", None, ["rayas", "cola anillada"], "small", False, None,
     "Gatito naranja atigrado encontrado junto a la plaza del Arenal. Tiene rayas marcadas y la cola anillada. Muy sociable, se deja coger. Está a salvo.",
     36.6821, -6.1376, "Calle San Miguel, junto a la plaza del Arenal, Jerez de la Frontera", "2026-09-20T18:00:00+02:00", None, "gato alert coincidencia con lost_001.jpg", "active"),
    ("lost_007.json", "lost", "cat", "siamés", "marrón", "crema", ["cara oscura", "cola oscura"], "small", False, None,
     "Gata siamesa perdida en San Miguel. Cuerpo color crema con cara, orejas y cola marrón oscuro. Ojos azules, muy dócil.",
     36.6802, -6.1398, "Calle Bizcocheros, San Miguel, Jerez de la Frontera", "2026-09-24T10:00:00+02:00", "2026-09-24T08:00:00+02:00", "lost_007.jpg", "active"),
    ("found_012.json", "found", "dog", "mestizo", "blanco", "crema", ["orejas erguidas"], "medium", False, None,
     "Perro blanco de orejas erguidas encontrado en Alameda Cristina. Mediano, sin collar, algo asustadizo pero bueno.",
     36.6858, -6.1363, "Alameda Cristina, San Miguel, Jerez de la Frontera", "2026-09-23T15:00:00+02:00", None, "found_012.jpg", "active"),
    ("found_013.json", "found", "dog", "mestizo", "marrón", "blanco", ["hocico blanco"], "medium", True, "collar oscuro",
     "Perro marrón de hocico blanco visto en la plaza del Mamelón. Mediano, con collar oscuro. Tranquilo.",
     36.6829, -6.1408, "Plaza del Mamelón, San Pedro, Jerez de la Frontera", "2026-09-19T11:00:00+02:00", None, "found_013.jpg", "active"),
]


def main():
    # Fechas aleatorias reproducibles entre el 25/08 y el 25/09 (S86). La pareja
    # E2E (lost_001/found_011) conserva sus fechas para no romper la demo.
    random.seed(20260925)
    d0, d1 = date(2026, 8, 25), date(2026, 9, 25)
    fijas = {"lost_001", "found_011", "lost_007", "found_012", "found_013"}
    for d in (LOST, FOUND, IMG):
        d.mkdir(parents=True, exist_ok=True)
    for (fn, tipo, animal, breed, c1, c2, marks, size, collar, collar_d, desc,
         lat, lng, addr, rep, seen, img, status) in A:
        folder = LOST if tipo == "lost" else FOUND
        aid = fn.replace(".json", "")
        if aid not in fijas:
            rep_d = d0 + timedelta(days=random.randint(0, (d1 - d0).days))
            rep = f"{rep_d.isoformat()}T12:00:00+02:00"
            seen = (f"{max(d0, rep_d - timedelta(days=1)).isoformat()}T18:00:00+02:00"
                    if tipo == "lost" else None)
        doc = {"id": aid, "type": tipo, "animal": animal,
               "breed_guess": breed, "color_primary": c1, "color_secondary": c2,
               "markings": marks, "size": size, "has_collar": collar,
               "collar_description": collar_d, "description_text": desc,
               "location": {"lat": lat, "lng": lng, "address_text": addr},
               "date_reported": rep, "date_last_seen": seen,
                "image_url": f"data/seed/images/{img}", "image_embedding": None,
                "contact_info": CONTACTOS.get(fn, ""), "status": status}
        (folder / fn).write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"seed v3: {len(A)} avisos")


if __name__ == "__main__":
    main()
