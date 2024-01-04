from time import sleep
from json_database import JsonConfigXDG
from ovos_plugin_manager.phal import PHALPlugin
from ovos_utils import create_daemon
from ovos_utils.log import LOG

import RPi.GPIO as GPIO


class WwLedPlugin(PHALPlugin):
    def __init__(self, bus=None, config=None):
        super().__init__(bus=bus, name="ovos-phal-plugin-ww-led", config=config)

        self.settings = JsonConfigXDG(self.name, subfolder="OpenVoiceOS")
        self.gpio_pin = self.settings.get("gpio_pin")
        self.wakeword_only = self.settings.get("wakeword_only", False)
        self.pulse = self.settings.get("pulse", True)

        self.duty_cycle = 0
        self.pwm = None
        self.pulsing = False

        try:
            # Setup GPIO
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            GPIO.setup(self.gpio_pin, GPIO.OUT)

            if self.pulse:
                self.pwm = GPIO.PWM(self.gpio_pin, 100)
                self.pwm.start(self.duty_cycle)

            # Catch events
            self.bus.on("recognizer_loop:record_begin", self._handle_listener_started)
            self.bus.on("recognizer_loop:record_end", self._handle_listener_ended)
            self.bus.on("recognizer_loop:audio_output_end", self._handle_audio_ended)
        except RuntimeError:
            LOG.error("Cannot initialize GPIO - plugin will not load")

    def led_pulsing_thread(self):
        create_daemon(self._pulsing)

    def _pulsing(self):
        while self.pulsing:
            for self.duty_cycle in range(0, 101, 5):
                self.pwm.ChangeDutyCycle(self.duty_cycle)
                sleep(0.05)

            for self.duty_cycle in range(100, -1, -5):
                self.pwm.ChangeDutyCycle(self.duty_cycle)
                sleep(0.05)

    def _handle_listener_started(self, message):
        """Handle the record_begin event detection and turn the LED on."""
        if self.pulse:
            self.pulsing = True
            self.led_pulsing_thread()
        else:
            GPIO.output(self.gpio_pin, GPIO.HIGH)

    def _handle_listener_ended(self, message):
        """Handle the record_end event detection and turn the LED off."""
        if self.wakeword_only:
            if self.pulse:
                self.pulsing = False
            else:
                GPIO.output(self.gpio_pin, GPIO.LOW)

    def _handle_audio_ended(self, message):
        """Handle the record_end event detecti"""
        if not self.wakeword_only:
            if self.pulse:
                self.pulsing = False
            else:
                GPIO.output(self.gpio_pin, GPIO.LOW)
