"""Genera seed Jerez (17 avisos: 5 lost + 12 found). Trazable a REQ-03.8.

Un par lost↔found casi idéntico garantiza ÉXITO-01 en demo.
Imágenes: placeholders sólidos por color (solo para que la app abra algo).
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOST = ROOT / "data" / "seed" / "lost"
FOUND = ROOT / "data" / "seed" / "found"
IMG = ROOT / "data" / "seed" / "images"

# Jerez: centro 36.6826,-6.1376
A = [
    # LOST (5)
    ("lost_001.json", "lost", "dog", "mestizo", "marrón", None, ["mancha blanca pecho"], "medium", True, "collar rojo",
     "Perro marrón mediano perdido cerca de la plaza del Arenal, con mancha blanca en el pecho y collar rojo.",
     36.6826, -6.1376, "Plaza del Arenal, Jerez", "2026-09-20T10:00:00+02:00", "2026-09-19T18:00:00+02:00", "perro_marron_arenal.jpg", "active"),
    ("lost_002.json", "lost", "cat", "europeo", "negro", None, ["patas blancas"], "small", False, None,
     "Gata negra pequeña con patas blancas, vista por última vez en el barrio de San Joaquín.",
     36.6950, -6.1300, "San Joaquín, Jerez", "2026-09-18T09:00:00+02:00", "2026-09-17T20:00:00+02:00", "gata_negra_sanjoaquin.jpg", "active"),
    ("lost_003.json", "lost", "dog", "podenco", "blanco", "marrón", ["oreja marrón"], "medium", True, "collar azul",
     "Podenco blanco con oreja marrón, collar azul, perdido por la zona de Chapín.",
     36.6905, -6.1479, "Chapín, Jerez", "2026-09-15T12:00:00+02:00", "2026-09-14T19:00:00+02:00", "podenco_chapin.jpg", "active"),
    ("lost_004.json", "lost", "other", None, "verde", None, ["anillo gris"], "small", False, None,
     "Loro verde con anillo gris escapado en La Granja. Responde al nombre Curro.",
     36.7000, -6.1200, "La Granja, Jerez", "2026-09-19T08:00:00+02:00", "2026-09-18T09:00:00+02:00", "loro_verde_granja.jpg", "active"),
    ("lost_005.json", "lost", "cat", "siamés", "crema", "marrón", [], "small", True, "collar rosa con cascabel",
     "Gato siamés crema con collar rosa, dócil, perdido en el centro.",
     36.6810, -6.1390, "Centro, Jerez", "2026-08-10T10:00:00+02:00", "2026-08-09T10:00:00+02:00", "siames_centro.jpg", "resolved"),
    # FOUND (12)
    ("found_001.json", "found", "dog", "mestizo", "marrón", None, ["mancha blanca pecho"], "medium", True, "collar rojo",
     "Encontrado perro marrón mediano con mancha blanca en el pecho y collar rojo por el centro, muy dócil.",
     36.6836, -6.1386, "Centro, Jerez", "2026-09-20T12:00:00+02:00", "2026-09-20T08:00:00+02:00", "perro_marron_centro.jpg", "active"),
    ("found_002.json", "found", "dog", "mestizo", "negro", None, [], "large", False, None,
     "Perro negro grande sin collar encontrado junto al parque González Hontoria.",
     36.6750, -6.1190, "Parque González Hontoria", "2026-09-19T11:00:00+02:00", None, "perro_negro_parque.jpg", "active"),
    ("found_003.json", "found", "cat", "europeo", "negro", None, ["patas blancas"], "small", False, None,
     "Gata negra con patas blancas recogida en San Joaquín, maúlla mucho.",
     36.6955, -6.1310, "San Joaquín, Jerez", "2026-09-18T15:00:00+02:00", None, "gata_negra_encontrada.jpg", "active"),
    ("found_004.json", "found", "dog", "podenco", "blanco", "marrón", [], "medium", False, None,
     "Podenco blanco sin collar visto corriendo por Chapín.",
     36.6910, -6.1480, "Chapín, Jerez", "2026-09-16T10:00:00+02:00", None, "podenco_blanco.jpg", "active"),
    ("found_005.json", "found", "other", None, "verde", None, [], "small", False, None,
     "Loro verde encontrado en un balcón de La Granja.",
     36.7005, -6.1210, "La Granja, Jerez", "2026-09-19T14:00:00+02:00", None, "loro_verde.jpg", "active"),
    ("found_006.json", "found", "cat", "atigrado", "gris", None, ["rayas"], "small", True, "collar verde",
     "Gato atigrado gris con collar verde en el barrio de Santiago.",
     36.6880, -6.1400, "Santiago, Jerez", "2026-09-17T10:00:00+02:00", None, "gato_gris_santiago.jpg", "active"),
    ("found_007.json", "found", "dog", "bulldog", "blanco", "marrón", ["mancha ojo"], "medium", True, "collar negro",
     "Bulldog blanco y marrón con collar negro en Puerta del Sur.",
     36.6700, -6.1500, "Puerta del Sur, Jerez", "2026-09-12T10:00:00+02:00", None, "bulldog_sur.jpg", "active"),
    ("found_008.json", "found", "other", None, "blanco", None, ["orejas largas"], "small", False, None,
     "Conejo blanco de orejas largas encontrado en el parque de La Plata.",
     36.6760, -6.1350, "La Plata, Jerez", "2026-09-18T10:00:00+02:00", None, "conejo_blanco.jpg", "active"),
    ("found_009.json", "found", "cat", "persa", "blanco", None, [], "medium", False, None,
     "Gato persa blanco sin collar en Vallesequillo.",
     36.7100, -6.1100, "Vallesequillo, Jerez", "2026-09-10T10:00:00+02:00", None, "persa_vallesequillo.jpg", "active"),
    ("found_010.json", "found", "dog", "galgo", "marrón", None, ["delgado"], "large", False, None,
     "Galgo marrón delgado sin collar en la carretera de Sevilla, lejos del centro.",
     36.7500, -6.0500, "Ctra. Sevilla", "2026-09-19T10:00:00+02:00", None, "galgo_ctra.jpg", "active"),
    ("found_011.json", "found", "dog", "mestizo", "marrón", None, [], "small", True, "collar rojo",
     "Cachorro marrón pequeño con collar rojo en El Pelirón.",
     36.6600, -6.1600, "El Pelirón, Jerez", "2026-08-01T10:00:00+02:00", None, "cachorro_peliron.jpg", "active"),
    ("found_012.json", "found", "cat", "europeo", "naranja", None, ["cola rayada"], "medium", False, None,
     "Gato naranja de cola rayada en Icovesa.",
     36.6860, -6.1280, "Icovesa, Jerez", "2026-09-20T09:00:00+02:00", None, "gato_naranja.jpg", "active"),
]

COLORS = {"marrón": (139, 69, 19), "negro": (30, 30, 30), "blanco": (230, 230, 230),
          "verde": (60, 160, 60), "gris": (130, 130, 130), "crema": (235, 220, 190), "naranja": (230, 140, 40)}


def main():
    for d in (LOST, FOUND, IMG):
        d.mkdir(parents=True, exist_ok=True)
    for (fn, tipo, animal, breed, c1, c2, marks, size, collar, collar_d, desc,
         lat, lng, addr, rep, seen, img, status) in A:
        folder = LOST if tipo == "lost" else FOUND
        doc = {"id": fn.replace(".json", ""), "type": tipo, "animal": animal,
               "breed_guess": breed, "color_primary": c1, "color_secondary": c2,
               "markings": marks, "size": size, "has_collar": collar,
               "collar_description": collar_d, "description_text": desc,
               "location": {"lat": lat, "lng": lng, "address_text": addr},
               "date_reported": rep, "date_last_seen": seen,
               "image_url": f"data/seed/images/{img}", "image_embedding": None,
               "contact_info": "600 123 456", "status": status}
        (folder / fn).write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
    # placeholders
    try:
        from PIL import Image
        done = 0
        for (fn, *_rest, img, _s) in A:
            color = COLORS.get((_rest[3] if len(_rest) > 3 else "gris"), (130, 130, 130)) if False else None
            p = IMG / img
            if p.exists():
                continue
            # color por color_primary del doc
            import json as j
            folder = LOST if fn.startswith("lost") else FOUND
            doc = j.loads((folder / fn).read_text(encoding="utf-8"))
            rgb = COLORS.get(doc["color_primary"], (130, 130, 130))
            Image.new("RGB", (320, 240), rgb).save(p, "JPEG")
            done += 1
        print(f"seed: {len(A)} avisos + {done} imágenes placeholder")
    except ImportError:
        print(f"seed: {len(A)} avisos (sin PIL, imágenes no generadas)")


if __name__ == "__main__":
    main()
