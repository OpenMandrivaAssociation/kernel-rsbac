# -*- Mode: rpm-spec -*-
#
# This Specfile is based on kernel-tmb spec done by
# Thomas Backlund <tmb@mandriva.org>
# 
# The mkflavour() macroization done by Anssi Hannula <anssi@mandriva.org>
#
# Manbo kernels now use kernel.org versioning
#
%define kernelversion	2
%define patchlevel	6
%define sublevel	31

# Package release
%define kbuild		2
%define	rsbacver	1.4.3

# kernel Makefile extraversion is substituted by 
# kpatch/kgit/kstable wich are either 0 (empty), rc (kpatch), git (kgit) 
# or stable release (kstable)
%define kpatch		0
%define kstable		6
# kernel.org -gitX patch (only the number after "git")
%define kgit		0

# Used when building update candidates
#define uclevel uc1
%define devel_notice %{?uclevel:NOTE: This is work-in-progress (WIP) development kernel.}

# Patch tarball tag
%define ktag		rsbac
%define kname 		kernel-%{ktag}

%define rpmtag		%distsuffix
%if %kpatch
%if %kgit
%define rpmrel		%mkrel 0.%{kpatch}.%{kgit}.%{kbuild}
%else
%define rpmrel		%mkrel 0.%{kpatch}.%{kbuild}
%endif
%else
%define rpmrel		%mkrel %{kbuild}
%endif

# fakerel above and fakever below never change, they are used to fool
# rpm/urpmi/smart
%define fakever		1
%define fakerel		%mkrel 1

# When we are using a pre/rc patch, the tarball is a sublevel -1
%if %kpatch
%define kversion  	%{kernelversion}.%{patchlevel}.%{sublevel}
%define tar_ver	  	%{kernelversion}.%{patchlevel}.%(expr %{sublevel} - 1)
%define patch_ver 	%{kversion}-%{kpatch}-%{ktag}%{kbuild}
%else
%if %kstable
%define kversion  	%{kernelversion}.%{patchlevel}.%{sublevel}.%{kstable}
%define tar_ver   	%{kernelversion}.%{patchlevel}.%{sublevel}
%else
%define kversion  	%{kernelversion}.%{patchlevel}.%{sublevel}
%define tar_ver   	%{kversion}
%endif
%define patch_ver 	%{kversion}-%{ktag}%{kbuild}
%endif
%define kverrel   	%{kversion}-%{rpmrel}

# used for not making too long names for rpms or search paths 
%if %kpatch
%if %kgit
%define buildrpmrel     0.%{kpatch}.%{kgit}.%{kbuild}%{?uclevel:.%{uclevel}}%{rpmtag}
%else
%define buildrpmrel     0.%{kpatch}.%{kbuild}%{?uclevel:.%{uclevel}}%{rpmtag}
%endif
%else
%define buildrpmrel     %{kbuild}%{?uclevel:.%{uclevel}}%{rpmtag}
%endif
%define buildrel     	%{kversion}-%{buildrpmrel}

# having different top level names for packges means that you have to remove
# them by hard :(
%define top_dir_name 	%{kname}-%{_arch}

%define build_dir 	${RPM_BUILD_DIR}/%{top_dir_name}
%define src_dir 	%{build_dir}/linux-%{tar_ver}

# disable useless debug rpms...
%define _enable_debug_packages 	%{nil}
%define debug_package 		%{nil}

# Build defines
%define build_doc 		1
%define build_source 		1
%define build_devel 		1

# Make kernel packages backportable
%if %{mdkversion} < 201000
# disable debug rpms for backports, it's enough already having them on cooker/stable
%define build_debug            0
%else
%define build_debug            1
%endif

# Build desktop i586 / 4GB
%ifarch %{ix86}
%define build_desktop586	1
%endif

# Build desktop (i686 / 4GB) / x86_64 / sparc64 sets
%define build_desktop		1

# Build server (i686 / 64GB)/x86_64 / sparc64 sets
%define build_server		1

# End of user definitions
%{?_without_desktop586: %global build_desktop586 0}
%{?_without_desktop: %global build_desktop 0}
%{?_without_server: %global build_server 0}
%{?_without_doc: %global build_doc 0}
%{?_without_source: %global build_source 0}
%{?_without_devel: %global build_devel 0}
%{?_without_debug: %global build_debug 0}

%{?_with_desktop586: %global build_desktop586 1}
%{?_with_desktop: %global build_desktop 1}
%{?_with_server: %global build_server 1}
%{?_with_doc: %global build_doc 1}
%{?_with_source: %global build_source 1}
%{?_with_devel: %global build_devel 1}
%{?_with_debug: %global build_debug 1}

# For the .nosrc.rpm
%define build_nosrc 	0
%{?_with_nosrc: %global build_nosrc 1}

%if %(if [ -z "$CC" ] ; then echo 0; else echo 1; fi)
%define kmake %make CC="$CC"
%else
%define kmake %make
%endif
# there are places where parallel make don't work
%define smake make

# Parallelize xargs invocations on smp machines
%define kxargs xargs %([ -z "$RPM_BUILD_NCPUS" ] \\\
	&& RPM_BUILD_NCPUS="`/usr/bin/getconf _NPROCESSORS_ONLN`"; \\\
	[ "$RPM_BUILD_NCPUS" -gt 1 ] && echo "-P $RPM_BUILD_NCPUS")

# Sparc arch wants sparc64 kernels
%define target_arch    %(echo %{_arch} | sed -e "s/sparc/sparc64/")


#
# SRC RPM description
#
Summary: 	Hardened Linux kernel with RSBAC enhancement
Name:		%{kname}
Version: 	%{kversion}
Release: 	%{rpmrel}
License: 	GPLv2
Group: 	 	System/Kernel and hardware
ExclusiveArch: %{ix86} ppc powerpc x86_64 amd64 sparc sparc64
ExclusiveOS: 	Linux
Provides:	kernel = %{kversion}
URL:            http://www.rsbac.org

