import pandas as pd

SIMULATION = ['no-network', 'disable', 'stimulus', 'calcium']

def read_positions(sim_type: str):
    position_file_loc = f'data/viz-{sim_type}/positions/rank_0_positions.txt'
    cols = ["local_id", "pos_x", "pos_y", "pos_z", "area", "type"]

    # Skip lines with # as they are comments and rename the columns to be clearer
    pos_file = pd.read_csv(position_file_loc, delimiter = " ",comment='#', header = None, names = cols)

    # Change the areas as number only values so that visualization is easier in Paraview
    pos_file["area"] = pos_file["area"].str.replace("area_", repl= "")
    return pos_file

for sim in SIMULATION:
    file = read_positions(sim)
    file.to_csv(f'data/viz-{sim}/positions/rank_0_positions_editted.csv')
