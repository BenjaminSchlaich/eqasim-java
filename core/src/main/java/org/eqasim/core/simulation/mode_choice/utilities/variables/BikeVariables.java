package org.eqasim.core.simulation.mode_choice.utilities.variables;

public class BikeVariables implements BaseVariables {
	final public double travelTime_min;
	// XX added slope as a variable to take into account
	final public double slope;

	public BikeVariables(double travelTime_min, double slope) {
		this.travelTime_min = travelTime_min;
		this.slope = slope;
	}
}