####################################################################
#
# Sources
#
### This is for full SRC RPM
Source0: 	ftp://ftp.kernel.org/pub/linux/kernel/v%{kernelversion}.%{patchlevel}/linux-%{tar_ver}.tar.bz2
Source1: 	ftp://ftp.kernel.org/pub/linux/kernel/v%{kernelversion}.%{patchlevel}/linux-%{tar_ver}.tar.bz2.sign
### This is for stripped SRC RPM
%if %build_nosrc
NoSource: 0
%endif
# This is for disabling *config, mrproper, prepare, scripts on -devel rpms
Source2: 	disable-mrproper-in-devel-rpms.patch
Source3:	disable-prepare-scripts-configs-in-devel-rpms.patch

Source4: 	README.kernel-sources
Source5: 	README.MandrivaLinux

Source100: 	linux-%{patch_ver}.tar.bz2

Source200:	kernel-rsbac.config
Source201:	http://download.rsbac.org/code/%{rsbacver}/%{kernelversion}/rsbac-common-%{kernelversion}.%{patchlevel}-%{rsbacver}.tar.bz2

####################################################################
#
# Patches

#
# Patch0 to Patch100 are for core kernel upgrades.
#

# Pre linus patch: ftp://ftp.kernel.org/pub/linux/kernel/v2.6/testing

%if %kpatch
Patch1:		ftp://ftp.kernel.org/pub/linux/kernel/v%{kernelversion}.%{patchlevel}/testing/patch-%{kernelversion}.%{patchlevel}.%{sublevel}-%{kpatch}.bz2
Source10: 	ftp://ftp.kernel.org/pub/linux/kernel/v%{kernelversion}.%{patchlevel}/testing/patch-%{kernelversion}.%{patchlevel}.%{sublevel}-%{kpatch}.bz2.sign
%endif
%if %kgit
Patch2:		ftp://ftp.kernel.org/pub/linux/kernel/v%{kernelversion}.%{patchlevel}/snapshots/patch-%{kernelversion}.%{patchlevel}.%{sublevel}-%{kpatch}-git%{kgit}.bz2
Source11:	ftp://ftp.kernel.org/pub/linux/kernel/v%{kernelversion}.%{patchlevel}/snapshots/patch-%{kernelversion}.%{patchlevel}.%{sublevel}-%{kpatch}-git%{kgit}.bz2.sign
%endif
%if %kstable
Patch1:   	ftp://ftp.kernel.org/pub/linux/kernel/v%{kernelversion}.%{patchlevel}/patch-%{kversion}.bz2
Source10: 	ftp://ftp.kernel.org/pub/linux/kernel/v%{kernelversion}.%{patchlevel}/patch-%{kversion}.bz2.sign
%endif

#END
####################################################################

# Defines for the things that are needed for all the kernels
#
%define common_description_kernel The kernel package contains the Linux kernel (vmlinuz), the core of your \
Mandriva/RSBAC Linux operating system. The kernel handles the basic functions \
of the operating system: memory allocation, process allocation, device \
input and output, etc. 

%define common_description_info For instructions for update, see:	\
http://www.mandriva.com/en/security/kernelupdate			\
This kernel include the RSBAC system. RSBAC is a flexible, powerful and \
fast (low overhead) open source access control framework for Linux kernels \
but this security solution is a very complex system: \
please don't use this kernel by newbie user. \
Please read more information in RSBAC home page: http://www.rsbac.org \
									\
%{devel_notice}

### Global Requires/Provides
%define requires1	bootloader-utils >= 1.13-1
%define requires2	mkinitrd >= 4.2.17-31
%define requires3	module-init-tools >= 3.0-7
%define requires4	sysfsutils >= 1.3.0-1
%define requires5	kernel-firmware >= 2.6.27-0.rc2.2mdv

%define kprovides 	%{kname} = %{kverrel}, kernel = %{tar_ver} ,alsa = 1.0.21, drbd-api = 88

%define kconflicts	drakxtools-backend < 10.4.190-2

%define kobsoletes	dkms-iwlwifi < 1.2.26

BuildRoot: 		%{_tmppath}/%{kname}-%{kversion}-%{_arch}-build
Autoreqprov: 		no
BuildRequires: 		gcc module-init-tools

%description
%common_description_kernel

%common_description_info

# Virtual kernel rpm to help the installer during the naming transition,
# consider removing it after 2008.0 release
%package -n %{kname}-%{buildrel}
Version:	%{fakever}
Release:	%{fakerel}
Summary:	Virtual rpm for installing the default %{kname}
Group:		System/Kernel and hardware
Requires:	%{kname}-desktop-%{buildrel}
%description -n %{kname}-%{buildrel}
This package is a virtual rpm that helps the installer to install
the default %{kname} during the transition to the new naming scheme.

%common_description_info

%files -n %{kname}-%{buildrel}
%defattr(-,root,root)

# mkflavour() name flavour processor
# name: the flavour name in the package name
# flavour: first parameter of CreateKernel()
%define mkflavour()					\
%package -n %{kname}-%{1}-%{buildrel}			\
Version:	%{fakever}				\
Release:	%{fakerel}				\
Provides:	%kprovides				\
Requires(pre):	%requires1 %requires2 %requires3 %requires4 \
Requires:	%requires5				\
Provides:	should-restart = system			\
Provides:	kernel-%{1} = %{kverrel}		\
Suggests:	crda					\
Obsoletes:	%kobsoletes				\
Conflicts:	%kconflicts				\
%ifarch %{ix86}						\
Conflicts:	arch(x86_64)				\
%endif							\
Summary:	%{expand:%{summary_%(echo %{1})}}	\
Group:		System/Kernel and hardware		\
%description -n %{kname}-%{1}-%{buildrel}		\
%common_description_kernel %{expand:%{info_%(echo %{1})}} \
							\
%common_description_info				\
							\
%if %build_devel					\
%package -n	%{kname}-%{1}-devel-%{buildrel}		\
Version:	%{fakever}				\
Release:	%{fakerel}				\
Requires:	glibc-devel ncurses-devel make gcc perl	\
Summary:	The kernel-devel files for %{kname}-%{1}-%{buildrel} \
Group:		Development/Kernel			\
Provides:	kernel-devel = %{kverrel} 		\
Provides:	%{kname}-devel = %{kverrel}		\
%ifarch %{ix86}						\
Conflicts:	arch(x86_64)				\
%endif							\
%description -n %{kname}-%{1}-devel-%{buildrel}		\
This package contains the kernel files (headers and build tools) \
that should be enough to build additional drivers for   \
use with %{kname}-%{1}-%{buildrel}.                     \
							\
