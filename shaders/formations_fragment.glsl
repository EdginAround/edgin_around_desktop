#version 300 es

uniform sampler2D sampler;

in highp vec4 shColor;
in highp vec2 shTexCoords;

out highp vec4 outColor;

void main(void) {
    if (shColor.a != 0.0) {
        outColor = shColor;
    } else {
        outColor = texture(sampler, shTexCoords);
    }
}

