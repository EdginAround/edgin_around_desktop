#version 300 es

const highp float highlightRatio = 0.8;
const highp float fullMistDistance = 30.0;
const highp vec3 highlightColor = vec3(1.0, 1.0, 1.0);
const highp vec3 farColor = vec3(0.5, 0.5, 0.5);

flat in highp int shHighlight;
in highp vec2 shTexCoords;
in highp float shDistance;

out highp vec4 outColor;
uniform sampler2D sampler;

void main(void) {
    highp vec4 color = texture(sampler, shTexCoords);
    if (shHighlight == 1) {
        outColor = vec4(mix(color.rgb, highlightColor, highlightRatio), color.a);
    } else {
        highp float ratio = min(shDistance / fullMistDistance, 1.0);
        outColor = vec4(mix(color.rgb, farColor, ratio), color.a);
    }
}

