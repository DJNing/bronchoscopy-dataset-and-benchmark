from turtle import forward

import torch
from template_FE import templateDLFE
import config
config.cfg.set_lib('loftr') 
from LoFTR_wrapper import default_cfg, LoFTR
from demo.utils import frame2tensor
import os 
import cv2
from utils_sys import Printer, is_opencv_version_greater_equal
from copy import deepcopy

class LoFTRMatcher2D():
    def __init__(self, cfg) -> None:
        self.weights_path=config.cfg.root_folder + '/thirdparty/LoFTR-MedicalData/weights/outdoor_ds.ckpt'
        if cfg is None:
            net_cfg = default_cfg
        else:
            net_cfg = cfg
        
        print(net_cfg)
        print('Loading LoFTR for matcher')
        print('===> Loading network with pretrained weights')
        self.net = LoFTR(config=net_cfg)
        if os.path.isfile(self.weights_path):
            self.net.load_state_dict(torch.load(self.weights_path)['state_dict'])
            print('==> weights successfully loaded.')
        else:
            raise FileNotFoundError('the weights file doesn\'t exist in %s' % self.weights_path)

        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        self.net = self.net.eval().to(device=self.device)

    def forward(self, data):
        pass

    # compute both keypoints and descriptors       
    def detectAndCompute(self, frame, mask=None):  # mask is a fake input 
        pass                 
            
    # return keypoints if available otherwise call detectAndCompute()    
    def detect(self, frame, mask=None):  # mask is a fake input  
        pass

    # return descriptors if available otherwise call detectAndCompute()  
    def compute(self, frame, kps=None, mask=None): # kps is a fake input, mask is a fake input
        pass

    def match(self, frame0, frame1, mask=None):
        
        pass

    def match_img(self, image_ref, image_cur, mask=None):
        '''
        @param:
            image_ref: reference image in np.array
            image_cur: reference image in np.array
            mask: image mask 
        '''

        tensor_ref = frame2tensor(self.crop_img(image_ref), self.device)
        tensor_cur = frame2tensor(self.crop_img(image_cur), self.device)
        data_dict = {
            'image0': tensor_ref,
            'image1': tensor_cur
        }
        self.net(data_dict)
        vis_range = [0, 2000] # default setting in LoFTR demo
        mkpts0 = data_dict['mkpts0_f'].cpu().numpy()[vis_range[0]:vis_range[1]]
        mkpts1 = data_dict['mkpts1_f'].cpu().numpy()[vis_range[0]:vis_range[1]]
        mconf = data_dict['mconf'].cpu().numpy()[vis_range[0]:vis_range[1]]
        # Normalize confidence.
        if len(mconf) > 0:
            conf_vis_min = 0.
            conf_max = mconf.max()
            mconf = (mconf - conf_vis_min) / (conf_max - conf_vis_min + 1e-5)
        
        return mkpts0, mkpts1, mconf

    def convert_superpts_to_keypoints(pts, size=1): 
        kps = []
        if pts is not None: 
            # convert matrix [Nx2] of pts into list of keypoints  
            if is_opencv_version_greater_equal(4,5,3):
                kps = [ cv2.KeyPoint(p[0], p[1], size=size, response=p[2]) for p in pts ]            
            else: 
                kps = [ cv2.KeyPoint(p[0], p[1], _size=size, _response=p[2]) for p in pts ]                      
        return kps  
        
    def crop_img(self, img):
        '''
        crop image to a size that can be divided by 8 to avoid error 
        '''
        h, w = img.shape
        h_res = h % 8
        w_res = w % 8
        new_img = deepcopy(img)
        new_img = new_img[0:h-h_res, 0:w-w_res]
        return new_img