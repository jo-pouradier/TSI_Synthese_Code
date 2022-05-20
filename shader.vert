#version 330 core

// Variable d'entrée, ici la position
layout (location = 0) in vec3 position;
uniform vec4 translation;

//Un Vertex Shader minimaliste
void main (void)
{
  //Coordonnees du sommet
  gl_Position = vec4(position,1.0);
  // gl_Position.x/=2;

  // vec4 p=vec4(position, 1.0);
  // p.x=p.x*0.3;
  // p+=vec4(-0.7,-0.8,0.0,0.0);
  // gl_Position = p;
  gl_Position+= translation;
}