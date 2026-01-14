package org.eqasim.switzerland.ch_cmdp;

import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;

public class ExtractCalibrationResults {
    // A main function that loads a particular .csv file and prints the values from ZÃ¼rich 
    public static void main(String[] args) {
        String csvFilePath = "simulation_output_calibration/ITERS/it.120/120.alphas.csv";

        double alpha_car = 0.0;
        double alpha_walk = 0.0;
        double alpha_bike = 0.0;
        double alpha_car_passenger = 0.0;
        double alpha_pt = 0.0;

        Path path = java.nio.file.Paths.get(csvFilePath);
        try {
            List<String> lines = java.nio.file.Files.readAllLines(path);
            for (String line : lines) {
                if (line.startsWith("ZÃ¼rich,")) {
                    String[] values = line.split(",");
                    alpha_car = Double.parseDouble(values[1]);
                    alpha_walk = Double.parseDouble(values[2]);
                    alpha_bike = Double.parseDouble(values[3]);
                    alpha_car_passenger = Double.parseDouble(values[4]);
                    alpha_pt = Double.parseDouble(values[5]);

                    System.out.println("Calibration results for ZÃ¼rich:");
                    System.out.println("Alpha Car: " + alpha_car);
                    System.out.println("Alpha Walk: " + alpha_walk);
                    System.out.println("Alpha Bike: " + alpha_bike);
                    System.out.println("Alpha Car Passenger: " + alpha_car_passenger);
                    System.out.println("Alpha PT: " + alpha_pt);
                }
            }
        } catch (java.io.IOException e) {
            e.printStackTrace();
        }


        // now load the file "estimated_dmc_parameters.yml" and replace the alpha values with the ones extracted above
        String ymlFilePath = "estimated_dmc_parameters.yml";
        try {
            List<String> lines = java.nio.file.Files.readAllLines(java.nio.file.Paths.get(ymlFilePath));
            for (int i = 0; i < lines.size(); i++) {
                String line = lines.get(i);
                if (line.startsWith("car.alpha_u:")) {
                    lines.set(i, "car.alpha_u: " + alpha_car);

                } else if (line.startsWith("walk.alpha_u:")) {
                    lines.set(i, "walk.alpha_u: " + alpha_walk);

                } else if (line.startsWith("bike.alpha_u:")) {
                    lines.set(i, "bike.alpha_u: " + alpha_bike);

                } else if (line.startsWith("cp.alpha_u:")) {
                    lines.set(i, "cp.alpha_u: " + alpha_car_passenger);

                } else if (line.startsWith("pt.alpha_u:")) {    
                    lines.set(i, "pt.alpha_u: " + alpha_pt);
                }

            }
            // overwrite the original file
            Files.write(java.nio.file.Paths.get(ymlFilePath), lines);
            System.out.println("Updated " + ymlFilePath + " with new alpha values.");


        } catch (java.io.IOException e) {
            e.printStackTrace();
        }

    }
    
}