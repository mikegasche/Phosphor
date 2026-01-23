#!/usr/bin/env python3
from pathlib import Path

# Underlying values for CRT
BASE_PARAMS = {
    "CURVATURE_AMOUNT": 0.05,   # Screen curvature strength
    "CHROMA_OFFSET": 0.002,     # Horizontal chromatic aberration
    "VIGNETTE_STRENGTH": 0.5,   # Vignette intensity
    "VIGNETTE_POWER": 1.0       # Vignette falloff
}

# Scale -5 to +5
SCALE = list(range(-5, 6))

SHADER_DIR = Path("../../shaders")
SHADER_DIR.mkdir(parents=True, exist_ok=True)

for i in SCALE:
    if i == 0:
        filename = SHADER_DIR / "crt_base_0.glsl"
    else:
        filename = SHADER_DIR / f"crt_base_{i}.glsl"

    # Scaling: +/-20% per level
    curvature = BASE_PARAMS["CURVATURE_AMOUNT"] * (1 + 0.2 * i)
    chroma = BASE_PARAMS["CHROMA_OFFSET"] * (1 + 0.2 * i)
    vignette_strength = min(max(BASE_PARAMS["VIGNETTE_STRENGTH"] * (1 + 0.15 * i), 0.0), 1.0)
    vignette_power = max(BASE_PARAMS["VIGNETTE_POWER"] * (1 + 0.1 * i), 0.1)

    content = f"""//!HOOK MAIN
//!BIND HOOKED
//!DESC Phosphor CRT Effect

// ===== CRT parameters =====
const float CURVATURE_AMOUNT      = {curvature:.4f};  // Screen curvature strength
const float CHROMA_OFFSET         = {chroma:.4f};  // Horizontal chromatic aberration
const float VIGNETTE_STRENGTH     = {vignette_strength:.4f};  // Vignette intensity
const float VIGNETTE_POWER        = {vignette_power:.4f};  // Vignette falloff curve

vec4 hook() {{
    vec2 uv = HOOKED_pos;

    // ===== Screen curvature =====
    vec2 n = uv * 2.0 - 1.0;
    n.x *= 1.0 + CURVATURE_AMOUNT * (n.y * n.y);
    n.y *= 1.0 + CURVATURE_AMOUNT * (n.x * n.x);
    vec2 cuv = (n + 1.0) * 0.5;

    // ===== Chromatic aberration =====
    float r = HOOKED_texOff(cuv + vec2( CHROMA_OFFSET, 0.0)).r;
    float g = HOOKED_tex(cuv).g;
    float b = HOOKED_texOff(cuv + vec2(-CHROMA_OFFSET, 0.0)).b;
    vec3 col = vec3(r, g, b);

    // ===== Vignette =====
    float dist = distance(uv, vec2(0.5));
    float vignette = pow(1.0 - dist, VIGNETTE_POWER);
    col *= mix(1.0, vignette, VIGNETTE_STRENGTH);

    return vec4(col, 1.0);
}}
"""
    with open(filename, "w") as f:
        f.write(content)
    print(f"Generated {filename}")
