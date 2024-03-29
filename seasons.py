# Seasons.py -- Hass helper python_script to turn a Climate entity into a smart
# thermostat, with support for multiple thermostats each having their own
# schedule.
#
# INPUTS:
# * climate_unit (required): The Climate entity to be controlled
# * global_mode (required): an entity whose state is the desired global climate
#   mode (usually an input_select)
# * state_entity (required): an input_text entity, unique to this climate_unit,
#   where the script can store some information between runs.
# * at_home_sensor (optional): an entity that represents whether anyone is home
#   (usually a binary_sensor)
# * from_timer (optional): whether the script was triggered by timer. If true,
#   only changes that modify the last-set operation mode or setpoint take
#   effect. This is done so that manual changes are left alone until the next
#   schedule switch.
#
# The last input is the 'seasons' dictionary as defined below, which defines the
# scheduled behavior for each global mode / climate unit combination. It's a
# dictionary keyed by a tuple of global mode and climate unit. Each entry is a
# list of schedules, where each schedule has the following fields:
# * title: Used only for logging and to help you find the right entry for edits
# * time_on / time_off (optional): Start and stop of this schedule, 24-hour
#   hours:minutes. If not given, this schedule is always active (though see
#   window and if_away/if_home below)
# * days: (optional): String defining days of week this schedule is active, matched
#   on the schedule's start time. Seven characters, dash or dot if not active, any
#   other character if active. You can use 0123456 or MTWTFSS or whatever you like.
#   Monday is first, following Python datetime convention.
# * operation (required): The operating mode for this schedule, one of the modes
#   supported by your climate entity.
# * setpoint (optional): The desired temperature for this schedule. Some modes
#   (e.g. 'dry' dehumidifaction) don't require a setpoint so it's optional
# * window (optional): If given, if this entity's state is 'on' (i.e. the given
#   window is open), the schedule will act as if its operation mode is 'off'.
#   This is so you don't attempt to heat/cool the great outdoors if you left the
#   window open for some fresh air.
# * if_away / if_home (optional): If present, this schedule will only apply if
#   the at_home_sensor state matches (true meaning someone is home). If no
#   at_home_sensor is given, these are both always false.
# * humidity_sensor (optional): See if_humid. Note: could also be some other
#   type of sensor, like dewpoint.
# * if_humid (optional): Percentage. If present, this schedule will only apply
#   if the humidity reported by the humidity_sensor is above this value at the
#   beginning of the period.
#
# Put this script in <config>/python_scripts (create the directory if needed)
# and activate it as described at
# https://www.home-assistant.io/components/python_script/ .
# You should set up automations to call service python_script.seasons for each
# relevant climate unit for the each of the following events:
# * your global_mode entity changes (all climate units)
# * your at_home_sensor changes (all climate units)
# * your window sensor(s) change(s) (relevant climate units)
# * on a time_interval, suggested every 15 minutes. (all climate units). This
#   interval is the resolution of your scheduled changes, so make it more or
#   less frequent as required.

