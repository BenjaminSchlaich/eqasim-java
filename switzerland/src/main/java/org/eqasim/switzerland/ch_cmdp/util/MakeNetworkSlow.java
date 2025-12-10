package org.eqasim.switzerland.ch_cmdp.util;

import java.util.ArrayList;
import java.util.List;

import org.matsim.api.core.v01.Id;
import org.matsim.api.core.v01.network.Link;
import org.matsim.api.core.v01.network.Network;
import org.matsim.api.core.v01.population.Person;
import org.matsim.api.core.v01.population.Population;
import org.matsim.core.network.NetworkUtils;
import org.matsim.core.population.PopulationUtils;
import org.matsim.utils.objectattributes.attributable.Attributes;

public class MakeNetworkSlow {
        public static void main(String[] args) {
        String configPath = args.length > 0 ? args[0] : "scenarios/Zurich_10pct/zurich_10pct_network.xml";

        Network network = NetworkUtils.readNetwork(configPath);

        
        // Create a copy of the IDs before modifying the population
        // List<Id<Person>> ids = new ArrayList<>(population.getPersons().keySet());

        // Dont get all keys, but all values
        List<Link> links = new ArrayList<>(network.getLinks().values());

        for (Link link : links) {

            double freespeed = link.getFreespeed();
            link.setFreespeed(freespeed * 0.1);
        }

        String outputPath = "scenarios/Zurich_10pct/zurich_10pct_network_slow.xml";
        NetworkUtils.writeNetwork(network, outputPath);
    }
}
