#version 330 core

// Variable de sortie (sera utilisé comme couleur)
out vec4 color;

//Un Fragment Shader minimaliste
void main (void)
{
  //Couleur du fragment
  // coloration simple
  //float r = gl_FragCoord.x/800.0; 
  //float g = gl_FragCoord.y/800.0; 
  //color = vec4(r,g,0.0,0.0); 

  //coloration "compexe" avec des lignes
  // float x=gl_FragCoord.x/800.0; 
  // float y=gl_FragCoord.y/800.0; 
  // float r=abs(cos(15.0*x+29.0*y)); 
  // float g=0.0; 
  // if(abs(cos(25.0*x*x))>0.95) {
  //   g=1.0; 
  //   }
  // else{ 
  //   g=0.0;
  //   }
  // color = vec4(r,g,0.0,0.0);

  //coloration avec cercle
  float x=gl_FragCoord.x/(800*2) - 0.5 ;  //avec ecran retina on a deux fois plus de pixel
  float y=gl_FragCoord.y/(800*2) - 0.5 ;
  float g = 1.0;
  float r = 0.0;
  if (x*x + y*y < 0.05*0.05) {
    r = 1.0;
    g = 0.0;
  }
  color = vec4(r,g,0.0,0.0);
}