If you want to build your own kernel, you need to install the full \
%{kname}-source-%{buildrel} rpm.			\
							\
%common_description_info				\
%endif							\
							\
%if %build_debug					\
%package -n	%{kname}-%{1}-debug-%{buildrel}		\
Version:	%{fakever}				\
Release:	%{fakerel}				\
Summary:	Files with debug info for %{kname}-%{1}-%{buildrel} \
Group:		Development/Debug			\
Provides:	kernel-debug = %{kverrel} 		\
Provides:	%{kname}-debug = %{kverrel}		\
%ifarch %{ix86}						\
Conflicts:	arch(x86_64)				\
%endif							\
%description -n %{kname}-%{1}-debug-%{buildrel}		\
This package contains the files with debug info to aid in debug tasks \
when using %{kname}-%{1}-%{buildrel}.			\
							\
If you need to look at debug information or use some application that \
needs debugging info from the kernel, this package may help. \
							\
%common_description_info				\
%endif							\
							\
%package -n %{kname}-%{1}-latest			\
Version:	%{kversion}				\
Release:	%{rpmrel}				\
Summary:	Virtual rpm for latest %{kname}-%{1}	\
Group:		System/Kernel and hardware		\
Requires:	%{kname}-%{1}-%{buildrel}		\
%ifarch %{ix86}						\
Conflicts:	arch(x86_64)				\
%endif							\
%description -n %{kname}-%{1}-latest			\
This package is a virtual rpm that aims to make sure you always have the \
latest %{kname}-%{1} installed...			\
							\
%common_description_info				\
							\
%if %build_devel					\
%package -n %{kname}-%{1}-devel-latest			\
Version:	%{kversion}				\
Release:	%{rpmrel}				\
Summary:	Virtual rpm for latest %{kname}-%{1}-devel \
Group:		Development/Kernel			\
Requires:	%{kname}-%{1}-devel-%{buildrel}		\
%ifarch %{ix86}						\
Conflicts:	arch(x86_64)				\
%endif							\
Provides:	%{kname}-devel-latest			\
Provides:	kernel-devel-latest			\
%description -n %{kname}-%{1}-devel-latest		\
This package is a virtual rpm that aims to make sure you always have the \
latest %{kname}-%{1}-devel installed...			\
							\
%common_description_info				\
%endif							\
							\
%if %build_debug					\
%package -n %{kname}-%{1}-debug-latest			\
Version:	%{kversion}				\
Release:	%{rpmrel}				\
Summary:	Virtual rpm for latest %{kname}-%{1}-debug \
Group:		Development/Debug			\
Requires:	%{kname}-%{1}-debug-%{buildrel}		\
%ifarch %{ix86}						\
Conflicts:	arch(x86_64)				\
%endif							\
Provides:	%{kname}-debug-latest			\
Provides:	kernel-debug-latest			\
%description -n %{kname}-%{1}-debug-latest		\
This package is a virtual rpm that aims to make sure you always have the \
latest %{kname}-%{1}-debug installed...			\
							\
%common_description_info				\
%endif							\
							\
%post -n %{kname}-%{1}-%{buildrel} -f kernel_files.%{1}-post \
cat << EOF						\
Please add to the kernel parameters this options 	\
to the successful first boot:				\
rsbac_softmode rsbac_um_no_excl				\
..and please read the Documentation/rsbac/README-kernparam file	\
the more information.					\
Thank you: Gergely Lónyai				\
EOF							\
							\
%preun -n %{kname}-%{1}-%{buildrel} -f kernel_files.%{1}-preun \
%postun -n %{kname}-%{1}-%{buildrel} -f kernel_files.%{1}-postun \
							\
%if %build_devel					\
%post -n %{kname}-%{1}-devel-%{buildrel} -f kernel_devel_files.%{1}-post \
%preun -n %{kname}-%{1}-devel-%{buildrel} -f kernel_devel_files.%{1}-preun \
%endif							\
							\
%files -n %{kname}-%{1}-%{buildrel} -f kernel_files.%{1} \
%files -n %{kname}-%{1}-latest				\
%defattr(-,root,root)					\
							\
%if %build_devel					\
%files -n %{kname}-%{1}-devel-%{buildrel} -f kernel_devel_files.%{1} \
%files -n %{kname}-%{1}-devel-latest			\
%defattr(-,root,root)					\
%endif							\
							\
%if %build_debug					\
%files -n %{kname}-%{1}-debug-%{buildrel} -f kernel_debug_files.%{1} \
%files -n %{kname}-%{1}-debug-latest			\
%defattr(-,root,root)					\
%endif

%ifarch %{ix86}
#
# kernel-desktop586: i586, smp-alternatives, 4GB
#
%if %build_desktop586
%define summary_desktop586 Hardened Linux kernel for desktop use with i586 & 4GB RAM RAM and enhanced by RSBAC
%define info_desktop586 This kernel is compiled for desktop use, single or \
multiple i586 processor(s)/core(s) and less than 4GB RAM, using voluntary \
preempt, CFS cpu scheduler and cfq i/o scheduler. \
This kernel relies on in-kernel smp alternatives to switch between up & smp \
mode depending on detected hardware. To force the kernel to boot in single \
processor mode, use the "nosmp" boot parameter.
%mkflavour desktop586
%endif
%endif

#
# kernel-desktop: i686, smp-alternatives, 4 GB / x86_64
#

%if %build_desktop
%ifarch %{ix86}
%define summary_desktop Hardened Linux Kernel for desktop use with i686 & 4GB RAM and enhanced by RSBAC
%define info_desktop This kernel is compiled for desktop use, single or \
multiple i686 processor(s)/core(s) and less than 4GB RAM, using HZ_1000, \
voluntary preempt, CFS cpu scheduler and cfq i/o scheduler. \
This kernel relies on in-kernel smp alternatives to switch between up & smp \
mode depending on detected hardware. To force the kernel to boot in single \
processor mode, use the "nosmp" boot parameter.
%else
%define summary_desktop Hardened Linux Kernel for desktop use with %{_arch} and enhanced by RSBAC
%define info_desktop This kernel is compiled for desktop use, single or \
multiple %{_arch} processor(s)/core(s), using HZ_1000, voluntary preempt, \
CFS cpu scheduler and cfq i/o scheduler. \
This kernel relies on in-kernel smp alternatives to switch between up & smp \
mode depending on detected hardware. To force the kernel to boot in single \
processor mode, use the "nosmp" boot parameter.
%endif
%mkflavour desktop
%endif

