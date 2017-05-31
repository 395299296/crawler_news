import os

def get_files(root='./', fullpath=False, basename=False, **kwargs):
    file_list = []
    for parent, dirnames, filenames in os.walk(root):
        for x in filenames:
            basenames = os.path.splitext(x)
            if '_pre' in kwargs:
                if not basenames[0].startswith(kwargs['_pre']): continue
            if '_ext' in kwargs:
                if basenames[1] != kwargs['_ext']: continue
            if '_filter' in kwargs:
                if kwargs['_filter'] in basenames[0]: continue
            if basename:
                x = basenames[0]
            if fullpath:
                x = os.path.join(parent, x)
            file_list.append(x)

    return file_list
