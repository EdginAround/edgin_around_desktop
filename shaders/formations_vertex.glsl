#version 300 es

uniform mat4 uniView;

layout(location = 0) in vec3 inPosition;
layout(location = 1) in vec4 inColor;
layout(location = 2) in vec2 inTexCoords;

out highp vec4 shColor;
out highp vec2 shTexCoords;

void main(void) {
    gl_Position = uniView * vec4(inPosition, 1);

    shColor = inColor;
    shTexCoords = inTexCoords;
}

