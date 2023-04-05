import OpenGL.GL as GL
import glfw
import pyrr
import numpy as np
from cpe3d import Object3D, Camera
import Pyramid
import math
import time
import Entity
import random as rand
 
class ViewerGL:
    def __init__(self):
        # initialisation de la librairie GLFW
        glfw.init()
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL.GL_TRUE)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.RESIZABLE, False)
        self.window = glfw.create_window(800, 800, 'Pyramid Attack', None, None)
        glfw.set_key_callback(self.window, self.key_callback)
        glfw.make_context_current(self.window)
        glfw.swap_interval(1)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glClearColor(0.5, 0.6, 0.9, 1.0)
        print(f"OpenGL: {GL.glGetString(GL.GL_VERSION).decode('ascii')}")

        self.objs = []
        self.objs_pyramide = []
        self.objs_projectile = []
        self.objs_bounding_boxes = []
        self.objs_bonus = []
        self.touch = {}
        self.objs_humain = None

        self.lock_cam = True
        self.pause = False
        self.bool_draw_bounding_boxes = False
        self.bool_caract = False

        self.timer_BB = 0.4
        self.time_last_BB = 0
        self.timer_bonus = 5
        self.time_last_bonus = 0
        self.timer_caract = 0.4
        self.time_last_caract = 0

        #gestion des vagues d'enemies
        self.nbr_pyramide = 10

        #code KONAMI
        self.cheat = 0
        self.cheat_allow = False

        # pour faire un saut de 1 metre: (voir jumpforce.py)
        self.bool_jumping = False
        self.gravity = -9.81
        self.accelerationY = self.gravity
        self.velocityY = 0
        # on part du principe qu'on a 60 fps
        self.dt = 1/60

    def run(self):
        # boucle d'affichage
        while not glfw.window_should_close(self.window):
            # nettoyage de la fenêtre : fond et profondeur
            GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
            if not self.pause:
                GL.glClearColor(0.5, 0.6, 0.9, 1.0)

                # affichage des objets
                for obj in self.objs:
                    GL.glUseProgram(obj.object.program)
                    if isinstance(obj.object, Object3D):
                        self.update_camera(obj.object.program)
                    obj.object.draw()
                self.objs_humain.bounding_box.move_BB()
                
                # mouvement des prohectiles
                for proj in self.objs_projectile :
                    proj.mov_arrow()
                # mouvement des pyramides + collisions
                for pyramid in self.objs_pyramide:
                    pyramid.mouvement(self.objs_humain)
                    pyramid.collision()

                # gestion des BoundingBox
                if self.bool_draw_bounding_boxes:
                    for bb in self.objs_bounding_boxes:
                        bb.object.draw()
                #gestion spawn pyramidE 
                self.Spawn_pyramid()

                self.update_key()
                self.gravitation()
                self.update_line()
                self.create_bonus()
                self.objs_humain.collision()
                if self.bool_caract:
                    self.text_character.draw()
                self.text_life.draw()
                self.end_game()
                self.text_score.draw()

            else:
                GL.glClearColor(0.2, 0.2, 0.2, 0.5)
                self.text_pause.draw()

            # changement de buffer d'affichage pour éviter un effet de scintillement
            glfw.swap_buffers(self.window)
            glfw.poll_events()

    def end_game(self):
        if self.objs_humain.life == 0:
            glfw.set_window_should_close(self.window, glfw.TRUE)
        else: pass


    def key_callback(self, win, key, scancode, action, mods):
        self.win = win
        # sortie du programme si appui sur la touche 'échappement'
        if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
            glfw.set_window_should_close(win, glfw.TRUE)
        if key == glfw.KEY_C and action == glfw.PRESS:
            self.lock_cam = not self.lock_cam
        if key == glfw.KEY_P and action == glfw.PRESS:
            self.pause = not self.pause
        else:
            if not self.pause:
                self.touch[key] = action

    def add_object(self, obj):
        self.objs.append(obj)

    def add_object_pyramide(self, obj):
        self.objs_pyramide.append(obj)

    def add_bounding_box(self, obj):
        self.objs_bounding_boxes.append(obj)

    def add_humain(self, obj):
        self.objs_humain = obj

    def set_camera(self, cam):
        self.cam = cam
        glfw.set_cursor_pos_callback(self.window, self.cam.cursor_pos_callback)

    def update_camera(self, prog):
        GL.glUseProgram(prog)
        loc = GL.glGetUniformLocation(prog, "translation_view")
        # Vérifie que la variable existe
        if (loc == -1):
            print("Pas de variable uniforme : translation_view")
        # Modifie la variable pour le programme courant
        translation = -self.cam.transformation.translation
        GL.glUniform4f(loc, translation.x, translation.y, translation.z, 0)
        loc = GL.glGetUniformLocation(prog, "rotation_center_view")
        if (loc == -1):
            print("Pas de variable uniforme : rotation_center_view")
        rotation_center = self.cam.transformation.rotation_center
        GL.glUniform4f(loc, rotation_center.x, rotation_center.y, rotation_center.z, 0)
        rot = pyrr.matrix44.create_from_eulers(-self.cam.transformation.rotation_euler)
        loc = GL.glGetUniformLocation(prog, "rotation_view")
        if (loc == -1):
            print("Pas de variable uniforme : rotation_view")
        GL.glUniformMatrix4fv(loc, 1, GL.GL_FALSE, rot)
        loc = GL.glGetUniformLocation(prog, "projection")
        if (loc == -1):
            print("Pas de variable uniforme : projection")
        GL.glUniformMatrix4fv(loc, 1, GL.GL_FALSE, self.cam.projection)

    def update_key(self):
        #mouvement joueur
        if glfw.KEY_W in self.touch and self.touch[glfw.KEY_W] > 0:
            self.objs_humain.object.transformation.translation += \
                pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.objs_humain.object.transformation.rotation_euler), pyrr.Vector3([0, 0, self.objs_humain.delta_posZ]))
        if glfw.KEY_S in self.touch and self.touch[glfw.KEY_S] > 0:
            self.objs_humain.object.transformation.translation -= \
                pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.objs_humain.object.transformation.rotation_euler), pyrr.Vector3([0, 0, self.objs_humain.delta_posZ]))
        if glfw.KEY_A in self.touch and self.touch[glfw.KEY_A] > 0:
            self.objs_humain.object.transformation.translation += \
                pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.objs_humain.object.transformation.rotation_euler), pyrr.Vector3([self.objs_humain.delta_posX, 0, 0]))
        if glfw.KEY_D in self.touch and self.touch[glfw.KEY_D] > 0:
            self.objs_humain.object.transformation.translation -= \
                pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.objs_humain.object.transformation.rotation_euler), pyrr.Vector3([self.objs_humain.delta_posX, 0, 0]))
        #jumping
        if glfw.KEY_SPACE in self.touch and self.touch[glfw.KEY_SPACE] > 0:
            if not self.bool_jumping:
                self.bool_jumping = True
                self.accelerationY += self.objs_humain.jumping_force/self.objs_humain.weight
        #affichage BoundingBox
        if glfw.KEY_B in self.touch and self.touch[glfw.KEY_B] > 0:
            if self.time_last_BB + self.timer_BB <= time.time():
                self.bool_draw_bounding_boxes = not self.bool_draw_bounding_boxes
                self.time_last_BB = time.time()
        #Rotation camera 3P
        if glfw.KEY_I in self.touch and self.touch[glfw.KEY_I] > 0:
            self.cam.transformation.rotation_euler[pyrr.euler.index().roll] -= 0.02
        if glfw.KEY_K in self.touch and self.touch[glfw.KEY_K] > 0:
            self.cam.transformation.rotation_euler[pyrr.euler.index().roll] += 0.02
        if glfw.KEY_J in self.touch and self.touch[glfw.KEY_J] > 0:
            self.cam.transformation.rotation_euler[pyrr.euler.index().yaw] -= 0.02
        if glfw.KEY_L in self.touch and self.touch[glfw.KEY_L] > 0:
            self.cam.transformation.rotation_euler[pyrr.euler.index().yaw] += 0.02
        # choix 1P ou 3P
        if self.lock_cam:
            self.cam.transformation.rotation_center = self.objs_humain.object.transformation.translation + self.objs_humain.object.transformation.rotation_center
            # on peut choisir l'offset lorsque l'on suit l'objet
            # 2.556
            self.cam.transformation.translation = self.objs_humain.object.transformation.translation + pyrr.Vector3([0, 0.75, 5])
        # Shoot
        if glfw.KEY_X in self.touch and self.touch[glfw.KEY_X]> 0 :
            self.objs_humain.shoot()
        if glfw.KEY_TAB in self.touch and self.touch[glfw.KEY_TAB]> 0 :
            if self.time_last_caract + self.timer_caract <= time.time():
                self.bool_caract = not self.bool_caract
                self.time_last_BB = time.time()
        state = glfw.get_mouse_button(self.window, glfw.MOUSE_BUTTON_LEFT)
        if (state == glfw.PRESS) :
            self.objs_humain.shoot()



        #test Code KONAMI
        if glfw.KEY_UP in self.touch and self.touch[glfw.KEY_UP]> 0 :
            self.cheat = 1
        if glfw.KEY_UP in self.touch and self.touch[glfw.KEY_UP]> 0 and self.cheat == 1:
            self.cheat = 2
        if glfw.KEY_DOWN in self.touch and self.touch[glfw.KEY_DOWN]> 0 and self.cheat == 2:
            self.cheat = 3
        if glfw.KEY_DOWN in self.touch and self.touch[glfw.KEY_DOWN]> 0 and self.cheat == 3:
            self.cheat = 4
        if glfw.KEY_LEFT in self.touch and self.touch[glfw.KEY_LEFT]> 0 and self.cheat == 4:
            self.cheat = 5
        if glfw.KEY_RIGHT in self.touch and self.touch[glfw.KEY_RIGHT]> 0 and self.cheat == 5:
            self.cheat = 6
        if glfw.KEY_LEFT in self.touch and self.touch[glfw.KEY_LEFT]> 0 and self.cheat == 6:
            self.cheat = 7
        if glfw.KEY_RIGHT in self.touch and self.touch[glfw.KEY_RIGHT]> 0 and self.cheat == 7:
            self.cheat = 8
        if glfw.KEY_B in self.touch and self.touch[glfw.KEY_B]> 0 and self.cheat == 8:
            self.cheat = 9
        if glfw.KEY_A in self.touch and self.touch[glfw.KEY_A]> 0 and self.cheat == 9:
            self.cheat = 0
            self.cheat_allow = True

        



    def gravitation(self):
        self.velocityY += self.accelerationY * self.dt
        X = self.objs_humain.object.transformation.translation.x
        Y = self.objs_humain.object.transformation.translation.y
        Z = self.objs_humain.object.transformation.translation.z
        #collision avec le sol
        if self.objs_humain.object.transformation.translation.y + self.velocityY * self.dt < 0.5 and not (X > 25 or X < -25) and not (Z > 25 or Z < -25) and Y > -0.5:
            self.velocityY = 0
            self.bool_jumping = False
        # en cas de chute on revient au centre de la carte
        if self.objs_humain.object.transformation.translation.y < -10:
            self.objs_humain.object.transformation.translation = pyrr.Vector3([0,0.75,0])
        # on applique la gravité 
        self.objs_humain.object.transformation.translation += \
            pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.objs_humain.object.transformation.rotation_euler), pyrr.Vector3([0, self.velocityY * self.dt, 0]))
        self.accelerationY = self.gravity

    def create_bonus(self):
        if self.time_last_bonus + self.timer_bonus <= time.time():
            x = rand.randint(0,50) - 25
            y = 0
            z = rand.randint(0,50) - 25
            cube_bonus = Entity.Entity(vie=1, coord=[x,y,z], rot=[0, 0, 0], obj=self.dic_obj["cube_bonus"],texture=self.dic_text["cube_bonus"], viewer=self, name="bonus",vao_obj = self.dic_vao["cube_bonus"])
            cube_bonus.create()
            cube_bonus.size = pyrr.Vector3([0.25, 0.25, 0.25])
            cube_bonus.bounding_box.move_BB()
            self.objs_bonus.append(cube_bonus)
            self.time_last_bonus = time.time()


    def update_line(self):
        self.objs_humain.line.object.transformation.translation = self.objs_humain.object.transformation.translation + 0.1 
        self.objs_humain.line.object.transformation.translation.x -= 0.1
        self.objs_humain.line.object.transformation.translation.z -= 0.1
        yaw = self.cam.transformation.rotation_euler[pyrr.euler.index().yaw]
        self.objs_humain.line.object.transformation.rotation_euler[pyrr.euler.index().yaw] = yaw
        self.objs_humain.line.object.transformation.rotation_euler[pyrr.euler.index().roll] = math.cos(-yaw) * self.cam.transformation.rotation_euler[pyrr.euler.index().roll]
        self.objs_humain.line.object.transformation.rotation_euler[pyrr.euler.index().pitch] = math.sin(yaw) * self.cam.transformation.rotation_euler[pyrr.euler.index().roll]

    def Spawn_pyramid(self) :
         # Spawn Pyramide
        if self.objs_pyramide == [] :
            self.nbr_pyramide += 2
            rayon = 10
            for i in range(self.nbr_pyramide):
                teta = rand.randint(0,self.nbr_pyramide*10) #*10 pour evite que des pyramide spawn au meme endroit
                pyramide = Pyramid.Pyramid(vie=1, coord=[rayon * math.cos(teta), 0, rayon * math.sin(teta)], rot=[0, 0, 0], obj=self.dic_obj["pyramid"],texture=self.dic_text["pyramid"], viewer=self, name="pyramid",vao_obj = self.dic_vao["pyramid"])
                pyramide.create()
                pyramide.size = pyrr.Vector3([0.25, 0.25, 0.25])
