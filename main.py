#!/usr/bin/env python3

import os
import OpenGL.GL as GL
import glfw
import numpy as np


def init_window():
    # initialisation de la librairie glfw
    glfw.init()
    # paramétrage du context opengl
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL.GL_TRUE)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    # création et parametrage de la fenêtre
    glfw.window_hint(glfw.RESIZABLE, True)  # changer en false
    window = glfw.create_window(800, 600, 'OpenGL', None, None)
    # parametrage de la fonction de gestion des évènements
    glfw.set_key_callback(window, key_callback)
    return window


def init_context(window):
    # activation du context OpenGL pour la fenêtre
    glfw.make_context_current(window)
    glfw.swap_interval(1)
    # activation de la gestion de la profondeur
    GL.glEnable(GL.GL_DEPTH_TEST)
    # choix de la couleur de fond
    GL.glClearColor(0.0, 0, 1, 1.0)
    print(f"OpenGL: {GL.glGetString(GL.GL_VERSION).decode('ascii')}")


def init_program():
    pass


def init_data():
    pass


def run(window):
    # boucle d'affichage
    i = 0
    g = 1 - i
    delta = 0.01

    while not glfw.window_should_close(window):
        # nettoyage de la fenêtre : fond et profondeur
        i, g, delta = changeColor(i, g, delta)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        #  l'affichage se fera ici

        # changement de buffer d'affichage pour éviter un effet de scintillement
        glfw.swap_buffers(window)
        # gestion des évènements
        glfw.poll_events()
        # print(glfw.get_time())


def changeColor(i, g, delta):
    i += delta
    if i >= 1:
        delta = -0.01
    if i <= 0:
        delta = 0.01
    g = 1-i
    GL.glClearColor(1, g, i, 1)
    return i, g, delta


def key_callback(win, key, scancode, action, mods):
    # sortie du programme si appui sur la touche 'echap'
    if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
        glfw.set_window_should_close(win, glfw.TRUE)


# compilation d'un shader donne ́ selon son type
def compile_shader(shader_content, shader_type):
    shader_id = GL.glCreateShader(shader_type)
    GL.glShaderSource(shader_id, shader_content)
    GL.glCompileShader(shader_id)
    success = GL.glGetShaderiv(shader_id, GL.GL_COMPILE_STATUS)
    if not success:
        log = GL.glGetShaderInfoLog(shader_id).decode('ascii')
    print(f'{25*"-"}\nError compiling shader: \n\
    {shader_content}\n{5*"-"}\n{log}\n{25*"-"}')
    return shader_id


def create_program(vertex_source, fragment_source):
    # creation d'un programme gpu
    vs_id = compile_shader(vertex_source, GL.GL_VERTEX_SHADER)
    fs_id = compile_shader(fragment_source, GL.GL_FRAGMENT_SHADER)
    if vs_id and fs_id:
        program_id = GL.glCreateProgram()
        GL.glAttachShader(program_id, vs_id)
        GL.glAttachShader(program_id, fs_id)
        GL.glLinkProgram(program_id)
        success = GL.glGetProgramiv(program_id, GL.GL_LINK_STATUS)
        if not success:
            log = GL.glGetProgramInfoLog(program_id).decode('ascii')
            print(f'{25*"-"}\nError linking program:\n{log}\n{25*"-"}')
        GL.glDeleteShader(vs_id)
        GL.glDeleteShader(fs_id)
    return program_id


def create_program_from_file(vs_file, fs_file):
    # creation d'un programme gpu a` partir de fichiers
    vs_content = open(vs_file, 'r').read() if os.path.exists(vs_file)\
        else print(f'{25*"-"}\nError reading file:\n{vs_file}\n{25*"-"}')
    fs_content = open(fs_file, 'r').read() if os.path.exists(fs_file)\
        else print(f'{25*"-"}\nError reading file:\n{fs_file}\n{25*"-"}')
    return create_program(vs_content, fs_content)


def main():
    window = init_window()
    init_context(window)
    init_program()
    init_data()
    run(window)
    glfw.terminate()


if __name__ == '__main__':
    main()
