package org.eqasim.switzerland.ch_cmdp.our_configurations;

import java.util.ArrayList;
import java.util.List;

import org.apache.logging.log4j.Logger;
import org.apache.logging.log4j.LogManager;
import org.matsim.api.core.v01.population.Person;
import org.matsim.api.core.v01.population.Population;
import org.matsim.utils.objectattributes.attributable.Attributes;

// XX this is entirely ours
public class PopulationConfigurator {
	private final static Logger logger = LogManager.getLogger(PopulationConfigurator.class);

    public void applyWealthFactor(Population population, double wealthFactor) {

        List<Person> persons = new ArrayList<>(population.getPersons().values());

        for (Person person : persons) {
            Attributes attributes = person.getAttributes();
            
            Object incomePerCapitaObj = attributes.getAttribute("incomePerCapita");

            // check for null
            if (incomePerCapitaObj == null) {
                logger.warn("Person {} has no incomePerCapita attribute", person.getId());
                continue;
            }

            double incomePerCapita = (double) incomePerCapitaObj;

            // debug print
            logger.info("Income per capita before for person {}: {}", person.getId(), incomePerCapita);
            attributes.putAttribute("incomePerCapita", incomePerCapita * wealthFactor);
        }
    }



    public void giveBikes(Population population, double chanceOfGettingBikeWhenNotForAll) {
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
                logger.warn("Person {} has no bikeAvailability attribute", person.getId());
                continue;
            }
            // compare to sting "FOR_ALL"
            if (bikeAvailabilityObj.equals("FOR_ALL")) {
                peopleWithBikes++;
                continue;
            } else if (bikeAvailabilityObj.equals("FOR_SOME")) {
                peopleSomeBikes++;
                if (Math.random() < chanceOfGettingBikeWhenNotForAll) {
                    attributes.putAttribute("bikeAvailability", "FOR_ALL");
                }

                continue;
            } else if (bikeAvailabilityObj.equals("FOR_NONE")) {
                peopleNoBikes++;
                // give bike with certain chance
                if (Math.random() < chanceOfGettingBikeWhenNotForAll) {
                    attributes.putAttribute("bikeAvailability", "FOR_ALL");
                }
                continue;
            } else {
                mysteriousPeople++;
                logger.warn("Person {} has a mysterious bikeAvailability attribute: {}", person.getId(), bikeAvailabilityObj);
                continue;
            }

        }

        // print stats
        logger.info("People with bikes: {}", peopleWithBikes);
        logger.info("People with some bikes: {}", peopleSomeBikes);
        logger.info("People with no bikes: {}", peopleNoBikes);
        logger.info("Mysterious people: {}", mysteriousPeople);
    }





    public void redistributeBikes(Population population) {
        // First find out how many people there are in total, and how many have bikes, and how many have sometimes and how many have none
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
                logger.warn("Person {} has no bikeAvailability attribute", person.getId());
                continue;
            }
            // compare to sting "FOR_ALL"
            if (bikeAvailabilityObj.equals("FOR_ALL")) {
                peopleWithBikes++;
                continue;
            } else if (bikeAvailabilityObj.equals("FOR_SOME")) {
                peopleSomeBikes++;
                continue;
            } else if (bikeAvailabilityObj.equals("FOR_NONE")) {
                peopleNoBikes++;
                continue;
            } else {
                mysteriousPeople++;
                logger.warn("Person {} has a mysterious bikeAvailability attribute: {}", person.getId(), bikeAvailabilityObj);
                continue;
            }

        }

        // print stats
        logger.info("People with bikes: {}", peopleWithBikes);
        logger.info("People with some bikes: {}", peopleSomeBikes);
        logger.info("People with no bikes: {}", peopleNoBikes);
        logger.info("Mysterious people: {}", mysteriousPeople);

        // Now, we redistribute bikes randomly. We do this, by first shuffling the list of persons, and then assigning bikes to the first N persons, where N is the number of people who had bikes before.
        java.util.Collections.shuffle(persons);

        for (int i = 0; i < persons.size(); i++) {
            Person person = persons.get(i);
            Attributes attributes = person.getAttributes();
            if (i < peopleWithBikes) {
                attributes.putAttribute("bikeAvailability", "FOR_ALL");
            } else if (i < peopleWithBikes + peopleSomeBikes) {
                attributes.putAttribute("bikeAvailability", "FOR_SOME");
            } else {
                attributes.putAttribute("bikeAvailability", "FOR_NONE");
            }
        }

        logger.info("Redistributed bikes among the population.");
    }


}

