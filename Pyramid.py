
from Entity import Entity
import math

class Pyramid(Entity):
    def mouvement(self,humain) :
        self.speed = 0.03
        vect =[humain.object.transformation.translation.x - self.object.transformation.translation.x,0,humain.object.transformation.translation.z  - self.object.transformation.translation.z]
        norm = math.sqrt(vect[0]*vect[0] + vect[2]*vect[2])
        vect_norm = [i/norm for i in vect]
        mov = [i*self.speed for i in vect_norm]
        self.object.transformation.translation.x += mov[0]
        self.object.transformation.translation.z += mov[2]
        self.bounding_box.move_BB()
    

    def destroy(self):
        self.viewer.objs_bounding_boxes.remove(self.bounding_box)
        self.viewer.objs_pyramide.remove(self)
        self.viewer.objs.remove(self)
        

    def collision(self):
        if not self.viewer.cheat_allow :
            if self.bounding_box.intersectBB(self.viewer.objs_humain.bounding_box):
                if self.viewer.objs_humain.life != 0:
                    self.viewer.objs_humain.score -= 10
                    self.viewer.text_score.value = f'score: {self.viewer.objs_humain.score}'
                    self.viewer.objs_humain.life -= 1
                    self.viewer.text_life.value = f'Vie: {int(self.viewer.objs_humain.life)}'
                    self.destroy()
                else:
                    self.viewer.text_life.value = f'Vie: {int(self.viewer.objs_humain.life)}'
                    self.destroy()
        for proj in self.viewer.objs_projectile:
            if self.bounding_box.intersectBB(proj.bounding_box):
                self.viewer.objs_humain.score += 10
                self.viewer.text_score.value = f'score: {self.viewer.objs_humain.score}'
                self.destroy()
                proj.destroy()