#
# kernel-server: i686, smp-alternatives, 64 GB / x86_64
#

%if %build_server
%ifarch %{ix86}
%define summary_server Hardened Linux Kernel for server use with i686 & 64GB RAM and enhanced by RSBAC
%define info_server This kernel is compiled for server use, single or \
multiple i686 processor(s)/core(s) and up to 64GB RAM using PAE, using \
no preempt, HZ_100, CFS cpu scheduler and cfq i/o scheduler. \
This kernel relies on in-kernel smp alternatives to switch between up & smp \
mode depending on detected hardware. To force the kernel to boot in single \
processor mode, use the "nosmp" boot parameter.
%else
%define summary_server Hardened Linux Kernel for server use with %{_arch} and enhanced by RSBAC
%define info_server This kernel is compiled for server use, single or \
multiple %{_arch} processor(s)/core(s), using no preempt, HZ_100, \
CFS cpu scheduler and cfq i/o scheduler. \
This kernel relies on in-kernel smp alternatives to switch between up & smp \
mode depending on detected hardware. To force the kernel to boot in single \
processor mode, use the "nosmp" boot parameter.
%endif
%mkflavour server
%endif

#
# kernel-source
#
%if %build_source
%package -n %{kname}-source-%{buildrel}
Version: 	%{fakever}
Release: 	%{fakerel}
Requires: 	glibc-devel, ncurses-devel, make, gcc, perl
Summary: 	The Linux source code for %{kname}-%{buildrel}  
Group: 		Development/Kernel
Autoreqprov: 	no
Provides: 	kernel-source = %{kverrel}, kernel-devel = %{kverrel}
Provides: 	%{kname}-source = %{kverrel}, %{kname}-devel = %{kverrel}
%ifarch %{ix86}	
Conflicts:	arch(x86_64)
%endif

%description -n %{kname}-source-%{buildrel}
The %{kname}-source package contains the source code files for the Manbo
Linux kernel. Theese source files are only needed if you want to build your
own custom kernel that is better tuned to your particular hardware.

If you only want the files needed to build 3rdparty (nVidia, Ati, dkms-*,...)
drivers against, install the *-devel-* rpm that is matching your kernel.

%common_description_info

%post -n %{kname}-source-%{buildrel}
for i in /lib/modules/%{kversion}-{desktop586,desktop,server}-%{buildrpmrel}; do
        if [ -d $i ]; then
		if [ ! -L $i/build -a ! -L $i/source ]; then
			ln -sf /usr/src/linux-%{kversion}-%{buildrpmrel} $i/build
			ln -sf /usr/src/linux-%{kversion}-%{buildrpmrel} $i/source
		fi
        fi
done
cd /usr/src
rm -f linux
ln -snf linux-%{kversion}-%{buildrpmrel} linux

%preun -n %{kname}-source-%{buildrel}
for i in /lib/modules/%{kversion}-{desktop586,desktop,server}-%{buildrpmrel}/{build,source}; do
	if [ -L $i ]; then
		if [ "$(readlink $i)" = "/usr/src/linux-%{kversion}-%{buildrpmrel}" ]; then
			rm -f $i
		fi
	fi
done
if [ -L /usr/src/linux ]; then
	if [ "$(readlink /usr/src/linux)" = "linux-%{kversion}-%{buildrpmrel}" ]; then
		rm -f /usr/src/linux
	fi
fi
exit 0

#
# kernel-source-latest: virtual rpm
#
%package -n %{kname}-source-latest
Version: 	%{kversion}
Release: 	%{rpmrel}
Summary: 	Virtual rpm for latest %{kname}-source
Group:   	Development/Kernel
Requires: 	%{kname}-source-%{buildrel}
Provides:	kernel-source-%{buildrel} = %{kversion}
%ifarch %{ix86}	
Conflicts:	arch(x86_64)
%endif

%description -n %{kname}-source-latest
This package is a virtual rpm that aims to make sure you always have the
latest %{kname}-source installed...

%common_description_info
%endif

%if %build_doc
#
# kernel-doc: documentation for the Linux kernel
#
%package -n %{kname}-doc
Version: 	%{kversion}
Release: 	%{rpmrel}
Summary: 	Various documentation bits found in the %{kname} source
Group: 		Books/Computer books
Provides:	kernel-doc = %{kversion}
%ifarch %{ix86}	
Conflicts:	arch(x86_64)
%endif

%description -n %{kname}-doc
This package contains documentation files from the %{kname} source. 
Various bits of information about the Linux kernel and the device drivers 
shipped with it are documented in these files. You also might want install 
this package if you need a reference to the options that can be passed to 
Linux kernel modules at load time.

%common_description_info
%endif

#
# End packages - here begins build stage
#
%prep
%setup -q -n %top_dir_name -c
#RSBAC
%setup -q -n %top_dir_name/linux-%{tar_ver} -D -T -a201
#
%setup -q -n %top_dir_name -D -T -a100

%define patches_dir ../%{patch_ver}/

cd %src_dir
%if %kpatch
%patch1 -p1
%endif
%if %kgit
%patch2 -p1
%endif
%if %kstable
%patch1 -p1
%endif

#RSBAC
for I in `find %{patches_dir}/configs/ -type f` ; do
	sed 's/^.*CONFIG_CRYPTO_SHA1=.*$/CONFIG_CRYPTO_SHA1=y/' -i ${I}
	cat %{SOURCE200} >> ${I}
done
cat %{SOURCE200} >> .config
sed 's/^.*CONFIG_CRYPTO_SHA1=.*$/CONFIG_CRYPTO_SHA1=y/' -i .config
#

%{patches_dir}/scripts/apply_patches

# PATCH END


#
# Setup Begin
#

# Prepare all the variables for calling create_configs

