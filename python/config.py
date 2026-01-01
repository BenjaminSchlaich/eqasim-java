
import pathlib

# general
ROOT_DIR = pathlib.Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
BOUNDARY_PATH = DATA_DIR / "Boundary" / "Zurich.shp"
SWISS_BOUNDARY_PATH = DATA_DIR / "Boundary" / "Switzerland.shp"
SMALL_DATA = True

# microcensus
ETAPPEN_PATH = DATA_DIR / "microcensus" / "etappen.csv"
ETAPPEN_OUT = DATA_DIR / "microcensus" / "etappen_zurich.csv"
WEGE_PATH = DATA_DIR / "microcensus" / "wege.csv"
WEGE_OUT = DATA_DIR / "microcensus" / "wege_zurich.csv"
MZ_PATH = DATA_DIR

# simulation output
SIM_TRIPS = DATA_DIR / "simulation_output" / "output_trips.csv"
SIM_PERSONS = DATA_DIR / "simulation_output" / "output_persons.csv"

ENCODING = "latin1"
