package org.eqasim.switzerland.ch_cmdp.util;

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

import org.apache.commons.math3.analysis.function.Add;
import org.matsim.api.core.v01.Coord;
import org.matsim.api.core.v01.Scenario;
import org.matsim.api.core.v01.network.Network;
import org.matsim.api.core.v01.network.NetworkWriter;
import org.matsim.core.config.Config;
import org.matsim.core.config.ConfigUtils;

import org.matsim.core.scenario.ScenarioUtils;
import org.matsim.core.utils.geometry.CoordUtils;

import java.awt.Color;
import java.awt.Graphics2D;
import java.awt.image.BufferedImage;

// TODO: this code should work, but I could not test it, since I do not have the ram on my laptop

public class AddZCoordsToNetwork {


    public static List<Coord> getHeightPoints() {
        String height_path = "data/heights";

        List<Path> xyzPaths;

        try (Stream<Path> stream = Files.walk(Path.of(height_path))) {
            xyzPaths = stream
                    .filter(Files::isRegularFile)
                    .filter(p -> p.toString().endsWith(".xyz"))
                    .collect(Collectors.toList());
        } catch (Exception e) {
            throw new RuntimeException("Error reading .xyz files", e);
        }

        System.out.println("Found " + xyzPaths.size() + " .xyz files.");

        List<Coord> points = new ArrayList<>();

        Random random = new Random(42);


        // int j = 0;
        // int j_upperLimit = 10000;

        for (Path xyzPath : xyzPaths) {
            System.out.println("Reading file: " + xyzPath);


            try (BufferedReader br = new BufferedReader(new FileReader(xyzPath.toFile()))) {
    
                // Skip the first line (Python used header=1)
                br.readLine();
    
                String line;
            
                while ((line = br.readLine()) != null) {
                    // j++;
                    // if (j > j_upperLimit) {
                    //     break;
                    // }

                    String[] parts = line.trim().split("\\s+");
                    if (parts.length < 3) continue;
    
                    double x = Double.parseDouble(parts[0]);
                    double y = Double.parseDouble(parts[1]);
                    double z = Double.parseDouble(parts[2]);
    
                    points.add(new Coord(x, y, z));
                }
            } catch (Exception e) {
                System.err.println("Error reading file: " + xyzPath);
                e.printStackTrace();
            }
            // j = 0;
        }

        System.out.println("Loaded " + points.size() + " points from .xyz files.");
        return points;
    }


    public static List<Coord> getHeightGrid() {
        String height_path = "data/heights";

        List<Path> xyzPaths;

        try (Stream<Path> stream = Files.walk(Path.of(height_path))) {
            xyzPaths = stream
                    .filter(Files::isRegularFile)
                    .filter(p -> p.toString().endsWith(".xyz"))
                    .collect(Collectors.toList());
        } catch (Exception e) {
            throw new RuntimeException("Error reading .xyz files", e);
        }
        // Sort the paths alphabetically to ensure consistent order
        xyzPaths.sort((p1, p2) -> p1.toString().compareTo(p2.toString()));


        System.out.println("Found " + xyzPaths.size() + " .xyz files.");
// getHeightPoints


        List<Coord> points = new ArrayList<>();

        Random random = new Random(42);


        // int j = 0;
        // int j_upperLimit = 10000;

        for (Path xyzPath : xyzPaths) {
            System.out.println("Reading file: " + xyzPath);


            try (BufferedReader br = new BufferedReader(new FileReader(xyzPath.toFile()))) {
    
                // Skip the first line (Python used header=1)
                br.readLine();
    
                String line;
            
                while ((line = br.readLine()) != null) {
                    // j++;
                    // if (j > j_upperLimit) {
                    //     break;
                    // }

                    String[] parts = line.trim().split("\\s+");
                    if (parts.length < 3) continue;
    
                    double x = Double.parseDouble(parts[0]);
                    double y = Double.parseDouble(parts[1]);
                    double z = Double.parseDouble(parts[2]);
    
                    points.add(new Coord(x, y, z));
                }
            } catch (Exception e) {
                System.err.println("Error reading file: " + xyzPath);
                e.printStackTrace();
            }
            // j = 0;
        }

        System.out.println("Loaded " + points.size() + " points from .xyz files.");
        return points;
    }



