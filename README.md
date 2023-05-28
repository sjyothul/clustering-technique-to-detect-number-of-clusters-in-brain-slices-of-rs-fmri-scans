# clustering-technique-to-detect-number-of-clusters-in-brain-slices-of-rs-fmri-scans
We will apply clustering techniques to detect the number of clusters in the extracted brain slices of resting state functional magnetic resonance imaging (rs-fMRI) scans.

We will be able to:
1. Perform cluster detection in the brain slices images.

We will write a python program, that takes a patient’s dataset, performs brain slice extraction on it and then detect the number of clusters present in every extracted brain slice.
There are two main parts to the process:
1. Extract the brain slices in every image.
2. Once we have the brain slices images, we will apply clustering techniques to detect the number of clusters present in every slice. To extract the noticeable big enough cluster, we only report the number of clusters whose pixel value is greater than 135 pixels.
