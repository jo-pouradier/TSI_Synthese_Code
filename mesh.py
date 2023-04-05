#!/usr/bin/env python3

import os
import OpenGL.GL as GL
import numpy as np
from ctypes import sizeof, c_float, c_void_p
import pyrr

class Mesh():
    def __init__(self):
        self.vertices = np.array([], np.float32)
        self.faces = np.array([], np.uint32)

    def normalize(self):
        max = np.amax(self.vertices, axis=0)
        min = np.amin(self.vertices, axis=0)
        avg = (max+min)/2
        amp = np.amax(max[:3]-min[:3])/2
        self.vertices = np.array([np.concatenate((((v[:3]-avg[:3])/amp), v[3:])) for v in self.vertices], np.float32)
    
    def apply_matrix(self, m):
        vert = []
        for v in self.vertices:
            p = pyrr.Vector4(v[:3].tolist()+[1])
            p = pyrr.matrix44.apply_to_vector(m, p)[:3].astype('float32')
            v = np.array(p.tolist()+v[3:].tolist(), np.float32)
            vert.append(v)
        self.vertices = np.array(vert, np.float32)

    def load_to_gpu(self):
        # attribution d'une liste d'état (1 indique la création d'une seule liste)
        vao = GL.glGenVertexArrays(1)
        # affectation de la liste d'état courante
        GL.glBindVertexArray(vao)
        # attribution d’un buffer de donnees (1 indique la création d’un seul buffer)
        vbo = GL.glGenBuffers(1)
        # affectation du buffer courant
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, vbo)
        # copie des donnees des sommets sur la carte graphique
        GL.glBufferData(GL.GL_ARRAY_BUFFER, self.vertices, GL.GL_STATIC_DRAW)

        # les deux commandes suivantes sont stockées dans l'état du vao courant
        # activation l'utilisation des données de positions (le 0 correspond à la location dans le vertex shader)
        GL.glEnableVertexAttribArray(0)
        # indication sur le buffer courant (dernier vbo "bindé") est utilisé pour les positions des sommets
        GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, GL.GL_FALSE, sizeof(c_float())*11, None)

        GL.glEnableVertexAttribArray(1)
        GL.glVertexAttribPointer(1, 3, GL.GL_FLOAT, GL.GL_FALSE, sizeof(c_float())*11, c_void_p(sizeof(c_float())*3))

        GL.glEnableVertexAttribArray(2)
        GL.glVertexAttribPointer(2, 3, GL.GL_FLOAT, GL.GL_FALSE, sizeof(c_float())*11, c_void_p(2*sizeof(c_float())*3))

        GL.glEnableVertexAttribArray(3)
        GL.glVertexAttribPointer(3, 2, GL.GL_FLOAT, GL.GL_FALSE, sizeof(c_float())*11, c_void_p(3*sizeof(c_float())*3))

        # attribution d’un autre buffer de donnees
        vboi = GL.glGenBuffers(1)
        # affectation du buffer courant (buffer d’indice)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER,vboi)
        # copie des indices sur la carte graphique
        GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER,self.faces,GL.GL_STATIC_DRAW)
        return vao

    def get_nb_triangles(self):
        return len(self.faces)

    """only process one object containing triangular faces"""
    @staticmethod
    def load_obj(filename):
        if not os.path.exists(filename):
            print(f'{25*"-"}\nError reading file:\n{filename}\n{25*"-"}')
        m = Mesh()
        tmpv = []
        tmpvn = []
        tmpvt = []
        vi = []
        vni = []
        vti = []
        with open(filename) as f:
            for line in f: 
                l = line.split()
                if l[0] == 'v' :
                    v = np.array(l[1:], np.float32)
                    tmpv.append(v)
                elif l[0] == 'vn' :
                    vn = np.array(l[1:], np.float32)
                    tmpvn.append(vn)
                elif l[0] == 'vt' :
                    vt = np.array(l[1:], np.float32)
                    tmpvt.append(vt)
                elif l[0] == 'f' :
                    f1 = l[1].split('/')
                    f2 = l[2].split('/')
                    f3 = l[3].split('/')
                    vi.append(np.array([f1[0], f2[0], f3[0]], np.uint32))
                    if len(f3) > 1 :   
                        vti.append(np.array([f1[1], f2[1], f3[1]], np.uint32))
                    else :
                        vti.append(np.array([1, 1, 1], np.uint32))
                    if len(f3) > 2 :   
                        vni.append(np.array([f1[2], f2[2], f3[2]], np.uint32))
                    else :
                        vni.append(np.array([1, 1, 1], np.uint32))
            if len(tmpvn) == 0:
                tmpvn.append(np.array([0, 0, 0], np.float32))
            if len(tmpvt) == 0:
                tmpvt.append(np.array([0, 0], np.float32))

        vi = [i-1 for i in vi]
        vni = [i-1 for i in vni]
        vti = [i-1 for i in vti]
        dic = dict()
        tmp = []
        tmpf = []
        for v, vn, vt in zip(vi, vni, vti):
            idx = []
            for i in [0, 1, 2]:
                if (v[i], vn[i], vt[i]) in dic : 
                    idx.append(dic[(v[i], vn[i], vt[i])])
                else :
                    tmp.append(np.concatenate((tmpv[v[i]], tmpvn[vn[i]], np.array(3*[1], np.float32), tmpvt[vt[i]])))
                    dic[(v[i], vn[i], vt[i])] = len(tmp)-1
                    idx.append(dic[(v[i], vn[i], vt[i])])
            tmpf.append(np.array(idx, np.uint32))
        m.vertices = np.array(tmp, np.float32)
        m.faces = np.array(tmpf, np.uint32)
        return m
