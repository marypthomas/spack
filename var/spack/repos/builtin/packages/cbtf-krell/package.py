# Copyright 2013-2018 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack import *
import spack
import spack.store


class CbtfKrell(CMakePackage):
    """CBTF Krell project contains the Krell Institute contributions to the
       CBTF project.  These contributions include many performance data
       collectors and support libraries as well as some example tools
       that drive the data collection at HPC levels of scale.
    """
    homepage = "http://sourceforge.net/p/cbtf/wiki/Home/"
    git      = "https://github.com/OpenSpeedShop/cbtf-krell.git"

    version('develop', branch='master')
    version('1.9.2', branch='1.9.2')
    version('1.9.1.2', branch='1.9.1.2')
    version('1.9.1.1', branch='1.9.1.1')
    version('1.9.1.0', branch='1.9.1.0')

    # MPI variants
    variant('openmpi', default=False,
            description="Build mpi experiment collector for openmpi MPI..")
    variant('mpt', default=False,
            description="Build mpi experiment collector for SGI MPT MPI.")
    variant('mvapich2', default=False,
            description="Build mpi experiment collector for mvapich2 MPI.")
    variant('mvapich', default=False,
            description="Build mpi experiment collector for mvapich MPI.")
    variant('mpich2', default=False,
            description="Build mpi experiment collector for mpich2 MPI.")
    variant('mpich', default=False,
            description="Build mpi experiment collector for mpich MPI.")
    variant('runtime', default=False,
            description="build only the runtime libraries and collectors.")
    variant('build_type', default='None', values=('None'),
            description='CMake build type')
    variant('cti', default=False,
            description="Build MRNet with the CTI startup option")
    variant('crayfe', default=False,
            description="build only the FE tool using the runtime_dir \
                         to point to target build.")

    # Dependencies for cbtf-krell
    depends_on("cmake@3.0.2:", type='build')

    # For binutils
    depends_on("binutils")

    # For boost
    depends_on("boost@1.66.0:")

    # For Dyninst
    depends_on("dyninst@develop", when='@develop')
    depends_on("dyninst@10:", when='@1.9.1.0:9999')

    # For MRNet
    depends_on("mrnet@5.0.1-3:+cti", when='@develop+cti', type=('build', 'link', 'run'))
    depends_on("mrnet@5.0.1-3:+lwthreads", when='@develop', type=('build', 'link', 'run'))

    depends_on("mrnet@5.0.1-3+cti", when='@1.9.1.0:9999+cti', type=('build', 'link', 'run'))
    depends_on("mrnet@5.0.1-3+lwthreads", when='@1.9.1.0:9999', type=('build', 'link', 'run'))

    # For Xerces-C
    depends_on("xerces-c")

    # For CBTF
    depends_on("cbtf@develop", when='@develop', type=('build', 'link', 'run'))
    depends_on("cbtf@1.9.1.0:9999", when='@1.9.1.0:9999', type=('build', 'link', 'run'))

    # For CBTF with cti
    depends_on("cbtf@develop+cti", when='@develop+cti', type=('build', 'link', 'run'))
    depends_on("cbtf@1.9.1.0:9999+cti", when='@1.9.1.0:9999+cti', type=('build', 'link', 'run'))

    # For CBTF with runtime
    depends_on("cbtf@develop+runtime", when='@develop+runtime', type=('build', 'link', 'run'))
    depends_on("cbtf@1.9.1.0:9999+runtime", when='@1.9.1.0:9999+runtime', type=('build', 'link', 'run'))

    # for services and collectors
    depends_on("libmonitor@2013.02.18+krellpatch")

    depends_on("libunwind", when='@develop')
    depends_on("libunwind@1.2.1", when='@1.9.1.0:9999')

    depends_on("papi@5.4.1:")

    depends_on("llvm-openmp-ompt@tr6_forwards+standalone")

    # MPI Installations
    depends_on("openmpi", when='+openmpi')
    depends_on("mpich", when='+mpich')
    depends_on("mpich2", when='+mpich2')
    depends_on("mvapich2", when='+mvapich2')
    depends_on("mvapich", when='+mvapich')
    depends_on("mpt", when='+mpt')

    depends_on("python", when='@develop', type=('build', 'run'))
    depends_on("python@2.7.14:2.7.15", when='@2.3.1.3:9999', type=('build', 'run'))

    depends_on("gotcha")

    parallel = False

    build_directory = 'build_cbtf_krell'

    def set_rt_only_cmake_options(self, spec, cmake_options):
        # Appends to cmake_options the options that will enable the appropriate
        # MPI implementations

        rt_only_options = []
        rt_only_options.append('-DRUNTIME_ONLY=true')
        cmake_options.extend(rt_only_options)

    def set_mpi_cmake_options(self, spec, cmake_options):
        # Appends to cmake_options the options that will enable the appropriate
        # MPI implementations

        mpi_options = []

        # openmpi
        if spec.satisfies('+openmpi'):
            mpi_options.append('-DOPENMPI_DIR=%s' % spec['openmpi'].prefix)
        # mpich
        if spec.satisfies('+mpich'):
            mpi_options.append('-DMPICH_DIR=%s' % spec['mpich'].prefix)
        # mpich2
        if spec.satisfies('+mpich2'):
            mpi_options.append('-DMPICH2_DIR=%s' % spec['mpich2'].prefix)
        # mvapich
        if spec.satisfies('+mvapich'):
            mpi_options.append('-DMVAPICH_DIR=%s' % spec['mvapich'].prefix)
        # mvapich2
        if spec.satisfies('+mvapich2'):
            mpi_options.append('-DMVAPICH2_DIR=%s' % spec['mvapich2'].prefix)
        # mpt
        if spec.satisfies('+mpt'):
            mpi_options.append('-DMPT_DIR=%s' % spec['mpt'].prefix)

        cmake_options.extend(mpi_options)

    def set_cray_login_node_cmake_options(self, spec, cmake_options):
        # Appends to cmake_options the options that will enable
        # the appropriate Cray login node libraries

        cray_login_node_options = []
        rt_platform = "cray"
        # How do we get the compute node (CNL) cbtf package
        # install directory path. spec['cbtf'].prefix is the
        # login node path for this build, as we are building
        # the login node components with this spack invocation. We
        # need these paths to be the ones created in the CNL
        # spack invocation.
        be_cbtf = spack.store.db.query_one('cbtf arch=cray-CNL-haswell')
        be_cbtfk = spack.store.db.query_one('cbtf-krell arch=cray-CNL-haswell')
        be_papi = spack.store.db.query_one('papi arch=cray-CNL-haswell')
        be_boost = spack.store.db.query_one('boost arch=cray-CNL-haswell')
        be_mont = spack.store.db.query_one('libmonitor arch=cray-CNL-haswell')
        be_unw = spack.store.db.query_one('libunwind arch=cray-CNL-haswell')
        be_xer = spack.store.db.query_one('xerces-c arch=cray-CNL-haswell')
        be_dyn = spack.store.db.query_one('dyninst arch=cray-CNL-haswell')
        be_mrnet = spack.store.db.query_one('mrnet arch=cray-CNL-haswell')

        cray_login_node_options.append(
            '-DCN_RUNTIME_PLATFORM=%s' % rt_platform)

        # Use install directories as CMAKE args for the building
        # of login cbtf-krell
        cray_login_node_options.append(
            '-DCBTF_CN_RUNTIME_DIR=%s' % be_cbtf.prefix)
        cray_login_node_options.append(
            '-DCBTF_KRELL_CN_RUNTIME_DIR=%s' % be_cbtfk.prefix)
        cray_login_node_options.append(
            '-DPAPI_CN_RUNTIME_DIR=%s' % be_papi.prefix)
        cray_login_node_options.append(
            '-DBOOST_CN_RUNTIME_DIR=%s' % be_boost.prefix)
        cray_login_node_options.append(
            '-DLIBMONITOR_CN_RUNTIME_DIR=%s' % be_mont.prefix)
        cray_login_node_options.append(
            '-DLIBUNWIND_CN_RUNTIME_DIR=%s' % be_unw.prefix)
        cray_login_node_options.append(
            '-DXERCESC_CN_RUNTIME_DIR=%s' % be_xer.prefix)
        cray_login_node_options.append(
            '-DDYNINST_CN_RUNTIME_DIR=%s' % be_dyn.prefix)
        cray_login_node_options.append(
            '-DMRNET_CN_RUNTIME_DIR=%s' % be_mrnet.prefix)

        cmake_options.extend(cray_login_node_options)

    def cmake_args(self):
        spec = self.spec

        compile_flags = "-O2 -g"

        # Add in paths for finding package config files that tell us
        # where to find these packages
        cmake_args = [
            '-DCMAKE_CXX_FLAGS=%s'         % compile_flags,
            '-DCMAKE_C_FLAGS=%s'           % compile_flags,
            '-DCBTF_DIR=%s' % spec['cbtf'].prefix,
            '-DBINUTILS_DIR=%s' % spec['binutils'].prefix,
            '-DLIBMONITOR_DIR=%s' % spec['libmonitor'].prefix,
            '-DLIBUNWIND_DIR=%s' % spec['libunwind'].prefix,
            '-DPAPI_DIR=%s' % spec['papi'].prefix,
            '-DBOOST_DIR=%s' % spec['boost'].prefix,
            '-DMRNET_DIR=%s' % spec['mrnet'].prefix,
            '-DDYNINST_DIR=%s' % spec['dyninst'].prefix,
            '-DLIBIOMP_DIR=%s' % spec['llvm-openmp-ompt'].prefix,
            '-DGOTCHA_DIR=%s' % spec['gotcha'].prefix,
            '-DXERCESC_DIR=%s' % spec['xerces-c'].prefix]

        if self.spec.satisfies('+runtime'):
            self.set_rt_only_cmake_options(spec, cmake_args)

        # Add any MPI implementations coming from variant settings
        self.set_mpi_cmake_options(spec, cmake_args)

        if self.spec.satisfies('+crayfe'):
            # We need to build target/compute node components/libraries first
            # then pass those libraries to the cbtf-krell login node build
            self.set_cray_login_node_cmake_options(spec, cmake_args)

        return cmake_args

    def setup_environment(self, spack_env, run_env):
        """Set up the compile and runtime environments for a package."""

        # Environment settings for cbtf-krell, bin is automatically
        # added to the path in the module file
        run_env.prepend_path('PATH', self.prefix.sbin)

        run_env.set('XPLAT_RSH', 'ssh')
        run_env.set('MRNET_COMM_PATH', self.prefix.sbin.cbtf_mrnet_commnode)

        # Set CBTF_MPI_IMPLEMENTATON to the appropriate mpi implementation
        # This is needed by CBTF tools to deploy the correct
        # mpi runtimes for cbtfsummary
        # Users may have to set the CBTF_MPI_IMPLEMENTATION variable
        # manually if multiple mpi's are specified in the build

        if self.spec.satisfies('+mpich'):
            run_env.set('CBTF_MPI_IMPLEMENTATION', "mpich")

        if self.spec.satisfies('+mvapich'):
            run_env.set('CBTF_MPI_IMPLEMENTATION', "mvapich")

        if self.spec.satisfies('+mvapich2'):
            run_env.set('CBTF_MPI_IMPLEMENTATION', "mvapich2")

        if self.spec.satisfies('+mpt'):
            run_env.set('CBTF_MPI_IMPLEMENTATION', "mpt")

        if self.spec.satisfies('+openmpi'):
            run_env.set('CBTF_MPI_IMPLEMENTATION', "openmpi")

        run_env.set('CBTF_MRNET_BACKEND_PATH',
                    self.prefix.sbin.cbtf_libcbtf_mrnet_backend)
