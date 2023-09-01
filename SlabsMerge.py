import argparse
import numpy as np
import nibabel as nib
from scipy import ndimage

def main(args):
    image_slab_1 = nib.load(args.path_image_slab_1)
    image_1 = np.array(image_slab_1.get_fdata())
    centerline_slab_1 = nib.load(args.path_centerline_slab_1)
    centerline_1 = np.array(centerline_slab_1.get_fdata())

    image_slab_2 = nib.load(args.path_image_slab_2)
    image_2 = np.array(image_slab_2.get_fdata())
    centerline_slab_2 = nib.load(args.path_centerline_slab_2)
    centerline_2 = np.array(centerline_slab_2.get_fdata())

    slice_slab1 = args.slice_slab1
    slice_slab2 = args.slice_slab2
    factor = slice_slab2 - slice_slab1

    for i in range(slice_slab1 + 1):
        slice_slab1 = i
        slice_slab2 = i + factor
        imag_1 = image_1[:, :, slice_slab1]
        imag_2 = image_2[:, :, slice_slab2]
        x_1, y_1 = ndimage.center_of_mass(centerline_1[:, :, slice_slab1])
        x_2, y_2 = ndimage.center_of_mass(centerline_2[:, :, slice_slab2])
        x_dist, y_dist = imag_2.shape

        padding_x = int(x_2 - x_1)
        padding_y = int(y_2 - y_1)

        imag_padding = np.zeros((x_dist, y_dist))
        padding_x_new = abs(padding_x)
        padding_y_new = abs(padding_y)
	
        if padding_x >= 0 and padding_y >= 0:
            imag_padding[0:x_dist - padding_x, 0:y_dist - padding_y] = imag_2[padding_x:x_dist, padding_y:y_dist]
            image_1[:, :, i] = imag_padding
        if padding_x >= 0 and padding_y < 0:
            imag_padding[0:x_dist - padding_x, padding_y_new:y_dist] = imag_2[padding_x:x_dist, 0:y_dist - padding_y_new]
            image_1[:, :, i] = imag_padding
        if padding_x < 0 and padding_y >= 0:
            imag_padding[padding_x_new:x_dist, 0:y_dist - padding_y] = imag_2[0:x_dist - padding_x_new, padding_y:y_dist]
            image_1[:, :, i] = imag_padding
        if padding_x < 0 and padding_y < 0:
            imag_padding[padding_x_new:x_dist, padding_y_new:y_dist] = imag_2[0:x_dist - padding_x_new, 0:y_dist - padding_y_new]
            image_1[:, :, i] = imag_padding

    slab_1_2 = nib.Nifti1Image(image_1, centerline_slab_1.affine)
    nib.save(slab_1_2, args.output_path)
    print("Merge of slabs saved in ", args.output_path)
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
    	description= 
    			'::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::\n'
    			'\n'
    			'   Script to merge two Slabs by NLM, Generated on 31/08/2023 \n'
    		     	'   ***WARNING**** It is imperative that the images and their centerlines are in RPI orientation \n'
    		     	'   If you want a more accurate merge alignment, manually correct the centerlines of the first slice_slab1 and slice_slab2 slices in each slab.\n'
    		     	'\n'
    		     	'::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::\n',
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("--path_image_slab_1", required=True, help="Path to image Slab 1 (.nii.gz)")
    parser.add_argument("--path_centerline_slab_1", required=True, help="Path to SC centerline of image Slab 1 in .nii.gz (this can be calculated from sct_get_centerline) (.nii.gz) ")
    parser.add_argument("--path_image_slab_2", required=True, help="Path to image Slab 2 (.nii.gz)")
    parser.add_argument("--path_centerline_slab_2", required=True, help="Path to SC centerline of image Slab 2 in .nii.gz (this can be calculated from sct_get_centerline) (.nii.gz)")
    parser.add_argument("--slice_slab1", type=int, required=True, help="Slice index where Slab 1 ends (int)")
    parser.add_argument("--slice_slab2", type=int, required=True, help="Slice index where Slab 2 starts and is corresponding to slice_slab1 (int)")
    parser.add_argument("--output_path", required=True, help="Merge of Slab 1 and 2 (.nii.gz)")
    args = parser.parse_args()
    main(args)
