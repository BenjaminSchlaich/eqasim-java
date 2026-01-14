package org.eqasim.core.simulation;

// XX this is entirely ours XX TODO maybe make this cleaner
public abstract class OurGlobalParameters {
    public static double BIKE_BIAS = 0.0;
    public static double CAR_BIAS = 0.0;
    public static double PT_BIAS = 0.0;
    public static int index_to_get_bike = 0;
    public static double BIKE_MAX_VELOCITY_MS = 6.3; // Value from strava. Could be made more linked to microzensus XX TODO

    public static boolean REMOVE_ELEVATION = false;
}
