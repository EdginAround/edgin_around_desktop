#version 300 es

uniform mat4 uniProj;
uniform mat4 uniView;

layout(location = 0) in vec3 inPosition;

out highp vec3 shColor;

void main(void) {
    gl_Position = uniProj * uniView * vec4(inPosition, 1);
    shColor = inPosition + vec3(100, 100, 100);
}
