package org.eqasim.switzerland.ch_cmdp;

import org.matsim.contribs.discrete_mode_choice.modules.AbstractDiscreteModeChoiceExtension;
import org.matsim.contribs.discrete_mode_choice.modules.config.DiscreteModeChoiceConfigGroup;
import org.matsim.contribs.discrete_mode_choice.modules.config.ModeAvailabilityConfigGroup;

import com.google.inject.Provides;

public class SwissModeAvailabilityModule extends AbstractDiscreteModeChoiceExtension {

    public static final String BIKE = "Bike";

    @Override
    public void installExtension() {
        bindModeAvailability(BIKE).to(BikeModeAvailability.class);
    }

    @Provides
    public BikeModeAvailability provideBikeModeAvailability(DiscreteModeChoiceConfigGroup dmcConfig) {
        ModeAvailabilityConfigGroup config = dmcConfig.getDefaultModeAvailabilityConfig();
        return new BikeModeAvailability(config.getAvailableModes());
    }
}
