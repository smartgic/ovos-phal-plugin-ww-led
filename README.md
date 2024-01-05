# PHAL plugin - Wakeword LED

A light _(LED)_ indicator when Open Voice OS is listening and/or speaking.

[![Video](https://img.youtube.com/vi/u3cftkais9s/maxresdefault.jpg)](https://www.youtube.com/watch?v=u3cftkais9s)

## About

This PHAL plugin interacts with a LED connected to a GPIO to let you know if Open Voice OS is listening. When a wake word is detected the LED turns on and when the audio output is over the LED turns off.

It also possible to configure the plugin to only turn the LED on and off during the listening _(not the audio output)_.

## Installation

```shell
pip install ovos-phal-plugin-ww-led
```

## Configuration

The plugin configuration file is `~/.config/OpenVoiceOS/ovos-phal-plugin-ww-led.json`.

| Option          | Value   | Description                                        |
| --------------- | ------- | -------------------------------------------------- |
| `gpio_pin`      | `N/A`   | GPIO PIN where the LED is connected                |
| `wakeword_only` | `false` | Turn on the LED only during the wakeword detection |
| `pulse`         | `true`  | Make the LED pulse                                 |

### Example

Configuration sample of `~/.config/OpenVoiceOS/ovos-phal-plugin-ww-led.json`.

```json
{
  "gpio_pin": 25,
  "wakeword_only": false,
  "pulse": true
}
```

## Credits

- [Smart'Gic](https://smartgic.io/)
