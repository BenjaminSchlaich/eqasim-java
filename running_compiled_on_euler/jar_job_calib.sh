#!/bin/sh
#SBATCH --job-name=matsim_simulation    #Name of the job
#SBATCH --ntasks=1                      #Requesting 1 node (is always 1)
#SBATCH --cpus-per-task=8               #Requesting 8 CPU
#SBATCH --mem-per-cpu=16G                #Requesting 3 Gb memory per core, 24 Gb in total 
#SBATCH --time=30:00:00                  #Requesting 30 hours run time
#SBATCH --mail-user=lfrieberger@ethz.ch     # or your preferred email address  
#SBATCH --mail-type=END,FAIL               # or BEGIN,ALL, etc.

#Source the GDC stack
# source /cluster/project/gdc/shared/stack/GDCstack.sh

#Load the needed modules
# module load stack/2024-06
# module load gcc/12.2.0
# module load openjdk/21.0.3_9
# module load maven

# module load stack/2024-06 openjdk/21.0.3_9

cd scenarios/Zurich_10pct

# mv simulation_output simulation_output_else


# mvn --offline -DskipTests clean package
# mvn --offline exec:java -Dexec.mainClass="org.eqasim.switzerland.ch_cmdp.RunSimulation" -Dexec.args="--config-path /cluster/scratch/bschlaich/eqasim-java/Zurich_10pct/zurich_10pct_config.xml"
#  
# java -jar switzerland-2.0.0-pt-hate.jar --config-path zurich_10pct_config.xml

# mv simulation_output simulation_output_pt_hate

# TODO: activate alphaCalibration in the config and set level parameter to global instead of canton
# set the expected values in canton_mode_share_csv 
# RUN
# Look in the it.60 folder for 60.alphas.csv file and take the alphas for zurich and put it in estimated_dmc_parameters.yml file
# Disable calibration again in the config for the next runs

java -jar switzerland-2.0.0.jar --config-path zurich_10pct_config_calib.xml --add-bike-vehicles
# This is with true, and canton in the config and the goal mode shares in the csv file
# mv simulation_output simulation_output_calibration_after_presentation

# idem, but now goal mode shares are also in the config file
mv simulation_output simulation_output_calibration


