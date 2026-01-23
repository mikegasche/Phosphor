#!/usr/bin/env python3
from pathlib import Path

# Underlying values for VHS
BASE_PARAMS = {
    "GRAIN_STRENGTH": 0.03,
    "FLICKER_STRENGTH": 0.01,
    "LINE_DENSITY": 10.0,
    "GLITCH_AMOUNT": 0.02
}

# Scale -5 to +5
SCALE = list(range(-5, 6))

SHADER_DIR = Path("../../shaders")
SHADER_DIR.mkdir(parents=True, exist_ok=True)

for i in SCALE:
    if i == 0:
        filename = SHADER_DIR / "vhs_noise_0.glsl"
    else:
        filename = SHADER_DIR / f"vhs_noise_{i}.glsl"

    # Scale calculations
    grain = max(BASE_PARAMS["GRAIN_STRENGTH"] * (1 + 0.2 * i), 0.0)
    flicker = max(BASE_PARAMS["FLICKER_STRENGTH"] * (1 + 0.2 * i), 0.0)
    glitch = max(BASE_PARAMS["GLITCH_AMOUNT"] * (1 + 0.2 * i), 0.0)

    content = f"""//!HOOK MAIN
//!BIND HOOKED
//!DESC VHS: dynamic grain + horizontal glitch

// ===== VHS parameters =====
const float GRAIN_STRENGTH   = {grain:.4f};  // Pixel noise intensity
const float FLICKER_STRENGTH = {flicker:.4f};  // Frame-based brightness flicker
const float LINE_DENSITY     = {BASE_PARAMS['LINE_DENSITY']:.1f};  // Number of horizontal glitch lines
const float GLITCH_AMOUNT    = {glitch:.4f};  // Horizontal glitch displacement strength

vec4 hook() {{
    vec4 col = HOOKED_tex(HOOKED_pos);

    // ===== Noise generation =====
    float grain = (
        fract(
            sin(dot(HOOKED_pos.xy + float(frame), vec2(12.9898, 78.233)))
            * 43758.5453
        ) - 0.5
    ) * GRAIN_STRENGTH;

    // Subtle frame-to-frame flicker
    float flicker = (
        fract(sin(float(frame) * 12.9898) * 43758.5453) - 0.5
    ) * FLICKER_STRENGTH;

    // Horizontal glitch lines
    float yPos = HOOKED_pos.y * LINE_DENSITY;
    float glitch = step(0.98, fract(yPos + float(frame) * 0.02)) * GLITCH_AMOUNT;

    // ===== Apply effect =====
    col.rgb += grain + flicker - glitch;

    return clamp(col, 0.0, 1.0);
}}
"""
    with open(filename, "w") as f:
        f.write(content)
    print(f"Generated {filename}")
