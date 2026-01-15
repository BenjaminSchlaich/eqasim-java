package org.eqasim.switzerland.ch_cmdp;

import ch.sbb.matsim.config.SwissRailRaptorConfigGroup;
import ch.sbb.matsim.mobsim.qsim.SBBTransitModule;
import ch.sbb.matsim.mobsim.qsim.pt.SBBTransitEngineQSimModule;

import org.apache.commons.math3.genetics.Population;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.eqasim.core.components.fast_calibration.AlphaCalibrator;
import org.eqasim.core.simulation.OurGlobalParameters;
import org.eqasim.switzerland.ch.PTLinkVolumesModule;
import org.eqasim.switzerland.ch.PTPassengerCountsModule;
import org.eqasim.switzerland.ch_cmdp.our_configurations.NetworkConfigurator;
import org.eqasim.switzerland.ch_cmdp.our_configurations.PopulationConfigurator;
import org.matsim.api.core.v01.Id;
import org.matsim.api.core.v01.Scenario;
import org.matsim.api.core.v01.network.Link;
import org.matsim.core.config.CommandLine;
import org.matsim.core.config.CommandLine.ConfigurationException;
import org.matsim.core.config.Config;
import org.matsim.core.config.ConfigUtils;
import org.matsim.core.config.groups.QSimConfigGroup;
import org.matsim.core.controler.Controler;
import org.matsim.core.network.NetworkUtils;
import org.matsim.core.router.TripRouterFactoryBuilderWithDefaults;
import org.matsim.core.scenario.ScenarioUtils;

import java.io.IOException;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;


public class RunSimulation {

	private final static Logger logger = LogManager.getLogger(RunSimulation.class);


