import time
from typing import Union

from inputs import get_gamepad
import pyvjoy
from pyvjoy.vjoydevice import VJoyDevice

CONTROLLER = VJoyDevice(1)
BTN_MAP = {
    "BTN_START": 1,
    "BTN_SELECT": 2,
    "BTN_WEST": 3,
    "BTN_NORTH": 4,
    "BTN_SOUTH": 5,
    "BTN_EAST": 6,
    "BTN_THUMBL": 11,
    "BTN_THUMBR": 12,
    "BTN_TL": 13,
    "BTN_TR": 14,
}
ABS_MAP = {
    "ABS_X": pyvjoy.HID_USAGE_X,
    "ABS_Y": pyvjoy.HID_USAGE_Y,
    "ABS_Z": pyvjoy.HID_USAGE_Z,
    "ABS_RX": pyvjoy.HID_USAGE_RX,
    "ABS_RY": pyvjoy.HID_USAGE_RY,
    "ABS_RZ": pyvjoy.HID_USAGE_RZ,
    "ABS_HAT0Y": {1: 8, -1: 7},
    "ABS_HAT0X": {1: 10, -1: 9},
}


def map_axis_value(axis_in: int) -> int:
    """Converts Xbox controller joystick axis value to a vJoy controller
    joystick axis value.

    Args:
        axis_in (int): Integer axis value of Xbox joystick.

    Returns:
        int: Corresponding integer axis value of vJoy joystick.
    """
    return int(0.5 * axis_in + 16383.5)


def map_trigger_value(trigger_in: int) -> int:
    """Converts Xbox controller trigger axis value to a vJoy controller
    joystick axis value.

    Args:
        trigger_in (int): Integer axis value of Xbox trigger.

    Returns:
        int: Corresponding integer axis value of vJoy joystick.
    """
    return int(128.5 * trigger_in)


def push_button(button: int, delay: Union[int, float] = 0.1) -> None:
    """Emulates the action of pressing a vJoy controller button by setting a
    button high and then, after a short delay, setting the same button back
    low.

    Args:
        button (int): The button number of the vJoy button to push.
        delay (Union[int, float], optional): How long in seconds the button
            pressing action should take. Defaults to 0.2.
    """
    CONTROLLER.set_button(button, 1)
    time.sleep(delay)
    CONTROLLER.set_button(button, 0)


def initialize_axes():
    "Sets all vJoy axes to neutral position"
    for axis in ABS_MAP.keys():
        if axis.endswith(("0X", "0Y")):
            continue
        if axis.endswith("Z"):
            CONTROLLER.set_axis(ABS_MAP[axis], map_trigger_value(0))
        else:
            CONTROLLER.set_axis(ABS_MAP[axis], map_axis_value(0))


def main():

    initialize_axes()
    left_trig = 0

    while 1:
        events = get_gamepad()
        for event in events:

            if left_trig:
                if event.code == "BTN_TL" and event.state == 0:
                    print("Left trigger released")
                    CONTROLLER.set_button(13, 0)
                    left_trig = 0

                if event.code == "BTN_NORTH" and event.state == 1:
                    print("Y button submitted with trigger held")
                    push_button(7)
                    push_button(8)
                    push_button(10)
                    push_button(9)
                    push_button(7)

            if event.code == "BTN_TL" and event.state == 1:
                print("Left trigger pressed")
                CONTROLLER.set_button(13, 1)
                left_trig = 1

            if event.code.startswith("ABS"):
                if event.code.endswith("Z"):
                    CONTROLLER.set_axis(
                        ABS_MAP[event.code], map_trigger_value(event.state)
                    )
                elif event.code.endswith(("0X", "0Y")):
                    if event.state == 0:
                        for button in ABS_MAP[event.code].values():
                            CONTROLLER.set_button(button, 0)
                    else:
                        CONTROLLER.set_button(
                            ABS_MAP[event.code][event.state],
                            abs(ABS_MAP[event.code][event.state]),
                        )
                else:
                    CONTROLLER.set_axis(
                        ABS_MAP[event.code], map_axis_value(event.state)
                    )
            elif event.code.startswith("BTN"):
                CONTROLLER.set_button(BTN_MAP[event.code], event.state)

            else:
                if event.ev_type != "Sync":
                    print(event.ev_type, event.code, event.state)


if __name__ == "__main__":
    main()
