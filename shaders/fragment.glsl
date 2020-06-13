#version 300 es

in highp vec3 shColor;

out highp vec4 outColor;

void main(void) {
    outColor = vec4(shColor, 1.0);
}
