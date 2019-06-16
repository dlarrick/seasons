def is_time_between(begin_time, end_time, check_time):
    # If check time is not given, default to current UTC time
    if begin_time < end_time:
        return check_time >= begin_time and check_time <= end_time
    else: # crosses midnight
        return check_time >= begin_time or check_time <= end_time

def time_offset(orig_time, offset):
    h = orig_time.hour
    m = orig_time.minute
    m = m + offset
    if m < 0:
        h = h - 1
        m = m + 60
    if m > 60:
        h = h + 1
        m = m - 60
    if h < 0:
        h = h + 24
    if h > 24:
        h = h - 24
    return datetime.time(hour=h, minute=m)
    
interval = 15
target_modes = ['Normal Summer', 'Hot Summer']

climate_unit = data.get('climate_unit', 'climate.master_br')
operation = data.get('operation', 'cool')
setpoint = data.get('setpoint', 73)
window = data.get('window', 'binary_sensor.bedroom_window')
from_timer = data.get('from_timer', False)
time_on = datetime.datetime.strptime(data.get('time_on', '20:00'), '%H:%M').time()
time_off = datetime.datetime.strptime(data.get('time_off', '09:00'), '%H:%M').time()

first_interval_start = time_offset(time_on, -interval)
first_interval_end = time_offset(time_on, interval)

current_mode = hass.states.get('input_select.climate_mode').state
current_operation = hass.states.get(climate_unit).state
now = datetime.datetime.now().time()

in_interval = is_time_between(time_on, time_off, now)
in_first_interval = is_time_between(first_interval_start, first_interval_end, now)

window_open = False
if window:
    window_open = hass.states.get(window).state is 'on'
else:
    window_open = False

in_target_mode = current_mode in target_modes

decided = False
turn_off = False
turn_on = False

# If we're not in target mode, window is open, or we're outside the
# interval, turn off
if (not in_target_mode) or window_open or (not in_interval):
    turn_off = True
    decided = True

# If we're called from timer, turn on if we're in the first interval
if not decided:
    if from_timer and in_first_interval:
        turn_on = True
        decided = True

# If we're called from event, turn on if we're in the interval
if not decided:
    if not from_timer and in_interval:
        turn_on = True
        decided = True

target_operation = 'off'
if decided and turn_off:
    target_operation = 'off'
elif decided and turn_on:
    target_operation = operation

if decided:
    logger.info("Setting {} to mode {} target {}".format(climate_unit, target_operation, setpoint))
    service_data = {
        "entity_id": climate_unit,
        "temperature": setpoint,
        "operation_mode": target_operation}
    hass.services.call('climate', 'set_temperature', service_data, False)
    service_data = {
        "entity_id": climate_unit,
        "operation_mode": target_operation}
    hass.services.call('climate', 'set_operation_mode', service_data, False)
        
