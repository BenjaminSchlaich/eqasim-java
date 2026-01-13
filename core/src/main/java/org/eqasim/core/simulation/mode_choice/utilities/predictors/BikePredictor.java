package org.eqasim.core.simulation.mode_choice.utilities.predictors;

import java.util.List;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.eqasim.core.analysis.run.RunActivityAnalysis;
import org.eqasim.core.simulation.OurGlobalParameters;
import org.eqasim.core.simulation.mode_choice.utilities.variables.BikeVariables;
import org.matsim.api.core.v01.TransportMode;
import org.matsim.api.core.v01.network.Network;
import org.matsim.api.core.v01.network.Node;
import org.matsim.api.core.v01.population.Activity;
import org.matsim.api.core.v01.population.Leg;
import org.matsim.api.core.v01.population.Person;
import org.matsim.api.core.v01.population.PlanElement;
import org.matsim.contribs.discrete_mode_choice.model.DiscreteModeChoiceTrip;
import org.matsim.core.router.TripStructureUtils;


import com.google.common.base.Verify;
import com.google.inject.Inject;

public class BikePredictor extends CachedVariablePredictor<BikeVariables> {

	// XX our logger
	private final static Logger logger = LogManager.getLogger(BikePredictor.class);




    private final Network network;

	// XX constructor with network injection

    @Inject
    public BikePredictor(Network network) {
        this.network = network;
		// print success message
		logger.info("BikePredictor initialized with network.");
    }




	@Override
	public BikeVariables predict(Person person, DiscreteModeChoiceTrip trip, List<? extends PlanElement> elements) {

		// XX .get(2) because the bike trip is at index 2 in the chain walk-bikeinteraction-bike-bikeinteraction-walk
		// XX TODO, get(2) gets out of bounds exception, so we use a safe way
		double travelTime_min = 0.0;

		int special_bike_index = OurGlobalParameters.index_to_get_bike;

		if (elements.size() >= special_bike_index + 1) {
			travelTime_min = ((Leg) elements.get(special_bike_index)).getTravelTime().seconds() / 60.0;
			logger.info("Trip elements size is sufficient to get bike leg travel time: " + travelTime_min + " minutes.");

		} else {
			// log a warning
			travelTime_min = ((Leg) elements.get(0)).getTravelTime().seconds() / 60.0;
			logger.warn("Trip elements size is less than 3, cannot get bike leg travel time. Setting travel time to " + travelTime_min + " minutes.");
		}

		// XX placeholder for slope calculation
		double slope = 0.0;
		// Get first Plan Element
		// print call stack for debugging



		// TODO: is this Z ever set?
		// Check if getz is valid


		List<Leg> legs = TripStructureUtils.getLegs(elements);
		// Get first and last leg
		Leg firstLeg = legs.get(0);
		Leg lastLeg = legs.get(legs.size() - 1);

		firstLeg.getRoute().getStartLinkId();
		// print found start link id for debugging
		// logger.info("Start link ID: " + firstLeg.getRoute().getStartLinkId());
		lastLeg.getRoute().getEndLinkId();
		// print found end link id for debugging
		// logger.info("End link ID: " + lastLeg.getRoute().getEndLinkId());

		Node originNode = network.getLinks().get(firstLeg.getRoute().getStartLinkId()).getFromNode();
		Node destinationNode = network.getLinks().get(lastLeg.getRoute().getEndLinkId()).getToNode();


		// print origin and destination node ids for debugging
		// logger.info("Origin node ID: " + originNode.getId());
		// logger.info("Destination node ID: " + destinationNode.getId());

		
		double originHeight = 0.0;
		if (originNode.getCoord().hasZ()) {
			originHeight = originNode.getCoord().getZ();
		} else {
			logger.warn("Origin activity does not have a valid z-coordinate.");
		}
		
		double destinationHeight = 0.0;
		if (destinationNode.getCoord().hasZ()) {
			destinationHeight = destinationNode.getCoord().getZ();
		} else {
			logger.warn("Destination activity does not have a valid z-coordinate.");
		}
		
		// print the heights for debugging
		// logger.info("Origin height: " + originHeight);
		// logger.info("Destination height: " + destinationHeight);
		double distance_in_m = PredictorUtils.calculateEuclideanDistance_km(trip) * 1000.0;
		
		slope = (destinationHeight - originHeight) / distance_in_m * 100.0; // slope in percentage
		// log the slope calculation process
		logger.info("Calculated slope (as percentage): (destHeight " + destinationHeight + " - origHeight " + originHeight + ") / euclideanDistance_m " + distance_in_m + " = " + slope);

		// Check if nan:
		if (!Double.isFinite(slope)) {
			slope = 0.0;
			logger.warn("Slope calculation resulted in NaN, setting slope to 0.0");
			// Print all available info for debugging
			logger.warn("Origin height: " + originHeight + ", Destination height: " + destinationHeight + ", Euclidean distance (km): " + PredictorUtils.calculateEuclideanDistance_km(trip));
			// Print ids
			logger.warn("Origin node ID: " + originNode.getId() + ", Destination node ID: " + destinationNode.getId());
			logger.warn("Origin link ID: " + firstLeg.getRoute().getStartLinkId() + ", Destination link ID: " + lastLeg.getRoute().getEndLinkId());
		}
		

		return new BikeVariables(travelTime_min, slope);
	}
}
