package org.eqasim.core.simulation;

// XX this is entirely ours XX TODO maybe make this cleaner
public abstract class OurGlobalParameters {
    public static double BIKE_BIAS = 0.0;
    public static double CAR_BIAS = 0.0;
    public static double PT_BIAS = 0.0;
    public static int index_to_get_bike = 0;
    public static double BIKE_MAX_VELOCITY_MS = 4.89; // Value from paper XX TODO
    // microzensus does not make a distinction between bike types, so we looked at this paper:
    // The distribution of mean trip speeds across different bicycle types is presented in Fig. 3. On average, e-bikes exhibit slightly higher mean trip speeds (18.55 km/h) compared to regular bicycles (17.62 km/h), whereas s-pedelecs reach significantly higher speeds at 23.24 km/h. 
// https://www.sciencedirect.com/science/article/pii/S295010592500021X
// 17.62 km/h = 4.89 m/s
// 18.55 km/h = 5.15 m/s

    public static boolean REMOVE_ELEVATION = false;

    public static double CAR_ADDITIONAL_COST_PER_KM = 0.0; // in CHF/km
    // https://shop.asfinag.at/de/maut-produkte/digitale-streckenmaut/1-fahrt-a-13-brenner-autobahn source for price of brenner autobahn: 12.50€ for about 24 km => 0.52 €/kmhttps://shop.asfinag.at/de/maut-produkte/digitale-streckenmaut/1-fahrt-a-13-brenner-autobahn
}
