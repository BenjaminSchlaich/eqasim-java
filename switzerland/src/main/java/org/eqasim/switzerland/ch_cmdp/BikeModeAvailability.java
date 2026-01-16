package org.eqasim.switzerland.ch_cmdp;

import java.util.Collection;
import java.util.List;
import java.util.stream.Collectors;

import org.matsim.api.core.v01.TransportMode;
import org.matsim.api.core.v01.population.Person;
import org.matsim.contribs.discrete_mode_choice.model.DiscreteModeChoiceTrip;
import org.matsim.contribs.discrete_mode_choice.model.mode_availability.DefaultModeAvailability;

public class BikeModeAvailability extends DefaultModeAvailability {

    public BikeModeAvailability(Collection<String> modes) {
        super(modes);
    }

    @Override
    public Collection<String> getAvailableModes(Person person, List<DiscreteModeChoiceTrip> trips) {
        Object bikeAttr = person.getAttributes().getAttribute("bikeAvailability");

        boolean hasBike = "FOR_ALL".equals(bikeAttr);

        if (!hasBike) {
            return super.getAvailableModes(person, trips).stream()
                .filter(m -> !TransportMode.bike.equals(m))
                .collect(Collectors.toSet());
        }

        return super.getAvailableModes(person, trips);
    }
}
