package org.eqasim.switzerland.zurich;

import org.matsim.api.core.v01.Id;
import org.matsim.api.core.v01.Scenario;
import org.matsim.api.core.v01.population.Person;
import org.matsim.core.config.Config;
import org.matsim.core.config.ConfigUtils;
import org.matsim.core.scenario.ScenarioUtils;
import org.matsim.vehicles.Vehicle;
import org.matsim.vehicles.VehicleType;
import org.matsim.vehicles.VehicleUtils;
import org.matsim.vehicles.Vehicles;
import org.matsim.vehicles.MatsimVehicleWriter;

public class AddBikeVehicles {
    
    public static void main(String[] args) {
        String configPath = "scenarios/Zurich_10pct/zurich_10pct_config.xml"; //change to your config path
        String outputVehiclesFile = "scenarios/Zurich_10pct/new_vehicles.xml"; // can name as you like and change to the path you want to save the file 

        Config config = ConfigUtils.loadConfig(configPath);
        Scenario scenario = ScenarioUtils.loadScenario(config);

        Vehicles vehicles = scenario.getVehicles();

        // We define a bike vehicle type
        VehicleType bikeType = VehicleUtils.createVehicleType(Id.create("bike", VehicleType.class));
        bikeType.setMaximumVelocity(16.67); // can define yours based on your scenario
        bikeType.setPcuEquivalents(0.25); // can define yours
        vehicles.addVehicleType(bikeType);

        if (!vehicles.getVehicleTypes().containsKey(bikeType.getId())) {
            vehicles.addVehicleType(bikeType);
        } else {
            bikeType = vehicles.getVehicleTypes().get(bikeType.getId());
        }
        
        // Here we add a bike vehicle for each person
        for (Person person : scenario.getPopulation().getPersons().values()) {
            if (person.getId().toString().contains("freight")){
                continue;
            }
            Vehicle bikeVehicle = VehicleUtils.createVehicle(Id.createVehicleId(person.getId()), bikeType);
            vehicles.addVehicle(bikeVehicle);
        }

        new MatsimVehicleWriter(vehicles).writeFile(outputVehiclesFile);
    }
}