SEASONS = {
    ('Cold Winter', 'climate.first_floor_heat'): [
        {
            'title': 'Ecobee schedule',
            'operation': 'heat'
        }
    ],
    ('Cold Winter', 'climate.second_floor'): [
        {
            'title': 'Ecobee schedule',
            'operation': 'heat'
        }
    ],
    ('Cold Winter', 'climate.loft_heat'): [
        {
            'title': 'Ecobee schedule',
            'operation': 'heat'
        }
    ],
    ('Winter', 'climate.first_floor_heat'): [
        {
            'title': 'Ecobee schedule',
            'operation': 'heat'
        }
    ],
    ('Winter', 'climate.second_floor'): [
        {
            'title': 'Ecobee schedule',
            'operation': 'heat'
        }
    ],
    ('Winter', 'climate.master_br'): [
        {
            'title': 'Winter Sleeping',
            'time_on': '21:29',
            'time_off': '07:59',
            'operation': 'heat',
            'setpoint': 64
        }
    ],
    ('Winter', 'climate.loft_heat'): [
        {
            'title': 'Ecobee schedule',
            'operation': 'heat'
        }
    ],
    ('Cold Shoulder', 'climate.first_floor_heat'): [
        {
            'title': 'Ecobee schedule',
            'operation': 'heat'
        }
    ],
    ('Cold Shoulder', 'climate.master_br'): [
        {
            'title': 'Morning (weekday)',
            'days': 'MTWTF..',
            'time_on': '05:44',
            'time_off': '07:59',
            'operation': 'heat',
            'window': 'binary_sensor.bedroom_window',
            'setpoint': 67
        },
        {
            'title': 'Morning (weekend)',
            'days': '.....SS',
            'time_on': '07:29',
            'time_off': '08:59',
            'operation': 'heat',
            'window': 'binary_sensor.bedroom_window',
            'setpoint': 68
        },
        {
            'title': 'Sleeping',
            'time_on': '21:59',
            'time_off': '08:59',
            'operation': 'heat',
            'window': 'binary_sensor.bedroom_window',
            'setpoint': 64
        },
        {
            'title': 'Day (Away)',
            'time_on': '07:59',
            'time_off': '16:29',
            'if_away': True,
            'operation': 'heat',
            'window': 'binary_sensor.bedroom_window',
            'setpoint': 62
        },
        {
            'title': 'Day (Home)',
            'time_on': '07:59',
            'time_off': '17:59',
            'operation': 'heat',
            'window': 'binary_sensor.bedroom_window',
            'setpoint': 68
        },
        {
            'title': 'Evening (Away)',
            'time_on': '17:59',
            'time_off': '21:44',
            'operation': 'heat',
            'window': 'binary_sensor.bedroom_window',
            'if_away': True,
            'setpoint': 62
        },
        {
            'title': 'Evening (Home)',
            'time_on': '15:59',
            'time_off': '21:44',
            'operation': 'heat',
            'window': 'binary_sensor.bedroom_window',
            'setpoint': 68
        }
    ],
    ('Cold Shoulder', 'climate.loft_heat'): [
        {
            'title': 'Morning Boost',
            'operation': 'heat',
            'time_on': '06:59',
            'time_off': '07:44',
            'window': 'binary_sensor.skylight',
            'setpoint': 68
        }
    ],
    ('Cold Shoulder', 'climate.loft'): [
        {
            'title': 'Night',
            'operation': 'heat',
            'time_on': '00:04',
            'time_off': '07:14',
            'window': 'binary_sensor.skylight',
            'setpoint': 61
        },
        {
            'title': 'Day (Weekday)',
            'days': 'MTWTF..',
            'operation': 'heat',
            'time_on': '07:14',
            'time_off': '16:59',
            'window': 'binary_sensor.skylight',
            'setpoint': 68
        },
        {
            'title': 'Day (Weekend)',
            'days': '.....SS',
            'operation': 'heat',
            'time_on': '08:59',
            'time_off': '16:59',
            'window': 'binary_sensor.skylight',
            'setpoint': 62
        },
        {
            'title': 'Evening',
            'operation': 'heat',
            'time_on': '16:59',
            'time_off': '00:04',
            'window': 'binary_sensor.skylight',
            'setpoint': 63
        }
    ],
    ('Warm Shoulder', 'climate.first_floor'): [
        {
            'title': 'Morning (weekday)',
            'days': 'MTWTF..',
            'time_on': '05:44',
            'time_off': '07:59',
            'operation': 'heat',
            'setpoint': 68
        },
        {
            'title': 'Morning (weekend)',
            'days': '.....SS',
            'time_on': '07:29',
            'time_off': '08:59',
            'operation': 'heat',
            'setpoint': 68
        },
        {
            'title': 'Pre-Sleeping',
            'time_on': '21:44',
            'time_off': '21:59',
            'operation': 'heat',
            'setpoint': 62
        },
        {
            'title': 'Sleeping',
            'time_on': '21:59',
            'time_off': '08:59',
            'operation': 'heat',
            'setpoint': 62
        },
        {
            'title': 'Day (Away)',
            'time_on': '08:59',
            'time_off': '16:29',
            'if_away': True,
            'operation': 'heat',
            'setpoint': 62
        },
        {
            'title': 'Day (Home)',
            'time_on': '08:59',
            'time_off': '17:59',
            'operation': 'heat',
            'setpoint': 68
        },
        {
            'title': 'Evening (Away)',
            'time_on': '17:59',
            'time_off': '21:44',
            'operation': 'heat',
            'if_away': True,
            'setpoint': 62
        },
        {
            'title': 'Evening (Home)',
            'time_on': '15:59',
            'time_off': '21:44',
            'operation': 'heat',
            'setpoint': 69
        }
    ],
    ('Warm Shoulder', 'climate.master_br'): [
        {
            'title': 'Morning (weekday)',
            'days': 'MTWTF..',
            'time_on': '05:44',
            'time_off': '07:59',
            'operation': 'heat',
            'setpoint': 67
        },
        {
            'title': 'Morning (weekend)',
            'days': '.....SS',
            'time_on': '07:29',
            'time_off': '08:59',
            'operation': 'heat',
            'setpoint': 68
        },
        {
            'title': 'Pre-Sleeping',
            'time_on': '21:44',
            'time_off': '21:59',
            'operation': 'heat',
            'setpoint': 64
        },
        {
            'title': 'Sleeping',
            'time_on': '21:59',
            'time_off': '08:59',
            'operation': 'heat',
            'setpoint': 64
        },
        {
            'title': 'Day (Away)',
            'time_on': '08:59',
            'time_off': '16:29',
            'if_away': True,
            'operation': 'heat',
            'setpoint': 62
        },
        {
            'title': 'Day (Home)',
            'time_on': '08:59',
            'time_off': '17:59',
            'operation': 'heat',
            'setpoint': 68
        },
        {
            'title': 'Evening (Away)',
            'time_on': '17:59',
            'time_off': '21:44',
            'operation': 'heat',
            'if_away': True,
            'setpoint': 62
        },
        {
            'title': 'Evening (Home)',
            'time_on': '15:59',
            'time_off': '21:44',
            'operation': 'heat',
            'setpoint': 68
        }
    ],
    ('Warm Shoulder', 'climate.loft'): [
        {
            'title': 'Night',
            'operation': 'heat',
            'time_on': '00:04',
            'time_off': '07:29',
            'window': 'binary_sensor.skylight',
            'setpoint': 61
        },
        {
            'title': 'Day (Weekday)',
            'days': 'MTWTF..',
            'operation': 'heat',
            'time_on': '07:29',
            'time_off': '17:59',
            'window': 'binary_sensor.skylight',
            'setpoint': 68
        },
        {
            'title': 'Day (Weekend)',
            'days': '.....SS',
            'operation': 'heat',
            'time_on': '08:59',
            'time_off': '17:59',
            'window': 'binary_sensor.skylight',
            'setpoint': 62
        },
        {
            'title': 'Evening',
            'operation': 'heat',
            'time_on': '17:59',
            'time_off': '00:04',
            'window': 'binary_sensor.skylight',
            'setpoint': 63
        }
    ],
    ('Normal Summer', 'climate.master_br'): [
        {
            'title': 'Dehumidify',
            'time_on': '19:59',
            'time_off': '20:59',
            'operation': 'dry',
            'humidity_sensor': 'sensor.dewpoint_mbr',
            'if_humid': 63,
            'window': 'binary_sensor.bedroom_window',
        },
        {
            'title': 'Sleeping-early',
            'time_on': '20:59',
            'time_off': '02:59',
            'operation': 'cool',
            'window': 'binary_sensor.bedroom_window',
            'setpoint': 73
        },
        {
            'title': 'Sleeping-late',
            'time_on': '02:59',
            'time_off': '07:59',
            'operation': 'cool',
            'window': 'binary_sensor.bedroom_window',
            'setpoint': 74
        },
    ],
    ('Hot Summer', 'climate.master_br'): [
        {
            'title': 'Dehumidify',
            'time_on': '19:59',
            'time_off': '20:59',
            'operation': 'dry',
            'humidity_sensor': 'sensor.dewpoint_mbr',
            'if_humid': 63,
            'window': 'binary_sensor.bedroom_window',
        },
        {
            'title': 'Sleeping-early',
            'time_on': '20:59',
            'time_off': '02:59',
            'operation': 'cool',
            'window': 'binary_sensor.bedroom_window',
            'setpoint': 73
        },
        {
            'title': 'Sleeping-late',
            'time_on': '02:59',
            'time_off': '07:59',
            'operation': 'cool',
            'window': 'binary_sensor.bedroom_window',
            'setpoint': 74
        },
        {
            'title': 'Day (Away)',
            'time_on': '08:29',
            'time_off': '19:44',
            'operation': 'cool',
            'window': 'binary_sensor.bedroom_window',
            'if_away': True,
            'setpoint': 78
        },
        {
            'title': 'Day (Home)',
            'time_on': '08:29',
            'time_off': '19:44',
            'operation': 'cool',
            'window': 'binary_sensor.bedroom_window',
            'setpoint': 76
        },
    ],
    ('Hot Summer', 'climate.loft'): [
        {
            'title': 'Night',
            'operation': 'cool',
            'time_on': '00:04',
            'time_off': '08:59',
            'window': 'binary_sensor.skylight',
            'setpoint': 83
        },
        {
            'title': 'Day (away)',
            'operation': 'cool',
            'time_on': '08:59',
            'time_off': '17:59',
            'if_away': True,
            'window': 'binary_sensor.skylight',
            'setpoint': 85
        },
        {
            'title': 'Day',
            'operation': 'cool',
            'time_on': '08:59',
            'time_off': '17:59',
            'window': 'binary_sensor.skylight',
            'setpoint': 80
        },
        {
            'title': 'Evening',
            'operation': 'cool',
            'time_on': '17:59',
            'time_off': '00:04',
            'window': 'binary_sensor.skylight',
            'setpoint': 81
        }
    ],
    ('Hot Summer', 'climate.first_floor'): [
        {
            'title': 'Sleeping',
            'time_on': '21:59',
            'time_off': '05:59',
            'window': 'binary_sensor.first_floor_windows',
            'operation': 'cool',
            'setpoint': 78
        },
        {
            'title': 'Day (Away)',
            'time_on': '07:59',
            'time_off': '15:59',
            'operation': 'cool',
            'window': 'binary_sensor.first_floor_windows',
            'if_away': True,
            'setpoint': 78
        },
        {
            'title': 'Day (Home)',
            'time_on': '05:59',
            'time_off': '15:59',
            'window': 'binary_sensor.first_floor_windows',
            'operation': 'cool',
            'setpoint': 75
        },
        {
            'title': 'Evening (Away)',
            'time_on': '17:59',
            'time_off': '21:44',
            'operation': 'cool',
            'window': 'binary_sensor.first_floor_windows',
            'if_away': True,
            'setpoint': 78
        },
        {
            'title': 'Evening (Home)',
            'time_on': '15:59',
            'time_off': '21:44',
            'window': 'binary_sensor.first_floor_windows',
            'operation': 'cool',
            'setpoint': 75
        }
    ]
}

