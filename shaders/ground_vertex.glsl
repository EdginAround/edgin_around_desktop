#version 300 es

uniform mat4 uniView;

layout(location = 0) in vec3 inPosition;

out highp vec3 shColor;
out highp float shDistance;

void main(void) {
    gl_Position = uniView * vec4(inPosition, 1);
    shColor = inPosition;
    shDistance = length(gl_Position.xyz);
}
