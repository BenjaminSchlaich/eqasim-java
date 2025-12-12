#!/bin/sh
#SBATCH --job-name=matsim_simulation    #Name of the job
#SBATCH --ntasks=1                      #Requesting 1 node (is always 1)
#SBATCH --cpus-per-task=8               #Requesting 8 CPU
#SBATCH --mem-per-cpu=16G                #Requesting 3 Gb memory per core, 24 Gb in total 
#SBATCH --time=6:00:00                  #Requesting 6 hours run time
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

java -jar switzerland-2.0.0.jar --config-path zurich_10pct_config.xml --early-exit
mv simulation_output simulation_output_default

java -jar switzerland-2.0.0.jar --config-path zurich_10pct_config.xml --bike-bias 1000 --early-exit
mv simulation_output simulation_output_bike_bias

java -jar switzerland-2.0.0.jar --config-path zurich_10pct_config.xml --car-bias -1000 --early-exit
mv simulation_output simulation_output_car_bias

java -jar switzerland-2.0.0.jar --config-path zurich_10pct_config.xml --pt-bias -1000 --early-exit
mv simulation_output simulation_output_pt_bias

java -jar switzerland-2.0.0.jar --config-path zurich_10pct_config.xml --population-wealth-factor 0.01 --early-exit
mv simulation_output simulation_output_low_wealth

java -jar switzerland-2.0.0.jar --config-path zurich_10pct_config.xml --network-speed-factor 0.1 --early-exit
mv simulation_output simulation_output_low_network_speed

java -jar switzerland-2.0.0.jar --config-path zurich_10pct_config.xml --population-bike-chance 1.0 --early-exit
mv simulation_output simulation_output_high_bike_chance