def is_time_between(begin_time, end_time, check_time):
    if begin_time < end_time:
        return begin_time <= check_time <= end_time
    # crosses midnight
    return check_time >= begin_time or check_time <= end_time

def time_offset(orig_time, offset):
    hour = orig_time.hour
    minute = orig_time.minute
    minute = minute + offset
    if minute < 0:
        hour = hour - 1
        minute = minute + 60
    if minute > 60:
        hour = hour + 1
        minute = minute - 60
    if hour < 0:
        hour = hour + 24
    if hour > 24:
        hour = hour - 24
    return datetime.time(hour=hour, minute=minute)

def day_of_start(start_time, end_time, check_time):
    today = datetime.datetime.now().weekday()
    # today if doesn't cross midnight or no actual times given
    if (not start_time) or (not end_time) or start_time <= end_time:
        return today
    # today if we're between start and midnight
    if start_time <= check_time:
        return today
    # Otherwise, yesterday
    return 6 if today == 0 else today - 1

saved_state = hass.states.get(data.get('state_entity')).state
climate_unit = data.get('climate_unit', 'climate.master_br')
current_mode = hass.states.get(data.get('global_mode')).state
from_timer = data.get('from_timer', False)
at_home_sensor = data.get('at_home_sensor')
is_home = False
is_away = False
if at_home_sensor:
    is_home = hass.states.get(at_home_sensor).state == 'on'
    is_away = not is_home

