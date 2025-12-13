package org.eqasim.switzerland.ch_cmdp.util.depricated;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Random;
import java.util.stream.Collectors;
import java.util.stream.Stream;

import javax.imageio.ImageIO;

import org.matsim.api.core.v01.Coord;
import org.matsim.api.core.v01.Id;
import org.matsim.api.core.v01.Scenario;
import org.matsim.api.core.v01.network.Network;
import org.matsim.api.core.v01.network.NetworkWriter;
import org.matsim.api.core.v01.population.Person;
import org.matsim.api.core.v01.population.Population;
import org.matsim.core.config.Config;
import org.matsim.core.config.ConfigUtils;
import org.matsim.core.network.NetworkUtils;
import org.matsim.core.population.PopulationUtils;
import org.matsim.core.scenario.ScenarioUtils;
import org.matsim.core.utils.geometry.CoordUtils;

import java.awt.Color;
import java.awt.Graphics2D;
import java.awt.image.BufferedImage;

// TODO: this code should work, but I could not test it, since I do not have the ram on my laptop

public class DoublePopulation {

    public static void main(String[] args) {
        String configPath = args.length > 0 ? args[0] : "scenarios/Zurich_10pct/zurich_10pct_population.xml";

        Population population = PopulationUtils.readPopulation(configPath);

        double sampleFraction = 0.01;

        // Create a copy of the IDs before modifying the population
        List<Id<Person>> ids = new ArrayList<>(population.getPersons().keySet());

        for (Id<Person> personId : ids) {
            if (Math.random() > sampleFraction) {
                population.removePerson(personId);
            }
        }

        String outputPath = "scenarios/Zurich_10pct/zurich_10pct_population_tiny.xml";
        PopulationUtils.writePopulation(population, outputPath);
    }
}
