import xml.etree.ElementTree as ET

def total_car_kilometers(xml_path: str) -> float:
    """
    Parse a MATSim experienced_plans.xml file and return the total
    distance traveled by car in kilometers.
    """

    total_distance_m = 0.0

    # Stream parsing to handle large files efficiently
    for event, elem in ET.iterparse(xml_path, events=("end",)):
        if elem.tag == "leg":
            routing_mode = None

            # Find routingMode attribute
            attributes = elem.find("attributes")
            if attributes is not None:
                for attr in attributes.findall("attribute"):
                    if attr.get("name") == "routingMode":
                        routing_mode = attr.text
                        break

            # Only count legs routed by car
            if routing_mode == "car":
                route = elem.find("route")
                if route is not None:
                    distance_str = route.get("distance")
                    if distance_str is not None:
                        total_distance_m += float(distance_str)

            # Clear element to free memory
            elem.clear()

    # Convert meters to kilometers
    return total_distance_m / 1000.0


if __name__ == "__main__":
    xml_file = "data/experienced_plans.xml"
    total_km = total_car_kilometers(xml_file)
    print(f"Total distance traveled by car: {total_km:.2f} km")
