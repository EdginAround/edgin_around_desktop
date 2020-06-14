#version 300 es

flat in highp int shHighlight;
in highp vec2 shTexCoords;

out highp vec4 outColor;
uniform sampler2D sampler;

void main(void) {
    highp vec4 color = texture(sampler, shTexCoords);
    if (shHighlight == 1) {
        outColor = vec4(0.8 * color.xyz + 0.2 * vec3(1.0, 1.0, 1.0), color.a);
    } else {
        outColor = color;
    }
}

