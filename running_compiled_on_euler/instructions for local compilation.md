Make sure that locally, the inner pom file has this line:
```
<mainClass>org.eqasim.switzerland.zurich.RunSimulation</mainClass>
```
Which specifies the main class to be used when running the jar. You can of course change this to any other main class you want to run.

First, compile the project with:
```
mvn clean package -Pstandalone -pl switzerland -am -DskipTests
```

This gives you multiple jar files in the inner `target` folder. Then copy the `switzerland-2.0.0.jar` file to the cluster.

Also have the scenario on the cluster (at `scenarios/Zurich_10pct`) and move the jar file to the same folder as the config file, because there is a buy that prevents the locating of the .csv and .yml files otherwise.

The `jar_job.sh` file should load these modules:
```
module load stack/2024-06 openjdk/21.0.3_9
```
From `scratch/<your_user>` run the following command to submit the job:
```
sbatch < jar_job.sh 
```

Check the queue with
```
squeue -u lfrieberger -i 20
```
