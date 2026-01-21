//!HOOK MAIN
//!BIND HOOKED
//!DESC VHS: dynamic grain + horizontal glitch

// ===== VHS parameters =====
const float GRAIN_STRENGTH   = 0.0540;  // Pixel noise intensity
const float FLICKER_STRENGTH = 0.0180;  // Frame-based brightness flicker
const float LINE_DENSITY     = 10.0;  // Number of horizontal glitch lines
const float GLITCH_AMOUNT    = 0.0360;  // Horizontal glitch displacement strength

vec4 hook() {
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
}
