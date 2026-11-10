from mobility_stats.rides import average_duration, busiest_start_station, count_by_rider_type


def build_summary(rides):
    """Build a compact dictionary with headline statistics."""
    ride_summary = {
        "ride_count": len(rides),
        "average_duration": average_duration(rides),
        "rider_types": count_by_rider_type(rides),
    }
    if rides:
        ride_summary["busiest_start_station"] = busiest_start_station(rides)
    else:
        ride_summary["busiest_start_station"] = None
    return ride_summary


def format_summary(ride_summary):
    """Create a human-readable text summary."""
    title = "Mobility summary"
    line1 = f"Rides: {ride_summary['ride_count']}"
    line2 = f"Average duration: {ride_summary['average_duration']:.1f} min"
    line3 = f"Busiest start: {ride_summary['busiest_start_station']}"
    return title + "\n" + line1 + "\n" + line2 + "\n" + line3
