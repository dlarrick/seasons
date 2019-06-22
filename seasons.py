# Seasons.py -- Hass helper python_script to turn a Climate entity into a smart thermostat, with
# support for multiple thermostats each having their own schedule.
#
# INPUTS:
# * climate_unit: The Climate entity to be controlled
# * global_mode: an entity whose state is the desired global climate mode (usually an input_select)
# * at_home_sensor: an entity that represents whether anyone is home (usually a binary_sensor)
# * from_timer: whether the script was triggered by timer. If true, only changes to the new mode /
#   setpoint within the first 15 minutes of each schedule, so that manual overrides stick until
#   the next schedule.
#
# The last input is the 'seasons' dictionary as defined below, which defines the scheduled behavior
# for each global mode / climate unit combination. It's a dictionary keyed by a tuple of
# global mode and climate unit. Each entry is a list of schedules, where each schedule has the
# following fields:
# * title: Used only for logging and to help you find the right entry for edits
# * time_on / time_off (optional): Start and stop of this schedule, 24-hour hours:minutes. If not
#   given, this schedule is always active (though see window and if_away/if_home below)
# * operation: The operating mode for this schedule, one of the modes supported by your climate
#   entity.
# * setpoint (optional): The desired temperature for this schedule. Some modes (e.g. 'dry'
#   dehumidifaction) don't require a setpoint so it's optional
# * window (optional): If given, if this entity's state is 'on' (i.e. the given window is open),
#   the schedule will act as if its operation mode is 'off'. This is so you don't attempt to
#   heat/cool the great outdoors if you left the window open for some fresh air.
# * if_away / if_home (optional): If present, this schedule will only apply if the at_home_sensor
#   state matches (true meaning someone is home). If no at_home_sensor is given, these are both
#   always false.
#
# Put this script in <config>/python_scripts (create the directory if needed) and activate it
# as described at https://www.home-assistant.io/components/python_script/ .
# You should set up automations to call service python_script.seasons for each relevant climate
# unit for the each of the following events:
# * your global_mode entity changes (all climate units)
# * your at_home_sensor changes (all climate units)
# * your window sensor(s) change(s) (relevant climate units)
# * on a time_interval, suggested every 15 minutes. (all climate units). This interval is the
#   resolution of your scheduled changes, so make it more or less frequent as required; you may
#   need to change the 'interval' variable below as well.

seasons = {
    ('Normal Summer', 'climate.master_br'): [
        {
            'title': 'Sleeping',
            'time_on': '20:30',
            'time_off': '09:00',
            'operation': 'cool',
            'window': 'binary_sensor.bedroom_window',
            'setpoint': 73
        },
    ],
    ('Normal Summer', 'climate.first_floor'): [
        {
            'title': 'Off',
            'operation': 'off',
        },
    ],
    ('Normal Summer', 'climate.loft'): [
        {
            'title': 'Off',
            'operation': 'off',
        },
    ],
    ('Humid Summer', 'climate.master_br'): [
        {
            'title': 'Dehumidify',
            'time_on': '19:30',
            'time_off': '21:00',
            'operation': 'dry',
            'window': 'binary_sensor.bedroom_window',
            'setpoint': 73
        },
        {
            'title': 'Sleeping',
            'time_on': '21:00',
            'time_off': '09:00',
            'operation': 'cool',
            'window': 'binary_sensor.bedroom_window',
            'setpoint': 73
        },
    ],
    ('Humid Summer', 'climate.first_floor'): [
        {
            'title': 'Off',
            'operation': 'off',
        },
    ],
    ('Humid Summer', 'climate.loft'): [
        {
            'title': 'Off',
            'operation': 'off',
        },
    ],
    ('Hot Summer', 'climate.master_br'): [
        {
            'title': 'Sleeping',
            'time_on': '20:00',
            'time_off': '09:00',
            'operation': 'cool',
            'window': 'binary_sensor.bedroom_window',
            'setpoint': 73
        },
        {
            'title': 'Day (Away)',
            'time_on': '09:30',
            'time_off': '19:45',
            'operation': 'cool',
            'window': 'binary_sensor.bedroom_window',
            'if_away': True,
            'setpoint': 78
        },
        {
            'title': 'Day (Home)',
            'time_on': '09:00',
            'time_off': '19:45',
            'operation': 'cool',
            'window': 'binary_sensor.bedroom_window',
            'setpoint': 75
        },
    ],
    ('Hot Summer', 'climate.loft'): [
        {
            'title': 'Maintenance',
            'operation': 'cool',
            'window': 'binary_sensor.skylight',
            'setpoint': 80
        }
    ],
    ('Hot Summer', 'climate.first_floor'): [
        {
            'title': 'Sleeping',
            'time_on': '22:00',
            'time_off': '06:00',
            'operation': 'cool',
            'setpoint': 78
        },
        {
            'title': 'Day (Away)',
            'time_on': '08:00',
            'time_off': '16:00',
            'operation': 'cool',
            'if_away': True,
            'setpoint': 78
        },
        {
            'title': 'Day (Home)',
            'time_on': '06:00',
            'time_off': '16:00',
            'operation': 'cool',
            'setpoint': 72
        },
        {
            'title': 'Evening (Away)',
            'time_on': '18:00',
            'time_off': '22:00',
            'operation': 'cool',
            'if_away': True,
            'setpoint': 78
        },
        {
            'title': 'Evening (Home)',
            'time_on': '16:00',
            'time_off': '22:00',
            'operation': 'cool',
            'setpoint': 72
        }
    ]
}