# Make kernel packages backportable
%if %{mdkversion} < 201000
# disable modesetting by default, no plymouth for distros < 2010.0
sed -i  's/\(CONFIG_DRM_[A-Z0-9]\+_KMS\)=y/# \1 is not set/' \
        %{patches_dir}/configs/*.config
%endif

%if %build_debug
%define debug --debug
%else
%define debug --no-debug
%endif

%{patches_dir}/scripts/create_configs %debug --user_cpu="%{target_arch}"

# make sure the kernel has the sublevel we know it has...
LC_ALL=C perl -p -i -e "s/^SUBLEVEL.*/SUBLEVEL = %{sublevel}/" Makefile

# get rid of unwanted files
find . -name '*~' -o -name '*.orig' -o -name '*.append' | %kxargs rm -f


%build
# Common target directories
%define _kerneldir /usr/src/linux-%{kversion}-%{buildrpmrel}
%define _bootdir /boot
%define _modulesdir /lib/modules
%define _efidir %{_bootdir}/efi/mandriva

# Directories definition needed for building
%define temp_root %{build_dir}/temp-root
%define temp_source %{temp_root}%{_kerneldir}
%define temp_boot %{temp_root}%{_bootdir}
%define temp_modules %{temp_root}%{_modulesdir}

PrepareKernel() {
	name=$1
	extension=$2
	x86_dir=arch/x86/configs

	echo "Make config for kernel $extension"

	%smake -s mrproper

	if [ "%{target_arch}" == "i386" -o "%{target_arch}" == "x86_64" ]; then
	    if [ -z "$name" ]; then
		cp ${x86_dir}/%{target_arch}_defconfig-desktop .config
	    else
		cp ${x86_dir}/%{target_arch}_defconfig-$name .config
	    fi
	else
	    if [ -z "$name" ]; then
		cp arch/%{target_arch}/defconfig-desktop .config
	    else
		cp arch/%{target_arch}/defconfig-$name .config
	    fi
	fi

	# make sure EXTRAVERSION says what we want it to say
	%if %kstable
		LC_ALL=C perl -p -i -e "s/^EXTRAVERSION.*/EXTRAVERSION = .%{kstable}-$extension/" Makefile
	%else
		LC_ALL=C perl -p -i -e "s/^EXTRAVERSION.*/EXTRAVERSION = -$extension/" Makefile
	%endif

	%smake oldconfig
}

BuildKernel() {
	KernelVer=$1

	echo "Building kernel $KernelVer"

	%kmake all

	# Start installing stuff
	install -d %{temp_boot}
	install -m 644 System.map %{temp_boot}/System.map-$KernelVer
	install -m 644 .config %{temp_boot}/config-$KernelVer
	gzip -c Module.symvers > %{temp_boot}/symvers-$KernelVer.gz

        %ifarch ppc powerpc
	        cp -f vmlinux %{temp_boot}/vmlinuz-$KernelVer
		%ifarch ppc
			cp -f arch/ppc/boot/images/zImage.chrp-rs6k %{temp_boot}/vmlinuz-rs6k-$KernelVer
		%endif
	%else
	%ifarch sparc sparc64
		gzip -9c vmlinux > %{temp_boot}/vmlinuz-$KernelVer
	%else
		cp -f arch/%{target_arch}/boot/bzImage %{temp_boot}/vmlinuz-$KernelVer
	%endif
	%endif

	# modules
	install -d %{temp_modules}/$KernelVer
	%smake INSTALL_MOD_PATH=%{temp_root} KERNELRELEASE=$KernelVer modules_install 

	# remove /lib/firmware, we use a separate kernel-firmware
	rm -rf %{temp_root}/lib/firmware
}


