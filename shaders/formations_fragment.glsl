#version 300 es

uniform sampler2D sampler;

in highp vec2 shTexCoords;

out highp vec4 outColor;

void main(void) {
    outColor = texture(sampler, shTexCoords);
}

