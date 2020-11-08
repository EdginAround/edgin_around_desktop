#version 300 es

uniform mat4 uniModel;
uniform mat4 uniView;
uniform int uniHighlight;

layout(location = 0) in vec3 inPosition;
layout(location = 1) in vec2 inTexCoords;

flat out highp int shHighlight;
out highp vec2 shTexCoords;
out highp float shDistance;

void main(void) {
    gl_Position = uniView * uniModel * vec4(inPosition, 1);
    shHighlight = uniHighlight;
    shTexCoords = inTexCoords;
    shDistance = length(gl_Position.xyz);
}

