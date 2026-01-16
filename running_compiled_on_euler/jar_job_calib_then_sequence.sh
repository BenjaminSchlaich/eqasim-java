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

java -jar switzerland-2.0.0.jar --config-path zurich_10pct_config_calib.xml --add-bike-vehicles
mv simulation_output simulation_output_calibration


java -jar ExtractCalibrationResults.jar


# java -jar switzerland-2.0.0.jar --config-path zurich_10pct_config.xml --add-bike-vehicles --remove-elevation
# mv simulation_output simulation_output_no_elevation


java -jar switzerland-2.0.0.jar --config-path zurich_10pct_config.xml --add-bike-vehicles --bike-max-velocity 10
mv simulation_output simulation_output_bike_max_velocity_10


# java -jar switzerland-2.0.0.jar --config-path zurich_10pct_config.xml --add-bike-vehicles --redistribute-bikes
# mv simulation_output simulation_output_redistribute_bikes
