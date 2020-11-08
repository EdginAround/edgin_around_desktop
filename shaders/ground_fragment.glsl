#version 300 es

const highp float fullMistDistance = 30.0;
const highp vec3 farColor = vec3(0.5, 0.5, 0.5);

in highp vec3 shColor;
in highp float shDistance;

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

    highp float ratio = min(shDistance / fullMistDistance, 1.0);
    highp vec4 color = texture(sampler, vec2(0.2 * x, 0.2 * y));
    outColor = vec4(mix(color.rgb, farColor, ratio), color.a);

    // Uncomment to see elevation
    //highp float red = length(shColor) - 100.0;
    //highp float green = 101.0 - length(shColor);
    //outColor = vec4(red, green, 0.0, 1.0);
}
