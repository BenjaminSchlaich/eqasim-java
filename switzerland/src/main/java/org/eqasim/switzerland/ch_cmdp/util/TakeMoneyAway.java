package org.eqasim.switzerland.ch_cmdp.util;

import java.util.ArrayList;
import java.util.List;

import org.matsim.api.core.v01.Id;
import org.matsim.api.core.v01.population.Person;
import org.matsim.api.core.v01.population.Population;
import org.matsim.core.population.PopulationUtils;
import org.matsim.utils.objectattributes.attributable.Attributes;

public class TakeMoneyAway {
        public static void main(String[] args) {
        String configPath = args.length > 0 ? args[0] : "scenarios/Zurich_10pct/zurich_10pct_population.xml";

        Population population = PopulationUtils.readPopulation(configPath);


        
        // Create a copy of the IDs before modifying the population
        // List<Id<Person>> ids = new ArrayList<>(population.getPersons().keySet());

        // Dont get all keys, but all values
        List<Person> persons = new ArrayList<>(population.getPersons().values());

        for (Person person : persons) {

            Attributes attributes = person.getAttributes();
            
            Object incomePerCapitaObj = attributes.getAttribute("incomePerCapita");

            // check for null
            if (incomePerCapitaObj == null) {
                System.out.println("Someone is poor");
                continue;
            }

            double incomePerCapita = (double) incomePerCapitaObj;

            
            // debug print
            System.out.println("Income per capita before: " + incomePerCapita);
            attributes.putAttribute("incomePerCapita", incomePerCapita * 0.01);
        }

        String outputPath = "scenarios/Zurich_10pct/zurich_10pct_population_poor.xml";
        PopulationUtils.writePopulation(population, outputPath);
    }
}
