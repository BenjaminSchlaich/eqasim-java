package org.eqasim.switzerland.ch_cmdp.mode_choice.costs;

import com.google.inject.Inject;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.eqasim.core.simulation.OurGlobalParameters;
import org.eqasim.core.simulation.mode_choice.cost.AbstractCostModel;
import org.eqasim.switzerland.ch_cmdp.mode_choice.parameters.SwissCostParameters;
import org.eqasim.switzerland.ch_cmdp.mode_choice.utilities.estimators.SwissBikeDetailedUtilityEstimator;
import org.matsim.api.core.v01.population.Person;
import org.matsim.api.core.v01.population.PlanElement;
import org.matsim.contribs.discrete_mode_choice.model.DiscreteModeChoiceTrip;

import java.util.List;

public class SwissCarCostModel extends AbstractCostModel {
	private static final Logger logger = LogManager.getLogger(SwissCarCostModel.class);

	private final SwissCostParameters parameters;

	@Inject
	public SwissCarCostModel(SwissCostParameters costParameters) {
		super("car");
		this.parameters = costParameters;
	}

	@Override
	public double calculateCost_MU(Person person, DiscreteModeChoiceTrip trip, List<? extends PlanElement> elements) {
		logger.info("The car_cost_CHF_km is: " + parameters.carCost_CHF_km);
		logger.info("The additional car cost per km is: " + OurGlobalParameters.CAR_ADDITIONAL_COST_PER_KM);
		logger.info("The distance in km is: " + getInVehicleDistance_km(elements));

		return (parameters.carCost_CHF_km + OurGlobalParameters.CAR_ADDITIONAL_COST_PER_KM) * getInVehicleDistance_km(elements);
	}
}
