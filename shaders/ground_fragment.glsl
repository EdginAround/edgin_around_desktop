#version 300 es

in highp vec3 shColor;

out highp vec4 outColor;
uniform sampler2D sampler;

void main(void) {
    //outColor = vec4(shColor, 1.0);

    highp float x;
    highp float y;
    if (shColor.x > shColor.y && shColor.x > shColor.z) {
        x = shColor.z;
        y = shColor.y;
    } else if (shColor.y > shColor.x && shColor.y > shColor.z) {
        x = shColor.x;
        y = shColor.z;
    } else {
        x = shColor.x;
        y = shColor.y;
    }

    outColor = texture(sampler, vec2(x - (x * floor(1.0 / x)), y - (y * floor(1.0 / y))));
}
