"""
Welcome to your first Halite-II bot!

This bot's name is Settler. It's purpose is simple (don't expect it to win complex games :) ):
1. Initialize game
2. If a ship is not docked and there are unowned planets
2.a. Try to Dock in the planet if close enough
2.b If not, go towards the planet

Note: Please do not place print statements here as they are used to communicate with the Halite engine. If you need
to log anything use the logging module.
"""
# Let's start by importing the Halite Starter Kit so we can interface with the Halite engine
import hlt
# Then let's import the logging module so we can print out information
import logging
from hlt.entity import Position


# GAME START
# Here we define the bot's name as Settler and initialize the game, including communication with the Halite engine.
game = hlt.Game("Chris")
# Then we print our start message to the logs
logging.info("Starting my Settler bot!")

while True:
    # TURN START
    # Update the map for the new turn and get the latest version
    game_map = game.update_map()
    max_corrections = 135
    angular_steps = int(5 + len(game_map.get_me().all_ships())/20)
    if len(game_map.get_me().all_ships()) < 50:
        ignore_ships = False
    else:
        ignore_ships = True

    # Here we define the set of commands to be sent to the Halite engine at the end of the turn
    command_queue = []
    # For every ship that I control
    for ship in game_map.get_me().all_ships():
        # If the ship is docked
        if ship.docking_status != ship.DockingStatus.UNDOCKED:
            # Skip this ship
            continue

        entities_by_distance = game_map.nearby_entities_by_distance(ship)
        nearest_planet = None
        for distance in sorted(entities_by_distance):
            logging.info("continued: " + str(ship.id))
            nearest_planet = next((nearest_entity for nearest_entity in entities_by_distance[distance] if
                                   isinstance(nearest_entity, hlt.entity.Planet)), None)
            if nearest_planet:
                planet = nearest_planet
                logging.info("Ship: " + str(ship.id) + "Planet" + str(planet.id))

        # For each planet in the game (only non-destroyed planets are included)
        #for planet in game_map.all_planets():
            # If the planet is owned
                if planet.is_owned():
                    if planet.owner == game_map.get_me():
                        logging.info("Length of planet.all_docked_ships(): " + str(len(planet.all_docked_ships())) + "tot spots" + str(planet.num_docking_spots))
                        if len(planet.all_docked_ships()) < planet.num_docking_spots:
                            if ship.can_dock(planet):
                                navigate_command = ship.dock(planet)

                            else:
                                navigate_command = ship.navigate(
                                    ship.closest_point_to(planet),
                                    game_map,
                                    speed=int(hlt.constants.MAX_SPEED),
                                    ignore_ships=ignore_ships,
                                    max_corrections= max_corrections,
                                    angular_step= angular_steps)
                            if navigate_command:
                                command_queue.append(navigate_command)
                                break
                        else:
                            logging.info("continuing: " + str(ship.id))
                            continue
                    else:
                        logging.info("attack")
                        docked_ships= planet.all_docked_ships()
                        ship1 = docked_ships[0]
                        navigate_command = ship.navigate(
                            ship.closest_point_to(ship1),
                            game_map,
                            speed=int(hlt.constants.MAX_SPEED),
                            ignore_ships=ignore_ships,
                            max_corrections = max_corrections,
                            angular_step = angular_steps)

                        if navigate_command:
                            command_queue.append(navigate_command)
                            break

                # If we can dock, let's (try to) dock. If two ships try to dock at once, neither will be able to.
                if ship.can_dock(planet):
                    # We add the command by appending it to the command_queue
                    command_queue.append(ship.dock(planet))
                else:
                    # If we can't dock, we move towards the closest empty point near this planet (by using closest_point_to)
                    # with constant speed. Don't worry about pathfinding for now, as the command will do it for you.
                    # We run this navigate command each turn until we arrive to get the latest move.
                    # Here we move at half our maximum speed to better control the ships
                    # In order to execute faster we also choose to ignore ship collision calculations during navigation.
                    # This will mean that you have a higher probability of crashing into ships, but it also means you will
                    # make move decisions much quicker. As your skill progresses and your moves turn more optimal you may
                    # wish to turn that option off.
                    navigate_command = ship.navigate(
                        ship.closest_point_to(planet),
                        game_map,
                        speed=int(hlt.constants.MAX_SPEED),
                        ignore_ships=ignore_ships,
                        max_corrections = max_corrections,
                        angular_step = angular_steps)

                    # If the move is possible, add it to the command_queue (if there are too many obstacles on the way
                    # or we are trapped (or we reached our destination!), navigate_command will return null;
                    # don't fret though, we can run the command again the next turn)
                    if navigate_command:
                        command_queue.append(navigate_command)
                break

    # Send our set of commands to the Halite engine for this turn
    game.send_command_queue(command_queue)
    # TURN END
# GAME END
