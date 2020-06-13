#version 300 es

uniform mat4 uniProj;
uniform mat4 uniView;

in vec3 inPosition;

out highp vec3 shColor;

void main(void) {
    gl_Position = uniProj * uniView * vec4(inPosition, 1);
    shColor = 0.5 * (inPosition + vec3(1, 1, 1));
}
