# Copyright 2013-2018 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack import *


class Iceauth(AutotoolsPackage):
    """The iceauth program is used to edit and display the authorization
    information used in connecting with ICE.   It operates very much
    like the xauth program for X11 connection authentication records."""

    homepage = "http://cgit.freedesktop.org/xorg/app/iceauth"
    url      = "https://www.x.org/archive/individual/app/iceauth-1.0.7.tar.gz"

    version('1.0.7', '183e834ec8bd096ac084ad4acbc29f51')

    depends_on('libice')

    depends_on('xproto@7.0.22:', type='build')
    depends_on('pkgconfig', type='build')
    depends_on('util-macros', type='build')
