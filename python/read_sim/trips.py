
import config as cfg
import os
import pandas as pd

sim_trips_path = os.path.join(
    cfg.DATA_DIR,
    'simulation_output_2/output_trips.csv'
)
df_sim_trips = pd.read_csv(sim_trips_path, sep=';')

df_sim_trips.rename(columns={'main_mode': 'mode'}, inplace=True)
df_sim_trips.rename(columns={'traveled_distance': 'distance'}, inplace=True)

if SMALL_DATA:
    df_sim_trips = df_sim_trips.head(10000)
df_sim_trips = df_sim_trips[['person', 'mode', 'distance', 'start_x', 'start_y', 'end_x', 'end_y']]
df_sim_trips = df_sim_trips[df_sim_trips['mode'] != 'outside']
df_sim_trips = df_sim_trips[df_sim_trips['mode'] != 'truck']

# clean modes: merge loop modes together
df_sim_trips['mode'] = df_sim_trips['mode'].str.replace('_loop', '', regex=False)

# remove super-short walks
sim_super_short_walks = df_sim_trips[(df_sim_trips['mode'] == 'walk') & (df_sim_trips['distance'] <= 1)]

print(f"removed super short walks in simulation: %d", len(sim_super_short_walks))
df_sim_trips = df_sim_trips[~df_sim_trips.index.isin(sim_super_short_walks.index)]

print(df_sim_trips.head())
