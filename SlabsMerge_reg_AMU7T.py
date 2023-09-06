import argparse
import numpy as np
import nibabel as nib
import os 
from scipy import ndimage

def main(args):
    image_slab_1 = nib.load(args.path_image_slab_1)
    image_1 = np.array(image_slab_1.get_fdata())  
    wm_slab_1 = nib.load(args.mask_wm_slab_1)
    im_wm_1 = np.array(wm_slab_1.get_fdata())
    centerline_slab_1 = nib.load(args.path_centerline_slab_1)
    centerline_1 = np.array(centerline_slab_1.get_fdata())

    image_slab_2 = nib.load(args.path_image_slab_2)
    image_2 = np.array(image_slab_2.get_fdata())
    wm_slab_2 = nib.load(args.mask_wm_slab_2)
    im_wm_2 = np.array(wm_slab_2.get_fdata())
    centerline_slab_2 = nib.load(args.path_centerline_slab_2)
    centerline_2 = np.array(centerline_slab_2.get_fdata())

    slice_slab1 = args.slice_slab1
    slice_slab2 = args.slice_slab2
    factor = slice_slab2 - slice_slab1
    
    # Merge IMAGE and WM mask in slab 1 space
    for i in range(slice_slab1 + 1):
        slice_slab1 = i
        slice_slab2 = i + factor
        imag_1 = image_1[:, :, slice_slab1]
        imag_2 = image_2[:, :, slice_slab2]
        wm_1 = im_wm_1[:, :, slice_slab1]
        wm_2 = im_wm_2[:, :, slice_slab2]
        x_1, y_1 = ndimage.center_of_mass(centerline_1[:, :, slice_slab1])
        x_2, y_2 = ndimage.center_of_mass(centerline_2[:, :, slice_slab2])
        x_dist, y_dist = imag_2.shape

        padding_x = int(x_2 - x_1)
        padding_y = int(y_2 - y_1)

        imag_padding = np.zeros((x_dist, y_dist))
        wm_padding = np.zeros((x_dist, y_dist))
        padding_x_new = abs(padding_x)
        padding_y_new = abs(padding_y)
	
        if padding_x >= 0 and padding_y >= 0:
            imag_padding[0:x_dist - padding_x, 0:y_dist - padding_y] = imag_2[padding_x:x_dist, padding_y:y_dist]
            image_1[:, :, i] = imag_padding
            wm_padding[0:x_dist - padding_x, 0:y_dist - padding_y] = wm_2[padding_x:x_dist, padding_y:y_dist]
            im_wm_1[:, :, i] = wm_padding
        if padding_x >= 0 and padding_y < 0:
            imag_padding[0:x_dist - padding_x, padding_y_new:y_dist] = imag_2[padding_x:x_dist, 0:y_dist - padding_y_new]
            image_1[:, :, i] = imag_padding
            wm_padding[0:x_dist - padding_x, padding_y_new:y_dist] = wm_2[padding_x:x_dist, 0:y_dist - padding_y_new]
            im_wm_1[:, :, i] = wm_padding
        if padding_x < 0 and padding_y >= 0:
            imag_padding[padding_x_new:x_dist, 0:y_dist - padding_y] = imag_2[0:x_dist - padding_x_new, padding_y:y_dist]
            image_1[:, :, i] = imag_padding
            wm_padding[padding_x_new:x_dist, 0:y_dist - padding_y] = wm_2[0:x_dist - padding_x_new, padding_y:y_dist]
            im_wm_1[:, :, i] = wm_padding
        if padding_x < 0 and padding_y < 0:
            imag_padding[padding_x_new:x_dist, padding_y_new:y_dist] = imag_2[0:x_dist - padding_x_new, 0:y_dist - padding_y_new]
            image_1[:, :, i] = imag_padding
            wm_padding[padding_x_new:x_dist, padding_y_new:y_dist] = wm_2[0:x_dist - padding_x_new, 0:y_dist - padding_y_new]
            im_wm_1[:, :, i] = wm_padding

    path = os.path.join(args.path_output)
    os.mkdir(path)

    slab_1_2 = nib.Nifti1Image(image_1, centerline_slab_1.affine)
    nib.save(slab_1_2, f"{args.path_output}/image_merged.nii.gz")
    wm_1_2 = nib.Nifti1Image(im_wm_1, centerline_slab_1.affine)
    nib.save(wm_1_2, f"{args.path_output}/wm_mask_merged.nii.gz")
    print("Slabs merged saved in : ", args.path_output)
    
    # Crop IMAGE and WM mask with 10 pixels dilation of WM mask
    comand_1 = f"sct_crop_image -i {args.path_output}/image_merged.nii.gz -m {args.path_output}/wm_mask_merged.nii.gz  -dilate 10x10x0 -o {args.path_output}/image_merged_crop.nii.gz"
    os.system(comand_1)
    comand_2 = f"sct_crop_image -i {args.path_output}/wm_mask_merged.nii.gz -m {args.path_output}/wm_mask_merged.nii.gz  -dilate 10x10x0 -o {args.path_output}/wm_mask_merged_crop.nii.gz"
    os.system(comand_2)
    # Registration of AMU7T template to subject space
    comand_3 = f"sct_register_to_template -i {args.path_output}/image_merged_crop.nii.gz -s {args.path_output}/wm_mask_merged_crop.nii.gz -l {args.landmarks} -c t1 -v 1 -s-template-id 4  -t {args.path_template_AMU7T}  -param step=1,type=imseg,algo=centermassrot,rot_method=pcahog:step=2,type=seg,algo=bsplinesyn,slicewise=0,metric=MeanSquares,samplStrategy=None,samplPercent=0.2,iter=2,smooth=1,rot_method=pcahog:step=3,type=seg,algo=syn,metric=MeanSquares,shrink=2,dof=Tz_Rz_Sz,slicewise=1,iter=20 -ref subject -ofolder {args.path_output}"
    os.system(comand_3)
    # Registration of AMU7T atlas to subject space
    comand_4 = f"sct_apply_transfo -i {args.path_template_AMU7T}/atlas/AMU7T_50_labels.nii.gz -d {args.path_output}/image_merged_crop.nii.gz  -w {args.path_output}/warp_template2anat.nii.gz -o {args.path_output}/labels_AMU7T2anat.nii.gz -x nn"
    os.system(comand_4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
    	description= 
    	'::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::\n'
    	'\n'
    	'Script to merge two Slabs, crop and registration to AMU7T template. \n'
    	'If you want a more accurate merge alignment, manually correct the centerlines of each slab. \n'
        'WM segmentations must be present only in the slices to be merged of each slab. \n'
    	'This script applies SCT command lines: sct_crop_image, sct_register_to_template and sct_apply_transfo. \n'
        'by NLM ---------------------- Version 06/09/2023 \n'
    	'\n'
        '*** WARNING **** It is imperative that the images and their centerlines are in RPI orientation \n'
        '\n'
    	'::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::\n',
        formatter_class=argparse.RawTextHelpFormatter )
        
    parser.add_argument("--path_image_slab_1", required=True, help="Path to image Slab 1 (.nii.gz)")
    parser.add_argument("--mask_wm_slab_1", required=True, help="Path to wm mask of Slab 1 (.nii.gz)")
    parser.add_argument("--path_centerline_slab_1", required=True, help="Path to SC centerline of image Slab 1 in .nii.gz (this can be calculated from sct_get_centerline) (.nii.gz) ")
    parser.add_argument("--path_image_slab_2", required=True, help="Path to image Slab 2 (.nii.gz)")
    parser.add_argument("--mask_wm_slab_2", required=True, help="Path to wm mask of Slab 2 (.nii.gz)")
    parser.add_argument("--path_centerline_slab_2", required=True, help="Path to SC centerline of image Slab 2 in .nii.gz (this can be calculated from sct_get_centerline) (.nii.gz)")
    parser.add_argument("--slice_slab1", type=int, required=True, help="Slice index where Slab 1 ends (int)")
    parser.add_argument("--slice_slab2", type=int, required=True, help="Slice index where Slab 2 starts and is corresponding to slice_slab1 (int)")   
    parser.add_argument("--landmarks", required=True, help="Path to landmarks in Slab 1 space, C2 and C5 are recommended (.nii.gz)")
    parser.add_argument("--path_template_AMU7T", required=True, help="Path to AMU7T template")
    parser.add_argument("--path_output", required=True, help="Path output folder")
    args = parser.parse_args()
    main(args)    
