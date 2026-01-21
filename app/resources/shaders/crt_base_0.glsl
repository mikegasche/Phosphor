//!HOOK MAIN
//!BIND HOOKED
//!DESC Phosphor CRT Effect

// ===== CRT parameters =====
const float CURVATURE_AMOUNT      = 0.0500;  // Screen curvature strength
const float CHROMA_OFFSET         = 0.0020;  // Horizontal chromatic aberration
const float VIGNETTE_STRENGTH     = 0.5000;  // Vignette intensity
const float VIGNETTE_POWER        = 1.0000;  // Vignette falloff curve

vec4 hook() {
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
}