	@SuppressWarnings("deprecation")
	static public void main(String[] args) throws ConfigurationException, IOException {
		// set preventwaitingtoentertraffic to y if you want to to prevent that waiting traffic has to wait for space in the link buffer
		// this is especially important to avoid high waiting times when we cutout scenarios from a larger scenario.
		CommandLine cmd = new CommandLine.Builder(args) //
				.requireOptions("config-path") //
				.allowPrefixes("mode-parameter", "cost-parameter", "preventwaitingtoentertraffic", "samplingRateForPT") //
				// XX these are our prefixes:
				.allowPrefixes("add-bike-vehicles", "bike-bias", "car-bias", "pt-bias", "population-wealth-factor", "network-speed-factor", "population-bike-chance", "early-exit", "remove-elevation", "redistribute-bikes", "bike-max-velocity", "car-penalty-per-km") //
				.build();

		SwitzerlandConfigurator configurator = new SwitzerlandConfigurator(cmd);
		Config config = ConfigUtils.loadConfig(cmd.getOptionStrict("config-path"));
		configurator.updateConfig(config);
		configurator.configure(config);
		cmd.applyConfiguration(config);

		if (cmd.hasOption("preventwaitingtoentertraffic")) {
			if (cmd.getOption("preventwaitingtoentertraffic").get().equals("y")) {
				((QSimConfigGroup) config.getModules().get(QSimConfigGroup.GROUP_NAME))
						.setPcuThresholdForFlowCapacityEasing(1.0);
			}
		}

		Scenario scenario = ScenarioUtils.createScenario(config);

		SwissRailRaptorConfigGroup srrConfigGroup = (SwissRailRaptorConfigGroup) config.getModules().getOrDefault("swissRailRaptor", null);
		System.out.println("Found the following transfer penalties: " + srrConfigGroup.getModeToModeTransferPenaltyParameterSets());

		configurator.configureScenario(scenario);
		ScenarioUtils.loadScenario(scenario);
		configurator.adjustScenario(scenario);
		configurator.adjustPTpcu(scenario);


		if (cmd.hasOption("bike-max-velocity")) {
			OurGlobalParameters.BIKE_MAX_VELOCITY_MS = Double.parseDouble(cmd.getOption("bike-max-velocity").get());
			logger.info("Setting bike max velocity to " + OurGlobalParameters.BIKE_MAX_VELOCITY_MS + " m/s");
		}

		// XX TODO: this experiment has kinda failed, since this code previously ran after add-bike-vehicles
		if (cmd.hasOption("redistribute-bikes")) {
			PopulationConfigurator populationConfigurator = new PopulationConfigurator();
			populationConfigurator.redistributeBikes(scenario.getPopulation());
			logger.info("Redistributing bikes in the scenario.");
		}


		if (cmd.hasOption("add-bike-vehicles")) {
			NetworkConfigurator networkConfigurator = new NetworkConfigurator();
			networkConfigurator.addBikeVehicles(scenario);


			// iterate over the whole network and add bike to the link
			int linksWithCar = 0;
			int totalLinks = 0;
			List<Link> links = new ArrayList<>(scenario.getNetwork().getLinks().values());
			for (Link link : links) {
				totalLinks++;
				if (link.getAllowedModes().contains("car")) {
					linksWithCar++;
					Set<String> allowedModes = new HashSet<>();
					allowedModes.addAll(link.getAllowedModes());
					allowedModes.add("bike");
	
					link.setAllowedModes(allowedModes);
				}
			}

			// Get the set of modes from the network before cleaning
			// Set<String> modesBeforeCleaning = NetworkUtils.getModes(scenario.getNetwork());
			// NetworkUtils.cleanNetwork(scenario.getNetwork(), modesBeforeCleaning);

			logger.info("Links with car previously: " + linksWithCar + " out of " + totalLinks);

			OurGlobalParameters.index_to_get_bike = 2;
			logger.info("Added bike vehicles to the scenario.");
		}

		if (cmd.hasOption("remove-elevation")) {
			OurGlobalParameters.REMOVE_ELEVATION = true;
			logger.info("Removing elevation data from the scenario.");
		}


		
		// XX extract new command line args:
		if (cmd.hasOption("bike-bias")) {
			OurGlobalParameters.BIKE_BIAS = Double.parseDouble(cmd.getOption("bike-bias").get());
			logger.info("Setting bike bias to " + OurGlobalParameters.BIKE_BIAS);
		}

		if (cmd.hasOption("car-bias")) {
			OurGlobalParameters.CAR_BIAS = Double.parseDouble(cmd.getOption("car-bias").get());
			logger.info("Setting car bias to " + OurGlobalParameters.CAR_BIAS);
		}

		if (cmd.hasOption("pt-bias")) {
			OurGlobalParameters.PT_BIAS = Double.parseDouble(cmd.getOption("pt-bias").get());
			logger.info("Setting pt bias to " + OurGlobalParameters.PT_BIAS);
		}

		if (cmd.hasOption("population-wealth-factor")) {
			double wealthFactor = Double.parseDouble(cmd.getOption("population-wealth-factor").get());
			PopulationConfigurator populationConfigurator = new PopulationConfigurator();
			populationConfigurator.applyWealthFactor(scenario.getPopulation(), wealthFactor);
			logger.info("Setting population wealth factor to " + wealthFactor);
		}

		if (cmd.hasOption("network-speed-factor")) {
			double speedFactor = Double.parseDouble(cmd.getOption("network-speed-factor").get());
			NetworkConfigurator networkConfigurator = new NetworkConfigurator();
			networkConfigurator.applySpeedFactor(scenario.getNetwork(), speedFactor);
			logger.info("Setting network speed factor to " + speedFactor);
		}

		if (cmd.hasOption("population-bike-chance")) {
			double bikeChance = Double.parseDouble(cmd.getOption("population-bike-chance").get());
			PopulationConfigurator populationConfigurator = new PopulationConfigurator();
			populationConfigurator.giveBikes(scenario.getPopulation(), bikeChance);
			logger.info("Setting population bike chance to " + bikeChance);
		}

		if (cmd.hasOption("car-penalty-per-km")) {
			OurGlobalParameters.CAR_ADDITIONAL_COST_PER_KM = Double.parseDouble(cmd.getOption("car-penalty-per-km").get());
			logger.info("Setting car additional cost per km to " + OurGlobalParameters.CAR_ADDITIONAL_COST_PER_KM + " CHF/km");
		}


		if (cmd.hasOption("early-exit")) {
			logger.info("Early exit after scenario loading as requested.");
			return;
		}




		Controler controller = new Controler(scenario);
		configurator.configureController(controller);
		controller.addOverridingModule(new PTPassengerCountsModule());
		controller.addOverridingModule(new PTLinkVolumesModule());


		// To use the deterministic pt simulation (Part 1 of 2):
		controller.addOverridingModule(new SBBTransitModule());
		// To use the deterministic pt simulation (Part 2 of 2):
		controller.configureQSimComponents(components -> {
			new SBBTransitEngineQSimModule().configure(components);

		});

		// 2025-12-05T20:11:01,299  WARN CoordUtils:393 Mix of 2D / 3D coordinates. Assuming 2D only.


		// XX logging coordinates of nodes for debugging
		
		// for (var node : scenario.getNetwork().getNodes().values()) {
		// 	logger.info("XX Node " + node.getId() + " has coordinates: " + node.getCoord());
		// }
		
		
		// for (var link : scenario.getNetwork().getLinks().values()) {
			// 	logger.info("XX Link " + link.getId() + " has attributes: " + link.getCoord());
			// 	logger.info("XX Link " + link.getId() + " has attributes: " + link.getAttributes());
			// }
			// TODO: try to find a way for z coords to be also added Activity s
			
		controller.run();
	}
}