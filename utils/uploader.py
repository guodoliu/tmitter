# -*- coding: utf-8 -*-
# ## ## ## ## ## ## ## ## ##
# upload file library
# ## ## ## ## ## ## ## ## ##
import time
from PIL import Image
from tmitter.settings import *


def upload_face(data):
    """
    summary: upload user face
    """
    _state = {
        'success': False,
        'message': '',
    }

    if data.size() > 0:
        base_im = Image.open(data)

        size16 = (16, 16)
        size24 = (24, 24)
        size32 = (32, 32)
        size100 = (75, 75)

        size_array = (size100, size32, size24, size16)

        # genrate file name and the file path
        file_name = time.strftime('%H%M%S') + '.png'
        file_root_path = '%sface/' %(MEDIA_ROOT)
        file_sub_path = '%s' %(str(time.strftime("%Y/%m/%d/")))

        # make different sizes photos
        for size in size_array:
            file_middle_path = '%d/' %size[0]
            file_path = os.path.abspath(file_root_path + file_middle_path + file_sub_path)

            im = base_im
