from viewerGL import ViewerGL
import glutils
from mesh import Mesh
from cpe3d import Camera, Text
import numpy as np
from Entity import Entity
import Humain
import math
import pyrr

def main():
    viewer = ViewerGL()

    # Cam
    cam = Camera(viewer)
    viewer.set_camera(cam)
    viewer.cam.transformation.translation.y = 1
    viewer.cam.transformation.rotation_center = viewer.cam.transformation.translation.copy()

    viewer.program3d_id = glutils.create_program_from_file('vert/shader.vert', 'frag/shader.frag')
    viewer.programGUI_id = glutils.create_program_from_file('vert/gui.vert', 'frag/gui.frag')

    dic_text = {}
    dic_obj = {}
    dic_vao = {}

    #------------------------ Chargements des textures + objs ----------------------------

    dic_text["pyramid"] = glutils.load_texture("Textures/architecture.jpg")
    dic_text["sol"] = glutils.load_texture("Textures/TextureSand.jpeg")
    dic_text["humain"] = glutils.load_texture("Textures/multicolor.png")
    dic_text["cube"] = glutils.load_texture("Textures/cube.png")
    dic_text["arrow"] = dic_text["humain"]
    dic_text["line"] = dic_text["humain"]
    dic_text["cube_bonus"] = glutils.load_texture("Textures/bloc_mario.png")

    dic_obj["pyramid"] = Mesh.load_obj("Textures/pyramid.obj")
    dic_obj["pyramid"].normalize()
    dic_obj["pyramid"].apply_matrix(pyrr.matrix44.create_from_scale([0.25, 0.25, 0.25, 1]))

    dic_obj["humain"] = Mesh.load_obj("Textures/homme.obj")
    dic_obj["humain"].normalize()
    dic_obj["humain"].apply_matrix(pyrr.matrix44.create_from_scale([0.5, 0.5, 0.5, 1]))
   
    #bounding_box
    dic_obj["cube_pyramid"] = Mesh.load_obj("Textures/cube.obj")
    dic_obj["cube_pyramid"].normalize()
    dic_obj["cube_pyramid"].apply_matrix(pyrr.matrix44.create_from_scale([0.25, 0.25, 0.25, 1]))
    dic_obj["cube_humain"] = Mesh.load_obj("Textures/cube.obj")
    dic_obj["cube_humain"].normalize()
    dic_obj["cube_humain"].apply_matrix(pyrr.matrix44.create_from_scale([0.2, 0.5, 0.2, 1]))
    dic_obj["cube_arrow"] = Mesh.load_obj("Textures/cube.obj")
    dic_obj["cube_arrow"].normalize()
    dic_obj["cube_arrow"].apply_matrix(pyrr.matrix44.create_from_scale([0.15, 0.15, 0.25, 1]))
    dic_obj["line"] = Mesh.load_obj("Textures/cube.obj")
    dic_obj["line"].normalize()
    dic_obj["line"].apply_matrix(pyrr.matrix44.create_from_scale([0.006, 0.006, 20, 1]))
    dic_obj["cube_bonus"] = Mesh.load_obj("Textures/cube.obj")
    dic_obj["cube_bonus"].normalize()
    dic_obj["cube_bonus"].apply_matrix(pyrr.matrix44.create_from_scale([0.25, 0.25, 0.25, 1]))

    dic_obj["arrow"] = Mesh.load_obj("Textures/arrow.obj")
    dic_obj["arrow"].normalize()
    dic_obj["arrow"].apply_matrix(pyrr.matrix44.create_from_scale([1, 1, 0.15, 1]))

    #chargement sol
    m = Mesh()
    p0, p1, p2, p3 = [-25, 0, -25], [25, 0, -25], [25, 0, 25], [-25, 0, 25]
    n, c = [0, 1, 0], [1, 1, 1]
    t0, t1, t2, t3 = [0, 0], [1, 0], [1, 1], [0, 1]
    m.vertices = np.array([[p0 + n + c + t0], [p1 + n + c + t1],[p2 + n + c + t2], [p3 + n + c + t3]], np.float32)
    m.faces = np.array([[0, 1, 2], [0, 2, 3]], np.uint32)
    dic_obj["sol"] = m

    for i in dic_obj :
        dic_vao[i] = dic_obj[i].load_to_gpu()

    viewer.dic_obj = dic_obj
    viewer.dic_text = dic_text
    viewer.dic_vao = dic_vao

    #------------------------Fin Chargements des textures + objs ---------------------------

    # humain
    humain = Humain.Humain(vie=10, coord=[0,0, 0], rot=[0, 0, 0], obj=dic_obj["humain"],texture=dic_text["humain"], viewer=viewer, name="humain",vao_obj=dic_vao["humain"])
    humain.create()
    humain.size = pyrr.Vector3([0.2, 0.5, 0.2])
    humain.v_proj = 0.2
    humain.object.transformation.rotation_euler[pyrr.euler.index().yaw] = math.pi # il faut mettre l'humain a l'endroit
    
    # Sol
    sol  = Entity(vie=1, coord=[0,0,0], rot=[0,math.pi/2,math.pi/2], obj=dic_obj["sol"],texture=dic_text["sol"],viewer=viewer,vao_obj = dic_vao["sol"],name="sol")
    sol.create()
   
    #Test "line"
    line = Entity(vie = 1, coord=[0,0,0], rot=[0,0,math.pi/2], obj=dic_obj["line"],texture=dic_text["line"],viewer=viewer, vao_obj = dic_vao["line"],name="line")
    line.create()
    line.object.transformation.rotation_euler[pyrr.euler.index().roll] = math.pi/2
    humain.line = line
    
    # Text Pause
    vao_obj = Text.initalize_geometry()
    texture = glutils.load_texture('Textures/fontB2.png')
    text_pause = Text('Pause', np.array([-0.8, 0.3], np.float32), np.array([0.8, 0.8], np.float32), vao_obj, 2, viewer.programGUI_id, texture)
    viewer.text_pause = text_pause

    # Text vie du joueur
    vao_obj = Text.initalize_geometry()
    texture = glutils.load_texture('Textures/fontB2.png')
    text_life = Text(f'Vie: {humain.life}', np.array([-0.95, -0.95], np.float32), np.array([-0.65, -0.85], np.float32), vao_obj, 2, viewer.programGUI_id, texture)
    viewer.text_life = text_life
   
    # Text charactéristique joueur
    vao_obj = Text.initalize_geometry()
    texture = glutils.load_texture('Textures/fontB2.png')
    V_init = humain.jumping_force/humain.weight * viewer.dt
    h= int(((0.5 * V_init**2)/viewer.gravity) *10) /10
    text_character = Text(f"V: {int(humain.delta_posZ * 100)/100 * 60}m/s, Vcoté: {int(humain.delta_posX* 100)/100*60}m/s, Fire rate:{int(1/humain.timer_shoot* 10)/10}/s a {int(humain.v_proj*10)/10*60}m/s , saut: {-h}m",
        np.array([-0.95, 0.85], np.float32), np.array([0.95, 0.9], np.float32), vao_obj, 2, viewer.programGUI_id, texture)
    viewer.text_character = text_character

    # Text score du joueur
    humain.score = 0
    vao_obj = Text.initalize_geometry()
    texture = glutils.load_texture('Textures/fontB2.png')
    text_score = Text(f'score: {humain.score}', np.array([0.62, -0.95], np.float32), np.array([0.95, -0.85], np.float32), vao_obj, 2, viewer.programGUI_id, texture)
    viewer.text_score = text_score

    viewer.run()


if __name__ == '__main__':
    main()
