# -*- coding: utf-8 -*-

import numpy as np

import pycuda.driver as cuda

from pyfr.backends.cuda.provider import CudaKernelProvider
from pyfr.backends.cuda.queue import CudaComputeKernel
from pyfr.util import npdtype_to_ctype

class CudaPointwiseKernels(CudaKernelProvider):
    def __init__(self, backend):
        pass

    def _get_function(self, mod, func, argt, opts, nvccopts=None):
        basefn = super(CudaPointwiseKernels, self)._get_function

        # Map dtype
        nopts = {k: v for k,v in opts.items()}
        nopts['dtype'] = npdtype_to_ctype(nopts['dtype'])

        return basefn(mod, func, argt, nopts, nvccopts)

    def tdisf_inv(self, ndims, nvars, u, smats, f, gamma):
        nupts, neles = u.nrow, u.ncol / nvars
        opts = dict(dtype=u.dtype, ndims=ndims, nvars=nvars, gamma=gamma)

        fn = self._get_function('tflux_inv', 'tdisf_inv', 'iiPPPiii', opts)

        block = (256, 1, 1)
        grid = self._get_grid_for_block(block, neles)

        return self._basic_kernel(fn, grid, block, nupts, neles,
                                  u, smats, f, u.leaddim,
                                  smats.leaddim, f.leaddim)

    def tdisf_vis(self, ndims, nvars, u, smats, rcpdjac, tgradu,
                  gamma, mu, pr):
        nupts, neles = u.nrow, u.ncol / nvars
        opts = dict(dtype=u.dtype, ndims=ndims, nvars=nvars,
                    gamma=gamma, mu=mu, pr=pr)

        fn = self._get_function('tflux_vis', 'tdisf_vis', 'iiPPPPiiii', opts)

        block = (256, 1, 1)
        grid = self._get_grid_for_block(block, neles)

        return self._basic_kernel(fn, grid, block, nupts, neles,
                                  u, smats, rcpdjac, tgradu,
                                  u.leaddim, smats.leaddim,
                                  rcpdjac.leaddim, tgradu.leaddim)

    def conu_int(self, nvars, ul_vin, ur_vin, ul_vout, ur_vout, beta):
        ninters = ul_vin.ncol
        dtype = ul_vin.refdtype
        opts = dict(dtype=dtype, nvars=nvars, beta=beta)

        fn = self._get_function('conu', 'conu_int', 'iPPPPPP', opts)

        block = (256, 1, 1)
        grid = self._get_grid_for_block(block, ninters)

        return self._basic_kernel(fn, grid, block, ninters,
                                  ul_vin.mapping, ul_vin.strides,
                                  ur_vin.mapping, ur_vin.strides,
                                  ul_vout.mapping, ur_vout.mapping)

    def conu_mpi(self, nvars, ul_vin, ul_vout, ur_mpim, beta):
        ninters = ul_vin.ncol
        dtype = ul_vin.refdtype
        opts = dict(dtype=dtype, nvars=nvars, beta=beta)

        fn = self._get_function('conu', 'conu_mpi', 'iPPPP', opts)

        block = (256, 1, 1)
        grid = self._get_grid_for_block(block, ninters)

        return self._basic_kernel(fn, grid, block, ninters,
                                  ul_vin.mapping, ul_vin.strides,
                                  ul_vout.mapping, ur_mpim, beta)

    def gradcoru(self, ndims, nvars, jmats, gradu):
        nfpts, neles = jmats.nrow, gradu.ncol / nvars
        opts = dict(dtype=u.dtype, ndims=ndims, nvars=nvars)

        fn = self._get_function('gradcoru', 'gradcoru', 'iiPPii', opts)

        block = (256, 1, 1)
        grid = self._get_grid_for_block(block, neles)

        return self._basic_kernel(fn, grid, block, nfpts, neles,
                                  jmats, gradu, jmats.leaddim, gradu.leaddim)

    def rsolve_rus_inv_int(self, ndims, nvars, ul_v, ur_v, magl, magr,
                           normpnorml, gamma):
        ninters = ul_v.ncol
        dtype = ul_v.refdtype
        opts = dict(dtype=dtype, ndims=ndims, nvars=nvars, gamma=gamma)

        fn = self._get_function('rsolve_inv', 'rsolve_rus_inv_int', 'iPPPPPPP',
                                opts)

        block = (256, 1, 1)
        grid = self._get_grid_for_block(block, ninters)

        return self._basic_kernel(fn, grid, block, ninters,
                                  ul_v.mapping, ul_v.strides,
                                  ur_v.mapping, ur_v.strides,
                                  magl, magr, normpnorml)

    def rsolve_rus_inv_mpi(self, ndims, nvars, ul_mpiv, ur_mpim, magl,
                           normpnorml, gamma):
        ninters = ul_mpiv.ncol
        ul_v = ul_mpiv.view
        dtype = ul_v.refdtype
        opts = dict(dtype=dtype, ndims=ndims, nvars=nvars, gamma=gamma)

        fn = self._get_function('rsolve_inv', 'rsolve_rus_inv_mpi', 'iPPPPP',
                                opts)

        block = (256, 1, 1)
        grid = self._get_grid_for_block(block, ninters)

        return self._basic_kernel(fn, grid, block, ninters,
                                  ul_v.mapping, ul_v.strides, ur_mpim,
                                  magl, normpnorml)

    def negdivconf(self, nvars, dv, rcpdjac):
        nupts, neles = dv.nrow, dv.ncol / nvars
        opts = dict(dtype=dv.dtype, nvars=nvars)

        fn = self._get_function('negdivconf', 'negdivconf', 'iiPPii', opts)

        block = (256, 1, 1)
        grid = self._get_grid_for_block(block, neles)

        return self._basic_kernel(fn, grid, block, nupts, neles, dv, rcpdjac,
                                  dv.leaddim, rcpdjac.leaddim)
