#!/usr/bin/env python3
from pathlib import Path

# Basiswerte für Scanlines
BASE_PARAMS = {
    "SCANLINE_DENSITY": 600.0,
    "DARK_LEVEL": 0.82,
    "BRIGHT_LEVEL": 1.05,
    "STRENGTH": 1.0
}

# Skala von -5 bis +5, 0 ist Basis
SCALE = list(range(-5, 6))

SHADER_DIR = Path("../../shaders")
SHADER_DIR.mkdir(parents=True, exist_ok=True)

for i in SCALE:
    if i == 0:
        filename = SHADER_DIR / "scanlines_0.glsl"
    else:
        filename = SHADER_DIR / f"scanlines_{i}.glsl"

    # Berechne Parameteränderungen
    # SCANLINE_DENSITY ±10% pro Schritt
    density = BASE_PARAMS["SCANLINE_DENSITY"] * (1 + 0.1 * i)
    # STRENGTH ±0.2 pro Schritt, clamp zwischen 0 und 2
    strength = min(max(BASE_PARAMS["STRENGTH"] * (1 + 0.2 * i), 0.0), 2.0)

    content = f"""//!HOOK MAIN
//!BIND HOOKED
//!DESC Scanlines Overlay

// ===== Scanline parameters =====
const float SCANLINE_DENSITY = {density:.1f};  // Vertical scanline frequency
const float DARK_LEVEL       = {BASE_PARAMS['DARK_LEVEL']:.2f};  // Brightness of dark scanlines
const float BRIGHT_LEVEL     = {BASE_PARAMS['BRIGHT_LEVEL']:.2f};  // Brightness between scanlines
const float STRENGTH         = {strength:.2f};  // Overall scanline intensity

vec4 hook() {{
    vec4 c = HOOKED_tex(HOOKED_pos);

    // ===== Scanline pattern =====
    float scan = sin(HOOKED_pos.y * SCANLINE_DENSITY) * 0.5 + 0.5;

    // Interpolate between dark and bright regions
    float modulation = mix(DARK_LEVEL, BRIGHT_LEVEL, scan);

    // Apply scanline modulation with brightness compensation
    c.rgb *= mix(1.0, modulation, STRENGTH);

    return c;
}}
"""
    with open(filename, "w") as f:
        f.write(content)
    print(f"Generated {filename}")
