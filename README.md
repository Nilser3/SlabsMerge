# AMU7T registration 
Images crop, AMU7T registration to subject space

## Usage:

```python
python AMU7T_registration.py --path_image image.nii.gz  --mask_wm image_wm.nii.gz  --landmarks landmarks.nii.gz  --path_template_AMU7T template_AMU7T  --path_output test
```

# SlabsMerge function 
Repository for merge two slabs and register to [AMU7T template](https://github.com/spinalcordtoolbox/template_AMU7T)
![Slabs](https://github.com/Nilser3/SlabsMerge/assets/77469192/4ada80e9-dba8-4028-b8b1-36f3fc72c3fc)
## Usage:

```python

python SlabsMerge.py --path_image_slab_1 slab1/image.nii.gz --path_centerline_slab_1 slab1/centerline.nii.gz --path_image_slab_2 slab2/image.nii.gz --path_centerline_slab_2 slab2/centerline.nii.gz --slice_slab1 21 --slice_slab2 21 --output_path slabs_merged.nii.gz

```


## SlabsMerge and registration to AMU7T function usage:

```python

python SlabsMerge_reg_AMU7T.py --path_image_slab_1 slab1/image.nii.gz --mask_wm_slab_1 slab1/wm_mask.nii.gz --path_centerline_slab_1 slab1/centerline.nii.gz --path_image_slab_2 slab2/image.nii.gz --mask_wm_slab_2 slab2/wm_mask.nii.gz --path_centerline_slab_2 slab2/centerline.nii.gz --slice_slab1 21 --slice_slab2 21 --landmarks landmarks.nii.gz --path_template_AMU7T template_AMU7T --path_output Registration_AMU7T

```
