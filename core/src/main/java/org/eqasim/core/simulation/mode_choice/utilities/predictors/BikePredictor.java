package org.eqasim.core.simulation.mode_choice.utilities.predictors;

import java.util.List;

import org.eqasim.core.simulation.mode_choice.utilities.variables.BikeVariables;
import org.matsim.api.core.v01.population.Leg;
import org.matsim.api.core.v01.population.Person;
import org.matsim.api.core.v01.population.PlanElement;
import org.matsim.contribs.discrete_mode_choice.model.DiscreteModeChoiceTrip;

public class BikePredictor extends CachedVariablePredictor<BikeVariables> {
	@Override
	public BikeVariables predict(Person person, DiscreteModeChoiceTrip trip, List<? extends PlanElement> elements) {

		// XX .get(2) because the bike trip is at index 2 in the chain walk-bikeinteraction-bike-bikeinteraction-walk
		double travelTime_min = ((Leg) elements.get(0)).getTravelTime().seconds() / 60.0;

		return new BikeVariables(travelTime_min);
	}
}
