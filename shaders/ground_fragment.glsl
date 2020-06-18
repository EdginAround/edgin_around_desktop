#version 300 es

in highp vec3 shColor;

out highp vec4 outColor;
uniform sampler2D sampler;

void main(void) {
    highp float x = abs(shColor.x);
    highp float y = abs(shColor.y);
    highp float z = abs(shColor.z);
    if (x > y && x > z) {
        x = shColor.z;
        y = shColor.y;
    } else if (y > x && y > z) {
        x = shColor.x;
        y = shColor.z;
    } else {
        x = shColor.x;
        y = shColor.y;
    }

    outColor = texture(sampler, vec2(0.2 * x, 0.2 * y));

    // Uncomment to see elevation
    //highp float red = length(shColor) - 100.0;
    //highp float green = 101.0 - length(shColor);
    //outColor = vec4(red, green, 0.0, 1.0);
}
