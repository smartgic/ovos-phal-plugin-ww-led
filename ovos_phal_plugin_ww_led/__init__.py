"""Wake word LED entrypoint PHAL plugin
"""
from time import sleep
from json_database import JsonConfigXDG
from ovos_plugin_manager.phal import PHALPlugin
from ovos_utils import create_daemon
from ovos_utils.log import LOG

from RPi import GPIO


class WwLedPlugin(PHALPlugin):
    """This is the place where all the magic happens for the
    wake word LED PHAL plugin.
    """

    def __init__(self, bus=None, config=None):
        super().__init__(bus=bus, name="ovos-phal-plugin-ww-led", config=config)

        # Retrieves settings from ~/.config/OpenVoiceOS/ovos-phal-plugin-ww-led.json
        self.settings = JsonConfigXDG(self.name, subfolder="OpenVoiceOS")
        self.gpio_pin = self.settings.get("gpio_pin")
        self.wakeword_only = self.settings.get("wakeword_only", False)
        self.pulse = self.settings.get("pulse", True)

        # Default values
        self.duty_cycle = 0
        self.pwm = None
        self.pulsing = False

        try:
            # Setup GPIO
            # By default the GPIO module will be configured with BCM.
            # https://raspberrypi.stackexchange.com/a/12967
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            GPIO.setup(self.gpio_pin, GPIO.OUT)

            if self.pulse:
                # Set GPIO PIN to PWM if pulse is configured
                self.pwm = GPIO.PWM(self.gpio_pin, 100)
                self.pwm.start(self.duty_cycle)

            # Map bus events to methods
            self.bus.on("recognizer_loop:record_begin", self._handle_listener_started)
            self.bus.on("recognizer_loop:record_end", self._handle_led_off)
            self.bus.on("recognizer_loop:audio_output_end", self._handle_led_off)
            self.bus.on("ovos.utterance.cancelled", self._handle_led_off)
        except RuntimeError:
            LOG.error("Cannot initialize GPIO - plugin will not load")

    def led_pulsing_thread(self):
        """Wrapper function calling the create_daemon() method from ovos-utils
        to start a thread.
        """
        create_daemon(self._pulsing)

    def _pulsing(self):
        """Watchdog for the create_daemon() method
        This will make the LED pulse based on the self.duty_cycle variable.
        """
        while self.pulsing:
            for self.duty_cycle in range(0, 101, 5):
                self.pwm.ChangeDutyCycle(self.duty_cycle)
                sleep(0.05)

            for self.duty_cycle in range(100, -1, -5):
                self.pwm.ChangeDutyCycle(self.duty_cycle)
                sleep(0.05)

    def _handle_listener_started(self, _):
        """Handle the record_begin event detection and turn the LED on."""
        if self.pulse:
            self.pulsing = True
            self.led_pulsing_thread()
        else:
            GPIO.output(self.gpio_pin, GPIO.HIGH)

    def _handle_led_off(self, _):
        """Handle the different events that will lead to turn the LED off."""
        if not self.wakeword_only:
            if self.pulse:
                self.pulsing = False
            else:
                GPIO.output(self.gpio_pin, GPIO.LOW)
