#!/bin/sh
#SBATCH --job-name=matsim_simulation    #Name of the job
#SBATCH --ntasks=1                      #Requesting 1 node (is always 1)
#SBATCH --cpus-per-task=8               #Requesting 8 CPU
#SBATCH --mem-per-cpu=3G                #Requesting 3 Gb memory per core, 24 Gb in total 
#SBATCH --time=6:00:00                  #Requesting 6 hours run time

#Source the GDC stack
# source /cluster/project/gdc/shared/stack/GDCstack.sh

#Load the needed modules
# module load stack/2024-06
# module load gcc/12.2.0
# module load openjdk/21.0.3_9
# module load maven

cd ./eqasim-java/switzerland
# mvn --offline -DskipTests clean package
# mvn --offline exec:java -Dexec.mainClass="org.eqasim.switzerland.ch_cmdp.RunSimulation" -Dexec.args="--config-path /cluster/scratch/bschlaich/eqasim-java/Zurich_10pct/zurich_10pct_config.xml"
#  
mvn --offline exec:java \
  -Dexec.mainClass=org.eqasim.switzerland.ch_cmdp.RunSimulation \
  -Dexec.args="--config-path ../scenarios/Zurich_10pct/zurich_10pct_config.xml" \
  -Dexec.classpathScope=compile
