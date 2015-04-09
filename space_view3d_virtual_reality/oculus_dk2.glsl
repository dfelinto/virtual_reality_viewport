// Oculus DK2 lens distortion shader for single eye
// shader is adapted from Oculus DK1 distortion shader by
// Lubosz Sarnecki(lubosz.wordpress.com/)

uniform sampler2D bgl_RenderedTexture;
uniform float bgl_RenderedTextureWidth;
uniform float bgl_RenderedTextureHeight;

const vec4 kappa = vec4(1.0,0.9,1.0,2.0);

float screen_width = bgl_RenderedTextureWidth;
float screen_height = bgl_RenderedTextureHeight;

const float scaleFactor = 0.83;

const vec2 lensCenter = vec2(0.5, 0.5);

// Scales input texture coordinates for distortion.
vec2 hmdWarp(vec2 texCoord, vec2 Scale, vec2 ScaleIn, float eta) {
	vec2 theta = (texCoord - lensCenter) * ScaleIn;
	float rSq = theta.x * theta.x + theta.y * theta.y;
	vec2 rvector = theta * (kappa.x + kappa.y * rSq + kappa.z * rSq * rSq + kappa.w * rSq * rSq * rSq);
	vec2 tc = lensCenter + Scale * eta * rvector;
	return tc;
}

float edges(vec2 tc)
{
	float vertL = smoothstep(0.0,0.05,tc.x);
	float vertR = smoothstep(1.0,0.95,tc.x);
	float horizL = smoothstep(0.0,0.05,tc.y);
	float horizR = smoothstep(1.0,0.95,tc.y);
	return vertL*vertR*horizL*horizR;
}


void main()
{
	vec2 screen = vec2(screen_width, screen_height);
	vec3 eta = vec3(1.00,1.018,1.042); //refraction indices

	float as = float(screen.x) / float(screen.y);
	vec2 Scale = vec2(1.0, 1.0);
	vec2 ScaleIn = vec2(scaleFactor, scaleFactor);

	vec2 texCoord = gl_TexCoord[0].st;

	vec2 tcR = vec2(0.0);
	vec2 tcG = vec2(0.0);
	vec2 tcB = vec2(0.0);

	vec4 color = vec4(0.0);

	tcR = hmdWarp(texCoord, Scale, ScaleIn, eta.r );
	tcG = hmdWarp(texCoord, Scale, ScaleIn, eta.g );
	tcB = hmdWarp(texCoord, Scale, ScaleIn, eta.b );
	color.r = texture2D(bgl_RenderedTexture, tcR*vec2(0.5,1.0)+vec2(0.25,0.0)).r;
	color.g = texture2D(bgl_RenderedTexture, tcG*vec2(0.5,1.0)+vec2(0.25,0.0)).g;
	color.b = texture2D(bgl_RenderedTexture, tcB*vec2(0.5,1.0)+vec2(0.25,0.0)).b;
	color = color * edges(tcR);

	gl_FragColor = color;
}
