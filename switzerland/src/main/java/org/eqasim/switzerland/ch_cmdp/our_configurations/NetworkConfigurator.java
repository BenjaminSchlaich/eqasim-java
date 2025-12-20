package org.eqasim.switzerland.ch_cmdp.our_configurations;

import java.util.ArrayList;
import java.util.List;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.matsim.api.core.v01.Id;
import org.matsim.api.core.v01.Scenario;
import org.matsim.api.core.v01.network.Link;
import org.matsim.api.core.v01.network.Network;
import org.matsim.api.core.v01.population.Person;
import org.matsim.api.core.v01.population.PopulationWriter;
import org.matsim.core.config.Config;
import org.matsim.core.config.ConfigUtils;
import org.matsim.core.network.NetworkUtils;
import org.matsim.core.scenario.ScenarioUtils;
import org.matsim.vehicles.MatsimVehicleWriter;
import org.matsim.vehicles.PersonVehicles;
import org.matsim.vehicles.Vehicle;
import org.matsim.vehicles.VehicleType;
import org.matsim.vehicles.VehicleUtils;
import org.matsim.vehicles.Vehicles;

// XX this is entirely ours
public class NetworkConfigurator {
	private final static Logger logger = LogManager.getLogger(NetworkConfigurator.class);


    public void applySpeedFactor(Network network, double speedFactor) {
        List<Link> links = new ArrayList<>(network.getLinks().values());
        for (Link link : links) {
            double freespeed = link.getFreespeed();
            link.setFreespeed(freespeed * speedFactor);
        }
        logger.info("Applied speed factor of {} to network", speedFactor);
    }

    public void applySpeedFactor(String configPath, String outputPath, double speedFactor) {
        Network network = NetworkUtils.readNetwork(configPath);
        applySpeedFactor(network, speedFactor);
        NetworkUtils.writeNetwork(network, outputPath);
    }



    // String configPath = "scenarios/Zurich_10pct/zurich_10pct_config.xml";//"..\\scenarios\\Lausanne_10pct\\lausanne_10pctconfig.xml"; //change to your config path
    //     String outputVehiclesFile = "scenarios/Zurich_10pct/zurich_10pct_vehicles_new.xml.gz";//= "..\\scenarios\\Lausanne_10pct\\new_vehicles.xml"; // can name as you like and change to the path you want to save the file 
    //     String outputPopFile = "scenarios/Zurich_10pct/zurich_10pct_population_new.xml.gz";//= "..\\scenarios\\Lausanne_10pct\\new_vehicles.xml"; // can name as you like and change to the path you want to save the file 

    //     Config config = ConfigUtils.loadConfig(configPath);
    //     Scenario scenario = ScenarioUtils.loadScenario(config);


    public void addBikeVehicles(Scenario scenario) {
        Vehicles vehicles = scenario.getVehicles();
        String vehicleMode = "bike";

        // We define a bike vehicle type
        VehicleType bikeType = VehicleUtils.createVehicleType(Id.create(vehicleMode, VehicleType.class));
        bikeType.setMaximumVelocity(16.67); // can define yours based on your scenario
        bikeType.setPcuEquivalents(0.25); // can define yours
        bikeType.getCapacity().setSeats(1);
        vehicles.addVehicleType(bikeType);

        if (!vehicles.getVehicleTypes().containsKey(bikeType.getId())) {
            vehicles.addVehicleType(bikeType);
        } else {
            bikeType = vehicles.getVehicleTypes().get(bikeType.getId());
        }

        int bikeCounter = 0;
        int oldBikeCounter = 0;
        
        // Here we add a bike vehicle for each person that has a bike available at least FOR_SOME
        for (Person person : scenario.getPopulation().getPersons().values()) {
            if (person.getId().toString().contains("freight")){
                continue;
            }

            oldBikeCounter++;

            // do not give a bicycle to people who never have one available
            if(person.getAttributes().getAttribute("bikeAvailability").equals("FOR_NONE"))
                continue;
            else
                bikeCounter++;

            Id<Vehicle> vehicle_id = Id.createVehicleId(person.getId().toString()+ ":" + vehicleMode);
            
            Vehicle bikeVehicle = VehicleUtils.createVehicle(vehicle_id, bikeType);

            //add some attributes as added for other modes..e.g.
            bikeVehicle.getAttributes().putAttribute("euro", 6);

            vehicles.addVehicle(bikeVehicle);

            //update vehicles in the population file
            Object vehicle_attr = person.getAttributes().getAttribute("vehicles");
            PersonVehicles personVehicles;

            if (vehicle_attr == null) {
                personVehicles = new PersonVehicles();
            } else {
                personVehicles = (PersonVehicles) vehicle_attr;
            }

            personVehicles.addModeVehicle(vehicleMode, vehicle_id);

            person.getAttributes().putAttribute("vehicles", personVehicles);
            
        }

        logger.info("Added " + bikeCounter + " bikes instead of " + oldBikeCounter + ", because we're skipping if bikeAvailability=FOR_SOME");

        // new MatsimVehicleWriter(vehicles).writeFile(outputVehiclesFile);
        // new PopulationWriter(scenario.getPopulation()).write(outputPopFile);
    }

}