SaveDevel() {
	devel_flavour=$1

	DevelRoot=/usr/src/linux-%{kversion}-$devel_flavour-%{buildrpmrel}
	TempDevelRoot=%{temp_root}$DevelRoot

	mkdir -p $TempDevelRoot
	for i in $(find . -name 'Makefile*'); do cp -R --parents $i $TempDevelRoot;done
	for i in $(find . -name 'Kconfig*' -o -name 'Kbuild*'); do cp -R --parents $i $TempDevelRoot;done
	cp -fR include $TempDevelRoot
	cp -fR scripts $TempDevelRoot
	cp -fR kernel/bounds.c $TempDevelRoot/kernel
	%ifarch %{ix86} x86_64
		cp -fR arch/x86/kernel/asm-offsets.{c,s} $TempDevelRoot/arch/x86/kernel/
		cp -fR arch/x86/kernel/asm-offsets_{32,64}.c $TempDevelRoot/arch/x86/kernel/
		cp -fR arch/x86/include $TempDevelRoot/arch/x86/
	%else
		cp -fR arch/%{target_arch}/kernel/asm-offsets.{c,s} $TempDevelRoot/arch/%{target_arch}/kernel/
		cp -fR arch/%{target_arch}/include $TempDevelRoot/arch/%{target_arch}/
	%endif
	cp -fR .config Module.symvers $TempDevelRoot
#	cp -fR 3rdparty/mkbuild.pl $TempDevelRoot/3rdparty

	# Needed for truecrypt build (Danny)
	cp -fR drivers/md/dm.h $TempDevelRoot/drivers/md/

	# Needed for lguest
	cp -fR drivers/lguest/lg.h $TempDevelRoot/drivers/lguest/

	# Needed for lirc_gpio (#39004)
	cp -fR drivers/media/video/bt8xx/bttv{,p}.h $TempDevelRoot/drivers/media/video/bt8xx/
	cp -fR drivers/media/video/bt8xx/bt848.h $TempDevelRoot/drivers/media/video/bt8xx/
	cp -fR drivers/media/video/btcx-risc.h $TempDevelRoot/drivers/media/video/

	# Needed for external dvb tree (#41418)
	cp -fR drivers/media/dvb/dvb-core/*.h $TempDevelRoot/drivers/media/dvb/dvb-core/
	cp -fR drivers/media/dvb/frontends/lgdt330x.h $TempDevelRoot/drivers/media/dvb/frontends/
	# http://lists.mandriva.com/cooker/2009-05/msg00534.php
	cp -fR drivers/ieee1394/*.h $TempDevelRoot/drivers/ieee1394/

	# add acpica header files, needed for fglrx build
	cp -fR drivers/acpi/acpica/*.h $TempDevelRoot/drivers/acpi/acpica/

	for i in alpha arm avr32 blackfin cris frv h8300 ia64 m32r m68knommu \
	         microblaze mips mn10300 parisc s390 sh xtensa; do
		rm -rf $TempDevelRoot/arch/$i
		rm -rf $TempDevelRoot/include/asm-$i
	done

	# ppc needs only m68k headers
	rm -rf $TempDevelRoot/arch/m68k

	%ifnarch ppc powerpc
		rm -rf $TempDevelRoot/arch/powerpc
		rm -rf $TempDevelRoot/include/asm-m68k
	%endif
	%ifnarch sparc sparc64
		rm -rf $TempDevelRoot/arch/sparc
		rm -rf $TempDevelRoot/arch/sparc64
	%endif
	%ifnarch %{ix86} x86_64
		rm -rf $TempDevelRoot/arch/x86
		rm -rf $TempDevelRoot/include/asm-x86
	%endif

	# Clean the scripts tree, and make sure everything is ok (sanity check)
	# running prepare+scripts (tree was already "prepared" in build)
	pushd $TempDevelRoot >/dev/null
		%smake -s prepare scripts
		%smake -s clean
	popd >/dev/null
	rm -f $TempDevelRoot/.config.old

	# fix permissions
	chmod -R a+rX $TempDevelRoot

	# disable mrproper in -devel rpms
	patch -p1 --fuzz=0 -d $TempDevelRoot -i %{SOURCE2}
	patch -p1 --fuzz=0 -d $TempDevelRoot -i %{SOURCE3}

	kernel_devel_files=../kernel_devel_files.$devel_flavour


### Create the kernel_devel_files.*
cat > $kernel_devel_files <<EOF
%defattr(-,root,root)
%dir $DevelRoot
%dir $DevelRoot/arch
%dir $DevelRoot/include
#$DevelRoot/3rdparty
$DevelRoot/Documentation
%ifarch ppc powerpc
$DevelRoot/arch/powerpc
$DevelRoot/arch/ppc
%endif
%ifarch sparc sparc64
$DevelRoot/arch/sparc
$DevelRoot/arch/sparc64
%endif
$DevelRoot/arch/um
%ifarch %{ix86} x86_64
$DevelRoot/arch/x86
%endif
$DevelRoot/block
$DevelRoot/crypto
$DevelRoot/drivers
$DevelRoot/firmware
$DevelRoot/fs
$DevelRoot/include/Kbuild
$DevelRoot/include/acpi
$DevelRoot/include/asm
$DevelRoot/include/asm-generic
%ifarch powerpc ppc
$DevelRoot/include/asm-m68k
$DevelRoot/include/asm-powerpc
$DevelRoot/include/asm-ppc
%endif
%ifarch sparc sparc64
$DevelRoot/include/asm-sparc
$DevelRoot/include/asm-sparc64
%endif
%ifarch %{ix86} x86_64
$DevelRoot/include/asm-x86
%endif
$DevelRoot/include/config
$DevelRoot/include/crypto
$DevelRoot/include/drm
$DevelRoot/include/keys
$DevelRoot/include/linux
$DevelRoot/include/math-emu
$DevelRoot/include/media
$DevelRoot/include/mtd
$DevelRoot/include/net
$DevelRoot/include/pcmcia
$DevelRoot/include/rdma
$DevelRoot/include/rsbac
$DevelRoot/include/rxrpc
$DevelRoot/include/scsi
$DevelRoot/include/sound
$DevelRoot/include/trace
$DevelRoot/include/video
$DevelRoot/include/xen
$DevelRoot/init
$DevelRoot/ipc
$DevelRoot/kernel
$DevelRoot/lib
$DevelRoot/mm
$DevelRoot/net
$DevelRoot/rsbac
$DevelRoot/samples
$DevelRoot/scripts
$DevelRoot/security
$DevelRoot/sound
$DevelRoot/tools
$DevelRoot/usr
$DevelRoot/.config
$DevelRoot/Kbuild
$DevelRoot/Makefile
$DevelRoot/Module.symvers
$DevelRoot/arch/Kconfig
%doc README.MandrivaLinux
%doc README.kernel-sources
EOF


### Create -devel Post script on the fly
cat > $kernel_devel_files-post <<EOF
if [ -d /lib/modules/%{kversion}-$devel_flavour-%{buildrpmrel} ]; then
	rm -f /lib/modules/%{kversion}-$devel_flavour-%{buildrpmrel}/{build,source}
	ln -sf $DevelRoot /lib/modules/%{kversion}-$devel_flavour-%{buildrpmrel}/build
	ln -sf $DevelRoot /lib/modules/%{kversion}-$devel_flavour-%{buildrpmrel}/source
fi
EOF


### Create -devel Preun script on the fly
cat > $kernel_devel_files-preun <<EOF
if [ -L /lib/modules/%{kversion}-$devel_flavour-%{buildrpmrel}/build ]; then
	rm -f /lib/modules/%{kversion}-$devel_flavour-%{buildrpmrel}/build
fi
if [ -L /lib/modules/%{kversion}-$devel_flavour-%{buildrpmrel}/source ]; then
	rm -f /lib/modules/%{kversion}-$devel_flavour-%{buildrpmrel}/source
fi
exit 0
EOF
}

SaveDebug() {
	debug_flavour=$1

	install -m 644 vmlinux \
	      %{temp_boot}/vmlinux-%{kversion}-$debug_flavour-%{buildrpmrel}
	kernel_debug_files=../kernel_debug_files.$debug_flavour
	echo "%defattr(-,root,root)" > $kernel_debug_files
	echo "%{_bootdir}/vmlinux-%{kversion}-$debug_flavour-%{buildrpmrel}" \
		>> $kernel_debug_files

	find %{temp_modules}/%{kversion}-$debug_flavour-%{buildrpmrel}/kernel \
		-name "*.ko" | \
		%kxargs -I '{}' objcopy --only-keep-debug '{}' '{}'.debug
	find %{temp_modules}/%{kversion}-$debug_flavour-%{buildrpmrel}/kernel \
		-name "*.ko" | %kxargs -I '{}' \
		sh -c 'cd `dirname {}`; \
		       objcopy --add-gnu-debuglink=`basename {}`.debug \
		       --strip-debug `basename {}`'

	pushd %{temp_modules}
	find %{kversion}-$debug_flavour-%{buildrpmrel}/kernel \
		-name "*.ko.debug" > debug_module_list
	popd
	cat %{temp_modules}/debug_module_list | \
		sed 's|\(.*\)|%{_modulesdir}/\1|' >> $kernel_debug_files
	cat %{temp_modules}/debug_module_list | \
		sed 's|\(.*\)|%exclude %{_modulesdir}/\1|' \
		>> ../kernel_exclude_debug_files.$debug_flavour
	rm -f %{temp_modules}/debug_module_list
}

CreateFiles() {
	kernel_flavour=$1

	kernel_files=../kernel_files.$kernel_flavour

### Create the kernel_files.*
cat > $kernel_files <<EOF
%defattr(-,root,root)
%{_bootdir}/System.map-%{kversion}-$kernel_flavour-%{buildrpmrel}
%{_bootdir}/symvers-%{kversion}-$kernel_flavour-%{buildrpmrel}.gz
%{_bootdir}/config-%{kversion}-$kernel_flavour-%{buildrpmrel}
%{_bootdir}/vmlinuz-%{kversion}-$kernel_flavour-%{buildrpmrel}
%dir %{_modulesdir}/%{kversion}-$kernel_flavour-%{buildrpmrel}/
%{_modulesdir}/%{kversion}-$kernel_flavour-%{buildrpmrel}/kernel
%{_modulesdir}/%{kversion}-$kernel_flavour-%{buildrpmrel}/modules.*
%doc README.MandrivaLinux
%doc README.kernel-sources
EOF

	%if %build_debug
	cat ../kernel_exclude_debug_files.$kernel_flavour >> $kernel_files
	%endif

### Create kernel Post script
cat > $kernel_files-post <<EOF
/sbin/installkernel %{kversion}-$kernel_flavour-%{buildrpmrel}
pushd /boot > /dev/null
if [ -L vmlinuz-$kernel_flavour ]; then
	rm -f vmlinuz-$kernel_flavour
fi
ln -sf vmlinuz-%{kversion}-$kernel_flavour-%{buildrpmrel} vmlinuz-$kernel_flavour
if [ -L initrd-$kernel_flavour.img ]; then
	rm -f initrd-$kernel_flavour.img
fi
ln -sf initrd-%{kversion}-$kernel_flavour-%{buildrpmrel}.img initrd-$kernel_flavour.img
popd > /dev/null
%if %build_devel
# create kernel-devel symlinks if matching -devel- rpm is installed
if [ -d /usr/src/linux-%{kversion}-$kernel_flavour-%{buildrpmrel} ]; then
	rm -f /lib/modules/%{kversion}-$kernel_flavour-%{buildrpmrel}/{build,source}
	ln -sf /usr/src/linux-%{kversion}-$kernel_flavour-%{buildrpmrel} /lib/modules/%{kversion}-$kernel_flavour-%{buildrpmrel}/build
	ln -sf /usr/src/linux-%{kversion}-$kernel_flavour-%{buildrpmrel} /lib/modules/%{kversion}-$kernel_flavour-%{buildrpmrel}/source
fi
%endif
%if %build_source
# create kernel-source symlinks only if matching -devel- rpm is not installed
if [ -d /usr/src/linux-%{kversion}-%{buildrpmrel} -a ! -d /usr/src/linux-%{kversion}-$kernel_flavour-%{buildrpmrel} ]; then
	rm -f /lib/modules/%{kversion}-$kernel_flavour-%{buildrpmrel}/{build,source}
	ln -sf /usr/src/linux-%{kversion}-%{buildrpmrel} /lib/modules/%{kversion}-$kernel_flavour-%{buildrpmrel}/build
	ln -sf /usr/src/linux-%{kversion}-%{buildrpmrel} /lib/modules/%{kversion}-$kernel_flavour-%{buildrpmrel}/source
fi
%endif
EOF


### Create kernel Preun script on the fly
cat > $kernel_files-preun <<EOF
/sbin/installkernel -R %{kversion}-$kernel_flavour-%{buildrpmrel}
pushd /boot > /dev/null
if [ -L vmlinuz-$kernel_flavour ]; then
	if [ "$(readlink vmlinuz-$kernel_flavour)" = "vmlinuz-%{kversion}-$kernel_flavour-%{buildrpmrel}" ]; then
		rm -f vmlinuz-$kernel_flavour
	fi
fi
if [ -L initrd-$kernel_flavour.img ]; then
	if [ "$(readlink initrd-$kernel_flavour.img)" = "initrd-%{kversion}-$kernel_flavour-%{buildrpmrel}.img" ]; then
		rm -f initrd-$kernel_flavour.img
	fi
fi
popd > /dev/null
%if %build_devel
if [ -L /lib/modules/%{kversion}-$kernel_flavour-%{buildrpmrel}/build ]; then
	rm -f /lib/modules/%{kversion}-$kernel_flavour-%{buildrpmrel}/build
fi
if [ -L /lib/modules/%{kversion}-$kernel_flavour-%{buildrpmrel}/source ]; then
	rm -f /lib/modules/%{kversion}-$kernel_flavour-%{buildrpmrel}/source
fi
%endif
exit 0
EOF


### Create kernel Postun script on the fly
cat > $kernel_files-postun <<EOF
/sbin/kernel_remove_initrd %{kversion}-$kernel_flavour-%{buildrpmrel}
EOF
}


CreateKernel() {
	flavour=$1

	PrepareKernel $flavour $flavour-%{buildrpmrel}

	BuildKernel %{kversion}-$flavour-%{buildrpmrel}
	%if %build_devel
		SaveDevel $flavour
	%endif
	%if %build_debug
		SaveDebug $flavour
	%endif
	CreateFiles $flavour
}


###
# DO it...
###


# Create a simulacro of buildroot
rm -rf %{temp_root}
install -d %{temp_root}


#make sure we are in the directory
cd %src_dir

%ifarch %{ix86}
%if %build_desktop586
CreateKernel desktop586
%endif
%endif

%if %build_desktop
CreateKernel desktop
%endif

%if %build_server
CreateKernel server
%endif


# We don't make to repeat the depend code at the install phase
%if %build_source
    PrepareKernel "" %{buildrpmrel}custom
%smake -s mrproper
%endif


###
### install
###
%install
install -m 644 %{SOURCE4}  .
install -m 644 %{SOURCE5}  .

cd %src_dir

# Directories definition needed for installing
%define target_source %{buildroot}%{_kerneldir}
%define target_boot %{buildroot}%{_bootdir}
%define target_modules %{buildroot}%{_modulesdir}

# We want to be able to test several times the install part
rm -rf %{buildroot}
cp -a %{temp_root} %{buildroot}

# Create directories infastructure
%if %build_source
install -d %{target_source} 

tar cf - . | tar xf - -C %{target_source}
chmod -R a+rX %{target_source}

# we remove all the source files that we don't ship
# first architecture files
for i in alpha arm arm26 avr32 blackfin cris frv h8300 ia64 m32r m68knommu \
         microblaze mips parisc s390 sh sh64 v850 xtensa mn10300; do
	rm -rf %{target_source}/arch/$i
	rm -rf %{target_source}/include/asm-$i
done

# ppc needs only m68k headers
rm -rf %{target_source}/arch/m68k

%ifnarch ppc powerpc
	rm -rf %{target_source}/arch/ppc
	rm -rf %{target_source}/arch/powerpc
	rm -rf %{target_source}/include/asm-m68k
	rm -rf %{target_source}/include/asm-ppc
	rm -rf %{target_source}/include/asm-powerpc
%endif
%ifnarch sparc sparc64
	rm -rf %{target_source}/arch/sparc
	rm -rf %{target_source}/arch/sparc64
	rm -rf %{target_source}/include/asm-sparc
	rm -rf %{target_source}/include/asm-sparc64
%endif
%ifnarch %{ix86} x86_64
	rm -rf %{target_source}/arch/x86
	rm -rf %{target_source}/include/asm-x86
%endif

# other misc files
rm -f %{target_source}/{.config.old,.config.cmd,.gitignore,.lst,.mailmap}
rm -f %{target_source}/{.missing-syscalls.d,arch/.gitignore,firmware/.gitignore}

#endif %build_source
%endif

# gzipping modules
find %{target_modules} -name "*.ko" | %kxargs gzip -9

# We used to have a copy of PrepareKernel here
# Now, we make sure that the thing in the linux dir is what we want it to be
for i in %{target_modules}/*; do
	rm -f $i/build $i/source
done

# sniff, if we gzipped all the modules, we change the stamp :(
# we really need the depmod -ae here
pushd %{target_modules}
for i in *; do
	/sbin/depmod -u -ae -b %{buildroot} -r -F %{target_boot}/System.map-$i $i
	echo $?
done

for i in *; do
	pushd $i
	echo "Creating modules.description for $i"
	modules=`find . -name "*.ko.gz"`
	echo $modules | %kxargs /sbin/modinfo \
	| perl -lne 'print "$name\t$1" if $name && /^description:\s*(.*)/; $name = $1 if m!^filename:\s*(.*)\.k?o!; $name =~ s!.*/!!' > modules.description
	popd
done
popd


###
### clean
###
%clean
rm -rf %{buildroot}


# We don't want to remove this, the whole reason of its existence is to be 
# able to do several rpm --short-circuit -bi for testing install 
# phase without repeating compilation phase
#rm -rf %{temp_root} 

###
### source and doc file lists
###

%if %build_source
%files -n %{kname}-source-%{buildrel}
%defattr(-,root,root)
%dir %{_kerneldir}
%dir %{_kerneldir}/arch
%dir %{_kerneldir}/include
#%{_kerneldir}/3rdparty
%{_kerneldir}/Documentation
%{_kerneldir}/arch/Kconfig
%ifarch powerpc ppc
%{_kerneldir}/arch/powerpc
%{_kerneldir}/arch/ppc
%endif
%ifarch sparc sparc64
%{_kerneldir}/arch/sparc
%{_kerneldir}/arch/sparc64
%endif
%{_kerneldir}/arch/um
%ifarch %{ix86} x86_64
%{_kerneldir}/arch/x86
%endif
%{_kerneldir}/block
%{_kerneldir}/crypto
%{_kerneldir}/drivers
%{_kerneldir}/firmware
%{_kerneldir}/fs
%{_kerneldir}/include/Kbuild
%{_kerneldir}/include/acpi
%{_kerneldir}/include/asm-generic
%ifarch powerpc ppc
%{_kerneldir}/include/m68k
%{_kerneldir}/include/powerpc
%{_kerneldir}/include/ppc
%endif
%ifarch sparc sparc64
%{_kerneldir}/include/asm-sparc
%{_kerneldir}/include/asm-sparc64
%endif
%ifarch %{ix86} x86_64
%{_kerneldir}/include/asm-x86
%endif
%{_kerneldir}/include/crypto
%{_kerneldir}/include/drm
%{_kerneldir}/include/keys
%{_kerneldir}/include/linux
%{_kerneldir}/include/math-emu
%{_kerneldir}/include/media
%{_kerneldir}/include/mtd
%{_kerneldir}/include/net
%{_kerneldir}/include/pcmcia
%{_kerneldir}/include/rdma
%{_kerneldir}/include/rsbac
%{_kerneldir}/include/rxrpc
%{_kerneldir}/include/scsi
%{_kerneldir}/include/sound
%{_kerneldir}/include/trace
%{_kerneldir}/include/video
%{_kerneldir}/include/xen
%{_kerneldir}/init
%{_kerneldir}/ipc
%{_kerneldir}/kernel
%{_kerneldir}/lib
%{_kerneldir}/mm
%{_kerneldir}/net
%{_kerneldir}/rsbac
%{_kerneldir}/virt
%{_kerneldir}/samples
%{_kerneldir}/scripts
%{_kerneldir}/security
%{_kerneldir}/sound
%{_kerneldir}/tools
%{_kerneldir}/usr
%{_kerneldir}/COPYING
%{_kerneldir}/CREDITS
%{_kerneldir}/Kbuild
%{_kerneldir}/MAINTAINERS
%{_kerneldir}/Makefile
%{_kerneldir}/README
%{_kerneldir}/REPORTING-BUGS
%doc README.MandrivaLinux
%doc README.kernel-sources

%files -n %{kname}-source-latest
%defattr(-,root,root)
%endif

%if %build_doc
%files -n %{kname}-doc
%defattr(-,root,root)
%doc linux-%{tar_ver}/Documentation/*
%endif

