"""Solution output routines"""
from six.moves import xrange
from datetime import datetime, timedelta

# copied from Google v7.0 example
def print_solution(demand,
                   dist_callback,
                   vehicles,
                   manager,
                   routing,
                   assignment):  # pylint:disable=too-many-locals
    """Prints assignment on console"""
    print('Objective: {}'.format(assignment.ObjectiveValue()))
    num_pickup_nodes = demand.get_number_nodes() / 2
    print('Breaks:')
    intervals = assignment.IntervalVarContainer()
    for i in xrange(intervals.Size()):
        brk = intervals.Element(i)
        if brk.PerformedValue() == 1:
            print('{}: Start({}) Duration({})'.format(
                brk.Var().Name(),
                brk.StartValue(),
                brk.DurationValue()))
        else:
            print('{}: Unperformed'.format(brk.Var().Name()))

    total_distance = 0
    total_load_served = 0
    total_time = 0
    capacity_dimension = routing.GetDimensionOrDie('Capacity')
    time_dimension = routing.GetDimensionOrDie('Time')
    print('Routes:')
    for vehicle in vehicles.vehicles:
        vehicle_id = vehicle.index
        index = routing.Start(vehicle_id)
        plan_output  ='Route for vehicle {}:\n'.format(vehicle_id)
        distance = 0
        this_distance = 0
        this_time = 0
        pickups = 0
        while not routing.IsEnd(index):
            # load_var = capacity_dimension.CumulVar(index)

            time_var = time_dimension.CumulVar(index)
            load_var  = capacity_dimension.CumulVar(index)
            slack_var = time_dimension.SlackVar(index)

            node = manager.IndexToNode(index)
            mapnode = demand.get_map_node(node)
            load = assignment.Value(load_var)
            min_time =  timedelta(minutes=assignment.Min(time_var))
            max_time =  timedelta(minutes=assignment.Max(time_var))
            slack_var_min = 0
            slack_var_max = 0
            if (node < num_pickup_nodes and node > 0):
                pickups += 1
            if node < num_pickup_nodes:
                slack_var_min = assignment.Min(slack_var)
                slack_var_max = assignment.Max(slack_var)

            plan_output += 'node {0}, mapnode {1}, Load {2},  Time({3},{4}) Slack({5},{6}) Link time({7}) Link distance({8} mi)\n ->'.format(
                node,
                mapnode,
                load,
                min_time,
                max_time,
                slack_var_min,
                slack_var_max,
                timedelta(minutes=this_time),
                this_distance
            )
            previous_index = index
            index = assignment.Value(routing.NextVar(index))

            this_time = routing.GetArcCostForVehicle(previous_index, index,
                                                     vehicle_id)
            this_distance = dist_callback(previous_index,index)
            distance += this_distance
        load_var = capacity_dimension.CumulVar(index)
        time_var = time_dimension.CumulVar(index)
        slack_var = time_dimension.SlackVar(index)
        plan_output += ' {0} Load({1})  Time({2},{3})  Link time({4}) Link distance({5} mi)\n'.format(
            manager.IndexToNode(index),
            assignment.Value(load_var),
            timedelta(minutes=assignment.Min(time_var)),
            timedelta(minutes=assignment.Max(time_var)),
            timedelta(minutes=this_time),
            this_distance
        )
        plan_output += 'Distance of the route: {0} miles\n'.format(distance)
        plan_output += 'Loads served by route: {}\n'.format(
            pickups)
        plan_output += 'Time of the route: {}\n'.format(
            timedelta(minutes=assignment.Value(time_var)))
        print(plan_output)
        total_distance += distance
        total_load_served += pickups
        total_time += assignment.Value(time_var)
    print('Total Distance of all routes: {0} miles'.format(total_distance))
    print('Total Loads picked up by all routes: {}'.format(total_load_served))
    print('Total Time of all routes: {0}'.format(timedelta(minutes=total_time)))