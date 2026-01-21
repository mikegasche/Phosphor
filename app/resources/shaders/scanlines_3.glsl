//!HOOK MAIN
//!BIND HOOKED
//!DESC Scanlines Overlay

// ===== Scanline parameters =====
const float SCANLINE_DENSITY = 780.0;  // Vertical scanline frequency
const float DARK_LEVEL       = 0.82;  // Brightness of dark scanlines
const float BRIGHT_LEVEL     = 1.05;  // Brightness between scanlines
const float STRENGTH         = 1.60;  // Overall scanline intensity

vec4 hook() {
    vec4 c = HOOKED_tex(HOOKED_pos);

    // ===== Scanline pattern =====
    float scan = sin(HOOKED_pos.y * SCANLINE_DENSITY) * 0.5 + 0.5;

    // Interpolate between dark and bright regions
    float modulation = mix(DARK_LEVEL, BRIGHT_LEVEL, scan);

    // Apply scanline modulation with brightness compensation
    c.rgb *= mix(1.0, modulation, STRENGTH);

    return c;
}
