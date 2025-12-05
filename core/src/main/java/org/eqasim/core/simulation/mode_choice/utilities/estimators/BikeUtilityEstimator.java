package org.eqasim.core.simulation.mode_choice.utilities.estimators;

import java.util.List;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.eqasim.core.components.fast_calibration.AlphaCalibrator;
import org.eqasim.core.simulation.mode_choice.parameters.ModeParameters;
import org.eqasim.core.simulation.mode_choice.utilities.UtilityEstimator;
import org.eqasim.core.simulation.mode_choice.utilities.predictors.BikePredictor;
import org.eqasim.core.simulation.mode_choice.utilities.predictors.PersonPredictor;
import org.eqasim.core.simulation.mode_choice.utilities.variables.BikeVariables;
import org.eqasim.core.simulation.mode_choice.utilities.variables.PersonVariables;
import org.matsim.api.core.v01.population.Person;
import org.matsim.api.core.v01.population.PlanElement;
import org.matsim.contribs.discrete_mode_choice.model.DiscreteModeChoiceTrip;

import com.google.inject.Inject;

public class BikeUtilityEstimator implements UtilityEstimator {
	private final ModeParameters parameters;
	private final BikePredictor bikePredictor;
	private final PersonPredictor personPredictor;

	// XX For logging purposes
	private static final Logger logger = LogManager.getLogger(BikeUtilityEstimator.class);


	@Inject
	public BikeUtilityEstimator(ModeParameters parameters, PersonPredictor personPredictor,
			BikePredictor bikePredictor) {
		this.parameters = parameters;
		this.bikePredictor = bikePredictor;
		this.personPredictor = personPredictor;
	}

	public PersonPredictor getPersonPredictor() {
		return personPredictor;
	}
	public BikePredictor getBikePredictor() {
		return bikePredictor;
	}

	protected double estimateConstantUtility() {
		return parameters.bike.alpha_u;
	}

	protected double estimateTravelUtility(BikeVariables variables) {
		double result = parameters.bike.betaTravelTime_u_min * variables.travelTime_min;
		// XX here, we add a penalty for slope
		// if the beta is still zero, we will use the travel time one, always print something
		if (Math.abs(parameters.bike.betaSlope_u_perGrad) > 0.0 + 1e-10) {
			logger.info("Using another beta, since the the one for slope is not set yet.");
			result += parameters.bike.betaTravelTime_u_min * variables.slope;

		} else {
			result += parameters.bike.betaSlope_u_perGrad * variables.slope;
		}


		logger.info("BikeUtilityEstimator: travelTime_min = " + variables.travelTime_min + ", slope = " + variables.slope + ", using betaTravelTime_u_min = " + parameters.bike.betaTravelTime_u_min + ", betaSlope_u_perGrad = " + parameters.bike.betaSlope_u_perGrad + ",	travel utility = " + result);


		return result;
	}

	protected double estimateAgeOver18Utility(PersonVariables variables) {
		return parameters.bike.betaAgeOver18_u_a * Math.max(0.0, variables.age_a - 18);
	}

	@Override
	public double estimateUtility(Person person, DiscreteModeChoiceTrip trip, List<? extends PlanElement> elements) {
		PersonVariables personVariables = personPredictor.predictVariables(person, trip, elements);
		BikeVariables bikeVariables = bikePredictor.predictVariables(person, trip, elements);

		double utility = 0.0;

		utility += estimateConstantUtility();
		// XX renamed from estimateTravelTimeUtility to estimateTravelUtility since we added more
		utility += estimateTravelUtility(bikeVariables);
		utility += estimateAgeOver18Utility(personVariables);

		return utility;
	}
}
