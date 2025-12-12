package org.eqasim.switzerland.ch_cmdp.our_configurations;

import java.util.ArrayList;
import java.util.List;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.matsim.api.core.v01.network.Link;
import org.matsim.api.core.v01.network.Network;
import org.matsim.core.network.NetworkUtils;

// XX this is entirely ours
public class NetworkConfigurator {
	private final static Logger logger = LogManager.getLogger(NetworkConfigurator.class);


    public void applySpeedFactor(Network network, double speedFactor) {
        List<Link> links = new ArrayList<>(network.getLinks().values());
        for (Link link : links) {
            double freespeed = link.getFreespeed();
            link.setFreespeed(freespeed * speedFactor);
        }
        logger.info("Applied speed factor of {} to network", speedFactor);
    }

    public void applySpeedFactor(String configPath, String outputPath, double speedFactor) {
        Network network = NetworkUtils.readNetwork(configPath);
        applySpeedFactor(network, speedFactor);
        NetworkUtils.writeNetwork(network, outputPath);
    }

}
