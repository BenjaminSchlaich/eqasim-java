package org.eqasim.switzerland.ch_cmdp.util;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Random;
import java.util.stream.Collectors;
import java.util.stream.Stream;

import javax.imageio.ImageIO;

import org.apache.commons.math3.analysis.function.Add;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.matsim.api.core.v01.Coord;
import org.matsim.api.core.v01.Scenario;
import org.matsim.api.core.v01.network.Network;
import org.matsim.api.core.v01.network.NetworkWriter;
import org.matsim.core.config.Config;
import org.matsim.core.config.ConfigUtils;
import org.matsim.core.network.NetworkUtils;
import org.matsim.core.scenario.ScenarioUtils;
import org.matsim.core.utils.geometry.CoordUtils;

import java.awt.Color;
import java.awt.Graphics2D;
import java.awt.image.BufferedImage;

// TODO: this code should work, but I could not test it, since I do not have the ram on my laptop

public class LoadAndTestZCoordsInNetwork {
    
    static Logger logger = LogManager.getLogger(LoadAndTestZCoordsInNetwork.class);



    public static void main(String[] args) {

        // Get the first command line argument as the config path
        String configPath = args.length > 0 ? args[0] : "scenarios/Zurich_10pct/zurich_10pct_config.xml";

    

        Config config = ConfigUtils.loadConfig(configPath);

        logger.info("Config loaded from: " + configPath);

        Scenario scenario = ScenarioUtils.loadScenario(config);
        Network network = scenario.getNetwork();

        Network netterworker = NetworkUtils.readNetwork("scenarios/Zurich_10pct/zurich_10pct_network.xml");



        int i = 0;
        int cap = 10;
        for (var node : scenario.getNetwork().getNodes().values()) {
            if (i >= cap) break;
            i++;
			logger.info("XX Node " + node.getId() + " has coordinates: " + node.getCoord());
		}

        i = 0;

        for (var node : netterworker.getNodes().values()) {
            if (i >= cap) break;
            i++;
			logger.info("YY Node " + node.getId() + " has coordinates: " + node.getCoord());
		}
    }
}










        

        // CommandLine cmd = new CommandLine.Builder(args) //
        //         .requireOptions("config-path") //
        //         .allowPrefixes("mode-parameter", "cost-parameter", "preventwaitingtoentertraffic") //
        //         .build();

        // SwitzerlandConfigurator configurator = new SwitzerlandConfigurator(cmd);

        // Config config = ConfigUtils.loadConfig(cmd.getOptionStrict("config-path"));
        
        // configurator.updateConfig(config);
        // cmd.applyConfiguration(config);


        // if (cmd.hasOption("preventwaitingtoentertraffic")) {
        //     if (cmd.getOption("preventwaitingtoentertraffic").get().equals("y")) {
        //         ((QSimConfigGroup) config.getModules().get(QSimConfigGroup.GROUP_NAME))
        //                 .setPcuThresholdForFlowCapacityEasing(1.0);
        //     }
        // }



        // // VDF: Disable queue logic
        // config.qsim().setFlowCapFactor(1e9);

        // // maybe we do not want to disable storage capacity logic
        // // as we might want to have some back propagation delays
        // config.qsim().setStorageCapFactor(1e9);

        // // VDF: Optional
        // VDFConfigGroup.getOrCreate(config).setWriteInterval(10);
        // VDFConfigGroup.getOrCreate(config).setWriteFlowInterval(10);

        // // VDF Engine: Decide whether to genertae link events or not
        // VDFEngineConfigGroup.getOrCreate(config).setGenerateNetworkEvents(false);

        // // VDF Engine: Remove car from main modes
        // Set<String> mainModes = new HashSet<>(config.qsim().getMainModes());
        // mainModes.remove("car");
        // config.qsim().setMainModes(mainModes);

        // Scenario scenario = ScenarioUtils.createScenario(config);
        // configurator.configureScenario(scenario);
        // ScenarioUtils.loadScenario(scenario);
        // configurator.adjustScenario(scenario);

        // Controler controller = new Controler(scenario);
        // configurator.configureController(controller);
        // controller.run();


        

    
        // Population population = scenario.getPopulation();

        // //Read the population file of interest into the population container
        // PopulationReader popReader = new PopulationReader(scenario);
        // popReader.readFile(args[0]);
       


        // //To get the information we need, first have to go through all the persons in the population file and
        // for (Person person: population.getPersons().values() ){

        //     //Initialize the variables we need

        //     String activity_type = "";
        //     double x = 0.0;
        //     double y = 0.0;

        //     //Then we need to go through the plans to get the activities for each person.
        //     // First you want the selected plan of the person, if it is an output file we are reading
        //     //Then to access the individual contents of the plans, these are the plan elements,
        //     // the plan has two instances - activity and leg

        //     for (PlanElement element: person.getSelectedPlan().getPlanElements()){
        //         //check for the instance we need - activity
        //         if(element instanceof Activity) {
        //             Activity activity = (Activity) element;
        //             activity_type = activity.getType();
        //             x = activity.getCoord().getX();
        //             y = activity.getCoord().getY();

        //             //Write out activities for each person
        //             writer.write(person.getId().toString() + ";"
        //                     + person.getAttributes().getAttribute("age") + ";"
        //                     + person.getAttributes().getAttribute("sex") + ";"
        //                     + activity_type + ";"
        //                     + x + ";"
        //                     + y + "\n"
        //             );

        //         }

        //     }



        // }

        // //we have to close the writer
        // writer.flush();
        // writer.close();