    public static void createImage(List<Coord> sampledPoints) {
        int width = 800;
        int height = 600;

        BufferedImage image = new BufferedImage(width, height, BufferedImage.TYPE_INT_ARGB);
        Graphics2D g = image.createGraphics();

        g.setColor(Color.white);
        g.fillRect(0, 0, width, height);

        // Determine bounds
        double minX = sampledPoints.stream().mapToDouble(p -> p.getX()).min().orElse(0);
        double maxX = sampledPoints.stream().mapToDouble(p -> p.getX()).max().orElse(1);
        double minY = sampledPoints.stream().mapToDouble(p -> p.getY()).min().orElse(0);
        double maxY = sampledPoints.stream().mapToDouble(p -> p.getY()).max().orElse(1);
        double minZ = sampledPoints.stream().mapToDouble(p -> p.getZ()).min().orElse(0);
        double maxZ = sampledPoints.stream().mapToDouble(p -> p.getZ()).max().orElse(1);

        for (Coord p : sampledPoints) {

            // Normalize x,y to image coordinates
            int px = (int) ((p.getX() - minX) / (maxX - minX) * (width - 1));
            int py = (int) ((p.getY() - minY) / (maxY - minY) * (height - 1));

            // Flip Y axis for image space (optional)
            py = height - py;

            // Map z to color (simple grayscale)
            float intensity = (float) ((p.getZ() - minZ) / (maxZ - minZ));
            Color color = new Color(intensity, 0, 1 - intensity); // Purple gradient

            g.setColor(color);
            g.fillOval(px - 3, py - 3, 6, 6); // draw a 6px dot
        }

        g.dispose();

        try {
            ImageIO.write(image, "png", new File("output.png"));
            System.out.println("Saved image: output.png");
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
    // (((310000000 * 3 * 16) / 8 ) / 1024) / 1024

    public static void main(String[] args) {

        // Get the first command line argument as the config path
        String configPath = args.length > 0 ? args[0] : "scenarios/Zurich_10pct/zurich_10pct_config.xml";
        
        // get the second command line argument as the output network file
        String outputNetworkFile = args.length > 1 ? args[1] : "scenarios/Zurich_10pct/zurich_10pct_network_with_z.xml";

        List<Coord> points = AddZCoordsToNetwork.getHeightPoints();

        // Cast the points to integers
        List<Coord> intPoints = points.stream()
                .map(p -> new Coord((int) p.getX(), (int) p.getY(), p.getZ()))
                .collect(Collectors.toList());


        // Now identify the minimum and maximum X and Y coordinates from the points, to cast to a grid
        // int minX = points.stream().mapToInt(p -> p.getX()).max().orElse(0);




        // int maxX = points.stream().mapToDouble(p -> p.getX()).max().orElse(1);

        // double minY = points.stream().mapToDouble(p -> p.getY()).min().orElse(0);
        // double maxY = points.stream().mapToDouble(p -> p.getY()).max().orElse(1);





        
        // String configPath = "scenarios/Zurich_10pct/zurich_10pct_config.xml";
        // String outputNetworkFile = "scenarios/Zurich_10pct/zurich_10pct_network_with_z.xml";



        Config config = ConfigUtils.loadConfig(configPath);
        Scenario scenario = ScenarioUtils.loadScenario(config);

        Network network = scenario.getNetwork();


        // int l = 0;
        // int l_upperLimit = 10000;

        List<Coord> sampledPoints = new ArrayList<>();
        int progress = 0;

        for (var node : network.getNodes().values()) {
            if (progress % 10000 == 0) {
                System.out.println("Processing node " + progress + " / " + network.getNodes().size());
            }
            // if (l >= l_upperLimit) {
            //     break;
            // }
            // l++;
        
            Coord location = node.getCoord();
            double minDistance = Double.MAX_VALUE;
            Coord nearestPoint = null;
            for (Coord point : points) {
                double distance = CoordUtils.calcEuclideanDistance(location, point);
                if (distance < minDistance) {
                    minDistance = distance;
                    nearestPoint = point;
                }
            }
            double z = nearestPoint != null ? nearestPoint.getZ() : -1; // Use nearest point's Z coordinate if available
            Coord newCoord = new Coord(location.getX(), location.getY(), z);
            node.setCoord(newCoord);
            sampledPoints.add(newCoord);
            // node.getAttributes().putAttribute("z", z);
        }

        new NetworkWriter(network).write(outputNetworkFile);


        AddZCoordsToNetwork.createImage(sampledPoints);


    }
}










        

        // CommandLine cmd = new CommandLine.Builder(args) //
        //         .requireOptions("config-path") //
        //         .allowPrefixes("mode-parameter", "cost-parameter", "preventwaitingtoentertraffic") //
        //         .build();

        // SwitzerlandConfigurator configurator = new SwitzerlandConfigurator(cmd);

        // Config config = ConfigUtils.loadConfig(cmd.getOptionStrict("config-path"));
        
        // configurator.updateConfig(config);
        // cmd.applyConfiguration(config);


        // if (cmd.hasOption("preventwaitingtoentertraffic")) {
        //     if (cmd.getOption("preventwaitingtoentertraffic").get().equals("y")) {
        //         ((QSimConfigGroup) config.getModules().get(QSimConfigGroup.GROUP_NAME))
        //                 .setPcuThresholdForFlowCapacityEasing(1.0);
        //     }
        // }



        // // VDF: Disable queue logic
        // config.qsim().setFlowCapFactor(1e9);

        // // maybe we do not want to disable storage capacity logic
        // // as we might want to have some back propagation delays
        // config.qsim().setStorageCapFactor(1e9);

        // // VDF: Optional
        // VDFConfigGroup.getOrCreate(config).setWriteInterval(10);
        // VDFConfigGroup.getOrCreate(config).setWriteFlowInterval(10);

        // // VDF Engine: Decide whether to genertae link events or not
        // VDFEngineConfigGroup.getOrCreate(config).setGenerateNetworkEvents(false);

        // // VDF Engine: Remove car from main modes
        // Set<String> mainModes = new HashSet<>(config.qsim().getMainModes());
        // mainModes.remove("car");
        // config.qsim().setMainModes(mainModes);

        // Scenario scenario = ScenarioUtils.createScenario(config);
        // configurator.configureScenario(scenario);
        // ScenarioUtils.loadScenario(scenario);
        // configurator.adjustScenario(scenario);

        // Controler controller = new Controler(scenario);
        // configurator.configureController(controller);
        // controller.run();


        

    
        // Population population = scenario.getPopulation();

        // //Read the population file of interest into the population container
        // PopulationReader popReader = new PopulationReader(scenario);
        // popReader.readFile(args[0]);
       


        // //To get the information we need, first have to go through all the persons in the population file and
        // for (Person person: population.getPersons().values() ){

        //     //Initialize the variables we need

        //     String activity_type = "";
        //     double x = 0.0;
        //     double y = 0.0;

        //     //Then we need to go through the plans to get the activities for each person.
        //     // First you want the selected plan of the person, if it is an output file we are reading
        //     //Then to access the individual contents of the plans, these are the plan elements,
        //     // the plan has two instances - activity and leg

        //     for (PlanElement element: person.getSelectedPlan().getPlanElements()){
        //         //check for the instance we need - activity
        //         if(element instanceof Activity) {
        //             Activity activity = (Activity) element;
        //             activity_type = activity.getType();
        //             x = activity.getCoord().getX();
        //             y = activity.getCoord().getY();

        //             //Write out activities for each person
        //             writer.write(person.getId().toString() + ";"
        //                     + person.getAttributes().getAttribute("age") + ";"
        //                     + person.getAttributes().getAttribute("sex") + ";"
        //                     + activity_type + ";"
        //                     + x + ";"
        //                     + y + "\n"
        //             );

        //         }

        //     }



        // }

        // //we have to close the writer
        // writer.flush();
        // writer.close();