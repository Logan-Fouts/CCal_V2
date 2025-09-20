from typing import List, Tuple, Dict, Any


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex color string to RGB tuple."""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def apply_brightness(
    color: Tuple[int, int, int], brightness: float
) -> Tuple[int, int, int]:
    """Apply brightness scaling to a color tuple."""
    brightness = max(0.0, min(1.0, float(brightness)))
    return tuple(int(c * brightness) for c in color)


def fade_color(
    start_color: Tuple[int, int, int], end_color: Tuple[int, int, int], progress: float
) -> Tuple[int, int, int]:
    """Fade between two colors based on progress (0.0 to 1.0)."""
    return tuple(
        int(start + (end - start) * progress)
        for start, end in zip(start_color, end_color)
    )


def create_gradient(
    start_color: Tuple[int, int, int], end_color: Tuple[int, int, int], num_leds: int
) -> List[Tuple[int, int, int]]:
    """Create a gradient of colors between start and end."""
    if num_leds == 1:
        return [start_color]
    return [
        fade_color(start_color, end_color, i / (num_leds - 1)) for i in range(num_leds)
    ]


def get_digit_patterns() -> Dict[int, List[int]]:
    """Return digit patterns for number display."""
    return {
        0: [4, 5, 6, 11, 13, 18, 20, 25, 26, 27],
        1: [6, 5, 12, 19, 26, 27, 25],
        2: [4, 5, 6, 11, 19, 25, 26, 27],
        3: [4, 5, 6, 12, 18, 26, 27],
        4: [6, 4, 11, 13, 18, 25, 12],
        5: [6, 13, 5, 4, 18, 25, 26, 27],
        6: [6, 13, 20, 27, 12, 26, 11, 18, 25],
        7: [6, 5, 4, 11, 19, 27],
        8: [4, 5, 6, 11, 13, 18, 20, 25, 26, 27, 19],
        9: [6, 5, 4, 11, 18, 25, 19, 20, 13],
    }


def calculate_time_based_brightness(current_hour: int, base_brightness: float) -> float:
    """Adjust brightness based on time of day."""
    is_night = current_hour >= 22 or current_hour <= 8
    return base_brightness * (0.1 if is_night else 1.0)


def get_temperature_color(temperature: float) -> Tuple[int, int, int]:
    """Get color based on temperature."""
    temp_int = int(round(temperature))
    if temp_int < 0:
        return (0, 200, 255)  # Blue for cold
    elif temp_int < 19:
        return (255, 255, 255)  # White for cool
    else:
        return (0, 255, 0)  # Green for warm
