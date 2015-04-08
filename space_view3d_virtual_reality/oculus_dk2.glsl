uniform sampler2D bgl_RenderedTexture;
uniform float bgl_RenderedTextureWidth;
uniform float bgl_RenderedTextureHeight;
uniform float bgl_RenderedStereoEye;

const vec4 kappa = vec4(1.0,0.7,1.0,1.0);

float screen_width = bgl_RenderedTextureWidth;
float screen_height = bgl_RenderedTextureHeight;

const float scaleFactor = 0.85;

const vec2 leftCenter = vec2(0.25, 0.5);
const vec2 rightCenter = vec2(0.75, 0.5);

const float separation = -0.00;

// Scales input texture coordinates for distortion.
vec2 hmdWarp(vec2 LensCenter, vec2 texCoord, vec2 Scale, vec2 ScaleIn, float eta) {
    vec2 theta = (texCoord - LensCenter) * ScaleIn;
    float rSq = theta.x * theta.x + theta.y * theta.y;
    vec2 rvector = theta * (kappa.x + kappa.y * rSq + kappa.z * rSq * rSq + kappa.w * rSq * rSq * rSq);
    vec2 tc = LensCenter + Scale * eta * rvector;
    return tc;
}

bool validate(vec2 tc, int left_eye)
{
    //keep within bounds of texture
    if ((left_eye == 1 && (tc.x < 0.0 || tc.x > 0.5)) ||
        (left_eye == 0 && (tc.x < 0.5 || tc.x > 1.0)) ||
        tc.y < 0.0 || tc.y > 1.0) {
        return false;
    }
    return true;
}

void main()
{
    vec2 screen = vec2(screen_width, screen_height);
    vec3 eta = vec3(1.00,1.018,1.042); //refraction indices

    float as = float(screen.x / 2.0) / float(screen.y);
    vec2 Scale = vec2(0.47, as);
    vec2 ScaleIn = vec2(2.0 * scaleFactor, 1.0 / as * scaleFactor);

    vec2 texCoord = (gl_TexCoord[0].st);
    texCoord.x *= 0.5;

    if (bgl_RenderedStereoEye > 0.1)
        texCoord.x += 0.5;

    vec2 texCoordSeparated = texCoord;

    vec2 tcR = vec2(0.0);
    vec2 tcG = vec2(0.0);
    vec2 tcB = vec2(0.0);

    vec4 color = vec4(0.0);

    if (texCoord.x < 0.5) {
        texCoordSeparated.x += separation;
        tcR = hmdWarp(leftCenter, texCoordSeparated, Scale, ScaleIn, eta.r );
        tcG = hmdWarp(leftCenter, texCoordSeparated, Scale, ScaleIn, eta.g );
        tcB = hmdWarp(leftCenter, texCoordSeparated, Scale, ScaleIn, eta.b );
        color.r = texture2D(bgl_RenderedTexture, tcR).r;
        color.g = texture2D(bgl_RenderedTexture, tcG).g;
        color.b = texture2D(bgl_RenderedTexture, tcB).b;

        if (!validate(tcR, 1))
            color = vec4(0.0);
    } else {
        texCoordSeparated.x -= separation;
        tcR = hmdWarp(rightCenter, texCoordSeparated, Scale, ScaleIn, eta.r );
        tcG = hmdWarp(rightCenter, texCoordSeparated, Scale, ScaleIn, eta.g );
        tcB = hmdWarp(rightCenter, texCoordSeparated, Scale, ScaleIn, eta.b );
        color.r = texture2D(bgl_RenderedTexture, tcR).r;
        color.g = texture2D(bgl_RenderedTexture, tcG).g;
        color.b = texture2D(bgl_RenderedTexture, tcB).b;
        if (!validate(tcR, 0))
            color = vec4(0.0);
    }
    gl_FragColor = color;
}
