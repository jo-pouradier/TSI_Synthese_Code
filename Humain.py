import OpenGL.GL as GL
import pyrr
from Entity import Entity
import Arrow
import glfw
import time
import random as rand
import math


class Humain(Entity):
    def __init__(self, vie, coord, rot, obj, texture, viewer, name,vao_obj, ):
        super().__init__(vie, coord, rot, obj, texture, viewer, name,vao_obj)
        self.delta_posZ = 0.1
        self.delta_posX = 0.1
        self.timer_shoot = 1
        self.time_last_shoot = 0
        self.jumping_force = 19910
        self.weight = 75


    def destroy(self):
        glfw.set_window_should_close(self.viewer.window, glfw.TRUE)

    def shoot(self) :
        if self.time_last_shoot + self.timer_shoot <= time.time() :
            proj = Arrow.Arrow(vie=1, coord=self.object.transformation.translation, rot=[0,0,0], obj=self.viewer.dic_obj["arrow"],texture=self.viewer.dic_text["arrow"], viewer=self.viewer, name="arrow",vao_obj=self.viewer.dic_vao["arrow"])
            proj.create()
            proj.size = pyrr.Vector3([0.15, 0.15, 0.25])
            proj.object.transformation.translation.y += self.object.transformation.translation.y + 0.1
            yaw = self.viewer.cam.transformation.rotation_euler[pyrr.euler.index().yaw]
            proj.object.transformation.rotation_euler[pyrr.euler.index().yaw] = yaw
            proj.object.transformation.rotation_euler[pyrr.euler.index().roll] = math.cos(-yaw) * self.viewer.cam.transformation.rotation_euler[pyrr.euler.index().roll]
            proj.object.transformation.rotation_euler[pyrr.euler.index().pitch] = math.sin(yaw) * self.viewer.cam.transformation.rotation_euler[pyrr.euler.index().roll]
            self.viewer.objs_projectile.append(proj)
            self.time_last_shoot = time.time()
        

    def collision(self):
        for bonus in self.viewer.objs_bonus:
            if self.bounding_box.intersectBB(bonus.bounding_box):
                self.bonus(bonus)

    def bonus(self, bonus):
        self.viewer.objs_humain.score += 5
        self.viewer.text_score.value = f'score: {self.viewer.objs_humain.score}'
        
        self.destroy_bonus(bonus)
        bonus = rand.randint(0,6)
        if bonus == 0:
            self.delta_posX +=0.04
        if bonus == 1:
            self.delta_posZ +=0.04
        if bonus == 2:
            self.timer_shoot -= 0.1
        if bonus == 3:
            self.jumping_force += 1000
        if bonus == 4:
            if self.weight > 5:
                self.weight -= 5
        if bonus == 5:
            self.v_proj += 0.6
        if bonus == 6:
            if self.life < 10:
                self.life += 1
        self.update_text_character()

    def destroy_bonus(self, bonus):
        self.viewer.objs_bounding_boxes.remove(bonus.bounding_box)
        self.viewer.objs_bonus.remove(bonus)
        self.viewer.objs.remove(bonus)

    def update_text_character(self):
        V_init = self.jumping_force/self.weight * self.viewer.dt
        h= int(((0.5 * V_init**2)/self.viewer.gravity)*10)/10
        self.viewer.text_character.value = f"V: {int(self.delta_posZ * 100 * 60)/100}m/s, Vcoté: {int(self.delta_posX* 100 * 60)/100}m/s, Fire rate:{int(1/self.timer_shoot* 10)/10}/s a {int(self.v_proj*10)/10*60}m/s , saut: {-h}m"