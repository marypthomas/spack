# Copyright 2013-2018 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack import *


class Groff(AutotoolsPackage):
    """Groff (GNU troff) is a typesetting system that reads
    plain text mixed with formatting commands and produces
    formatted output. Output may be PostScript or PDF, html, or
    ASCII/UTF8 for display at the terminal."""

    homepage = "https://www.gnu.org/software/groff/"
    url      = "https://ftpmirror.gnu.org/groff/groff-1.22.3.tar.gz"

    # TODO: add html variant, spack doesn't have netpbm and its too
    # complicated for me to find out at this point in time.
    # See brew scripts for groff for guidance:
    # https://github.com/Homebrew/homebrew-core/blob/master/Formula/groff.rb
    # Seems troublesome...netpbm requires groff?
    variant('pdf', default=True, description='Build the `gropdf` executable.')

    depends_on('gawk',  type='build')
    depends_on('gmake', type='build')
    depends_on('sed',   type='build')
    depends_on('ghostscript', when='+pdf')

    version('1.22.3', 'cc825fa64bc7306a885f2fb2268d3ec5')

    # https://savannah.gnu.org/bugs/index.php?43581
    # TODO: figure out why this patch does not actually work for parallel
    # builds reliably.
    # patch('gropdf.patch')
    parallel = False

    def configure_args(self):
        args = [
            "--without-x"
        ]
        return args
