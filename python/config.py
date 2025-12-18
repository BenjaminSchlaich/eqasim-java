
import pathlib

ROOT_DIR = pathlib.Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
BOUNDARY_PATH = DATA_DIR / "Boundary" / "Zurich.shp"
SWISS_BOUNDARY_PATH = DATA_DIR / "Boundary" / "Switzerland.shp"
ETAPPEN_PATH = DATA_DIR / "microcensus" / "etappen.csv"
ETAPPEN_OUT = DATA_DIR / "microcensus" / "etappen_zurich.csv"
WEGE_PATH = DATA_DIR / "microcensus" / "wege.csv"
WEGE_OUT = DATA_DIR / "microcensus" / "wege_zurich.csv"
MZ_PATH = DATA_DIR
ENCODING = "latin1"