def is_time_between(begin_time, end_time, check_time):
    if begin_time < end_time:
        return check_time >= begin_time and check_time <= end_time
    # crosses midnight
    return check_time >= begin_time or check_time <= end_time

def time_offset(orig_time, offset):
    hr = orig_time.hour
    min = orig_time.minute
    min = min + offset
    if min < 0:
        hr = hr - 1
        min = min + 60
    if min > 60:
        hr = hr + 1
        min = min - 60
    if hr < 0:
        hr = hr + 24
    if hr > 24:
        hr = hr - 24
    return datetime.time(hour=hr, minute=min)

interval = 15

climate_unit = data.get('climate_unit', 'climate.master_br')
current_mode = hass.states.get(data.get('global_mode', 'input_select.climate_mode')).state
from_timer = data.get('from_timer', False)
at_home_sensor = data.get('at_home_sensor')
is_home = False
is_away = False
if at_home_sensor:
    is_home = hass.states.get(at_home_sensor).state
    is_away = not is_home

current_operation = hass.states.get(climate_unit).state
now = datetime.datetime.now().time()

key = (current_mode, climate_unit)
schedules = seasons.get(key)

matched = False
setpoint = None
if not schedules:
    logger.info("No schedules for {}".format(key))
else:
    turn_on = False
    turn_off = False
    desired_operation = None
    setpoint = None
    title = None
    for schedule in schedules:
        time_on_str = schedule.get('time_on')
        time_off_str = schedule.get('time_off')
        time_on = None
        time_off = None
        if time_on_str:
            time_on = datetime.datetime.strptime(time_on_str, '%H:%M').time()
        if time_off_str:
            time_off = datetime.datetime.strptime(time_off_str, '%H:%M').time()
        in_interval = ((not time_on) or (not time_off) or
                       is_time_between(time_on, time_off, now))
        home_away_match = True
        if schedule.get('if_home'):
            home_away_match = is_home
        if schedule.get('if_away'):
            home_away_match = not is_home

        if in_interval and home_away_match:
            if not time_on:
                time_on = datetime.datetime.strptime('00:00', '%H:%M').time()
            first_interval_start = time_on
            first_interval_end = time_offset(time_on, interval)
            in_first_interval = is_time_between(first_interval_start, first_interval_end, now)
            window_open = False
            if schedule.get('window'):
                window_open = hass.states.get(schedule['window']).state is 'on'
            else:
                window_open = False

            # When we get here, we have schedules for this unit and
            # global mode and we're in this schedule's interval.
            # We will obey this schedule and ignore subsequent matches
            decided = False
            matched = True

            if window_open:
                # Off if window is open
                turn_off = True
                title = schedule.get('title') + ' (Window open)'
                decided = True
            if not decided and from_timer and in_first_interval:
                desired_operation = schedule.get('operation')
                if desired_operation == 'off':
                    turn_off = True
                else:
                    turn_on = True
                setpoint = schedule.get('setpoint')
                title = schedule.get('title')
                decided = True
            if not decided and not from_timer:
                desired_operation = schedule.get('operation')
                if desired_operation == 'off':
                    turn_off = True
                else:
                    turn_on = True
                setpoint = schedule.get('setpoint')
                title = schedule.get('title')
                decided = True
            break
        
    if not matched:
        # If no schedules matched, turn off
        # FIXME: only do this just past the most recent schedule period
        turn_off = True
        title = 'Default (Off)'

    if turn_off:
        desired_operation = 'off'

    logger.info("Setting {} to mode {} target {} from schedule {}".format(
        climate_unit, desired_operation, setpoint, title))

    if setpoint and desired_operation:
        service_data = {
            "entity_id": climate_unit,
            "temperature": setpoint,
            "operation_mode": desired_operation}
        hass.services.call('climate', 'set_temperature', service_data, False)

    if desired_operation:
        service_data = {
            "entity_id": climate_unit,
            "operation_mode": desired_operation}
        hass.services.call('climate', 'set_operation_mode', service_data, False)
