"""Ruth's painting composed from the element library. Canvas 1104 by 2768, as the traced source."""
import sys
from compose import lib, symbols, use
G = "#a37d33"
def shape(fill, d): return f'<path fill="{fill}" stroke="{G}" stroke-width="4" stroke-linejoin="round" d="{d}"/>'
def row(name, xs, bottom, height, jitter=0):
    return "".join(use(name, x, bottom + (i % 2) * jitter, height * (1 - 0.08 * (i % 3)), flip=i % 2 == 1) for i, x in enumerate(xs))
seals = {
 "cover": shape("#ecd9a0", "M270 2570 Q552 2530 840 2575 L860 2710 Q552 2740 250 2710 Z") + use("sheaf", 552, 2700, 900),
 "moab": shape("#7c8b3f", "M15 1760 Q40 1470 330 1440 Q640 1430 760 1620 L680 1850 Q340 1920 50 1860 Z")
       + shape("#c9b48f", "M25 1815 Q340 1750 740 1640 L725 1715 Q370 1850 45 1880 Z")
       + use("family", 350, 1795, 340),
 "return": shape("#c9b48f", "M560 1470 Q800 1380 1085 1410 L1092 1580 Q820 1640 590 1600 Z") + use("clinging", 860, 1560, 520),
 "field": shape("#ecd9a0", "M15 640 Q300 560 620 600 Q900 580 1090 650 L1092 1180 Q900 1230 640 1290 Q300 1340 12 1240 Z")
       + row("barley", [110, 320, 520], 880, 360, 14)
       + use("reaper_green", 700, 850, 250) + use("reaper_brown", 950, 870, 250, flip=True)
       + row("barley", [70, 250, 640, 830, 1020], 1080, 400, 18)
       + use("gleaner", 400, 1150, 400)
       + row("barley", [120, 600], 1300, 420, 16) + row("ear", [300, 470], 1300, 180),
 "night": shape("#2f4f77", "M500 560 Q460 370 600 280 Q700 140 860 180 Q1020 130 1078 300 Q1104 440 1070 565 Z")
       + use("moon", 960, 360, 120) + shape("#c9b48f", "M515 548 L1080 548 L1090 600 L505 600 Z") + use("winnower", 740, 552, 350),
 "gate": use("gate", 255, 560, 500) + use("elders", 257, 470, 150),
}
order = ["cover", "moab", "field", "return", "night", "gate"]
names = ["sheaf", "family", "clinging", "barley", "reaper_green", "reaper_brown", "gleaner", "ear", "moon", "winnower", "gate", "elders"]
style = sys.argv[2] if len(sys.argv) > 2 else ""
body = "".join(f'<g data-seal="{k}">{seals[k]}</g>' for k in order)
open(sys.argv[1], "w").write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1104 2768"><style>{style}</style><defs>{symbols(names)}</defs>{body}</svg>')
