__authors__ = "Ian Goodfellow"
__copyright__ = "Copyright 2010-2012, Universite de Montreal"
__credits__ = ["Ian Goodfellow"]
__license__ = "3-clause BSD"
__maintainer__ = "Ian Goodfellow"
__email__ = "goodfeli@iro"
from pylearn2.packaged_dependencies.theano_linear.matrixmul import MatrixMul as OrigMatrixMul
from pylearn2.linear.linear_transform import LinearTransform as PL2LT
import functools
import numpy as np
from pylearn2.utils import sharedX

class MatrixMul(OrigMatrixMul):
    """ The most basic LinearTransform: matrix multiplication. See TheanoLinear
    for more documentation. """

    @functools.wraps(PL2LT.get_params)
    def get_params(self):
        return set([self._W])

def make_local_rfs(dataset, nhid, rf_shape, stride, irange = .05, draw_patches = False, rng = None):
    """
        initializes a weight matrix with local receptive fields
        param: dataset:
                the dataset defining the topology of the space (needed to convert
                    2D patches into subsets of pixels in a 1D filter vector)
               nhid: # of hidden units to make filters for
               rf_shape: 2 elem list or tuple giving topological shape of a receptive field
               stride: 2 elem list or tuple giving offset between receptive fields
               irange: if draw_patches is false, weights are initialized in U(-irange,irange)
               draw_patches: if true, weights are drawn from random examples
    """
    s = dataset.view_shape()
    height, width, channels = s
    W_img = np.zeros( (nhid, height, width, channels) )

    last_row = s[0] - rf_shape[0]
    last_col = s[1] - rf_shape[1]

    rng = np.random.RandomState([2012,07,18])


    if stride is not None:
        #local_rf_stride specified, make local_rfs on a grid
        assert last_row % stride[0] == 0
        num_row_steps = last_row / stride[0] + 1

        assert last_col % stride[1] == 0
        num_col_steps = last_col /stride[1] + 1

        total_rfs = num_row_steps * num_col_steps

        if nhid % total_rfs != 0:
            raise ValueError('nhid modulo total_rfs should be 0, but we get %d modulo %d = %d' % (nhid, total_rfs, nhid % total_rfs))

        filters_per_rf = nhid / total_rfs

        idx = 0
        for r in xrange(num_row_steps):
            rc = r * stride[0]
            for c in xrange(num_col_steps):
                cc = c * stride[1]

                for i in xrange(filters_per_rf):

                    if draw_patches:
                        img = dataset.get_batch_topo(1)[0]
                        local_rf = img[rc:rc+rf_shape[0],
                                       cc:cc+rf_shape[1],
                                       :]
                    else:
                        local_rf = rng.uniform(-irange,
                                    irange,
                                    (rf_shape[0], rf_shape[1], s[2]) )



                    W_img[idx,rc:rc+rf_shape[0],
                      cc:cc+rf_shape[1],:] = local_rf
                    idx += 1
        assert idx == nhid
    else:
        raise NotImplementedError()
        #the case below is copy-pasted from s3c and not generalized yet
        #no stride specified, use random shaped patches
        """
        assert local_rf_max_shape is not None

        for idx in xrange(nhid):
            shape = [ self.rng.randint(min_shape,max_shape+1) for
                    min_shape, max_shape in zip(
                        local_rf_shape,
                        local_rf_max_shape) ]
            loc = [ self.rng.randint(0, bound - width + 1) for
                    bound, width in zip(s, shape) ]

            rc, cc = loc

            if local_rf_draw_patches:
                img = local_rf_src.get_batch_topo(1)[0]
                local_rf = img[rc:rc+shape[0],
                               cc:cc+shape[1],
                               :]
            else:
                local_rf = self.rng.uniform(-self.irange,
                            self.irange,
                            (shape[0], shape[1], s[2]) )

            W_img[idx,rc:rc+shape[0],
                      cc:cc+shape[1],:] = local_rf
        """


    W = dataset.view_converter.topo_view_to_design_mat(W_img).T

    rval = MatrixMul(W = sharedX(W))

    return rval
