package org.eqasim.switzerland.ch_cmdp.util.depricated;

import java.util.ArrayList;
import java.util.List;

import org.matsim.api.core.v01.Id;
import org.matsim.api.core.v01.population.Person;
import org.matsim.api.core.v01.population.Population;
import org.matsim.core.population.PopulationUtils;
import org.matsim.utils.objectattributes.attributable.Attributes;

public class GiveBikes {
        public static void main(String[] args) {
        String configPath = args.length > 0 ? args[0] : "scenarios/Zurich_10pct/zurich_10pct_population.xml";

        Population population = PopulationUtils.readPopulation(configPath);


        
        // Create a copy of the IDs before ifying the population
        // List<Id<Person>> ids = new ArrayList<>(population.getPersons().keySet());

        // Dont get all keys, but all values
        List<Person> persons = new ArrayList<>(population.getPersons().values());

        int peopleWithBikes = 0;
        int peopleSomeBikes = 0;
        int peopleNoBikes = 0;
        int mysteriousPeople = 0;

        for (Person person : persons) {

            Attributes attributes = person.getAttributes();
            
            Object bikeAvailabilityObj = attributes.getAttribute("bikeAvailability");

            // check for null
            if (bikeAvailabilityObj == null) {
                System.out.println("Someone has no bikeAvailability attribute");
                continue;
            }
            // compare to sting "FOR_ALL"
            if (bikeAvailabilityObj.equals("FOR_ALL")) {
                peopleWithBikes++;
                continue;
            } else if (bikeAvailabilityObj.equals("FOR_SOME")) {
                peopleSomeBikes++;
                attributes.putAttribute("bikeAvailability", "FOR_ALL");
                continue;
            } else if (bikeAvailabilityObj.equals("FOR_NONE")) {
                peopleNoBikes++;
                attributes.putAttribute("bikeAvailability", "FOR_ALL");
                continue;
            } else {
                mysteriousPeople++;
                System.out.println("Someone has a mysterious bikeAvailability attribute: " + bikeAvailabilityObj);
                continue;
            }

        }

        // print stats
        System.out.println("People with bikes: " + peopleWithBikes);
        System.out.println("People with some bikes: " + peopleSomeBikes);
        System.out.println("People with no bikes: " + peopleNoBikes);
        System.out.println("Mysterious people: " + mysteriousPeople);

        String outputPath = "scenarios/Zurich_10pct/zurich_10pct_population_many_bikes.xml";
        PopulationUtils.writePopulation(population, outputPath);
    }
}