now = datetime.datetime.now().time()

key = (current_mode, climate_unit)
schedules = SEASONS.get(key)

matched = False
setpoint = None
turn_on = False
turn_off = False
desired_operation = None
title = None
next_state = None
if not schedules:
    logger.info("No schedules for {}".format(key))
else:
    for schedule in schedules:
        time_on_str = schedule.get('time_on')
        time_off_str = schedule.get('time_off')
        time_on = None
        time_off = None
        if time_on_str:
            time_on = datetime.datetime.strptime(time_on_str, '%H:%M').time()
        if time_off_str:
            time_off = datetime.datetime.strptime(time_off_str, '%H:%M').time()

        start_day = day_of_start(time_on, time_off, now)
        day_match = True
        days = schedule.get('days')
        if days and len(days) == 7:
            day_match = days[start_day] != '-' and days[start_day] != '.'

        in_interval = day_match and (((not time_on) or (not time_off) or
                                      is_time_between(time_on, time_off, now)))

        home_away_match = True
        if schedule.get('if_home'):
            home_away_match = is_home
        if schedule.get('if_away'):
            home_away_match = not is_home

        dry_exclude = False
        hs = schedule.get('humidity_sensor')
        if hs and schedule.get('if_humid'):
            dry_exclude = float(hass.states.get(hs).state) < float(schedule['if_humid'])

        if in_interval and home_away_match and not dry_exclude:
            # When we get here, we have schedules for this unit and
            # global mode and we're in this schedule's interval.
            # We will obey this schedule and ignore subsequent matches
            if not time_on:
                time_on = datetime.datetime.strptime('00:00', '%H:%M').time()
            window_open = False
            if schedule.get('window'):
                window_open = hass.states.get(schedule['window']).state == 'on'
            else:
                window_open = False

            decided = False
            matched = True
            next_state = "%s-%s" % (str(schedule.get('operation')),
                                    str(schedule.get('setpoint')))
            same_next_state = (next_state == saved_state)
            if window_open:
                # Off if window is open
                turn_off = True
                title = schedule.get('title') + ' (Window open)'
                decided = True
            if (not decided) and from_timer and (not same_next_state):
                desired_operation = schedule.get('operation')
                if desired_operation == 'off':
                    turn_off = True
                else:
                    turn_on = True
                setpoint = schedule.get('setpoint')
                title = schedule.get('title')
                decided = True
            if not decided and (not from_timer):
                desired_operation = schedule.get('operation')
                if desired_operation == 'off':
                    turn_off = True
                else:
                    turn_on = True
                setpoint = schedule.get('setpoint')
                title = schedule.get('title')
                decided = True
            break

if not matched and current_mode != "Manual":
    # If no schedules matched, turn off except in Manual
    next_state = "off-None"
    same_next_state = (next_state == saved_state)
    if (not from_timer) or (not same_next_state):
        turn_off = True
        title = 'Default (Off)'

if turn_off:
    desired_operation = 'off'

if desired_operation:
    logger.info("Setting {} to mode {} target {} from schedule {}".format(
        climate_unit, desired_operation, setpoint, title))
    service_data = {
        "entity_id": climate_unit,
        "hvac_mode": desired_operation
    }
    hass.services.call('climate', 'set_hvac_mode', service_data, False)

    if setpoint:
        time.sleep(2.0)
        if '.' in str(setpoint):
            setpoint_num = float(setpoint)
        else:
            setpoint_num = int(setpoint)
        service_data = {
            "entity_id": climate_unit,
            "temperature": setpoint_num,
            "hvac_mode": desired_operation
        }
        hass.services.call('climate', 'set_temperature', service_data, False)

if next_state:
    hass.states.set(data.get('state_entity'), next_state)

