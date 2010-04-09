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
%define sublevel	33

# kernel Makefile extraversion is substituted by
# kpatch/kgit/kstable wich are either 0 (empty), rc (kpatch),
# git (kgit, only the number after "git"), or stable release (kstable)
%define kpatch		0
%define kgit		0
%define kstable		2

# this is the releaseversion
%define kbuild		1
%define	rsbacver	1.4.3

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

# theese two never change, they are used to fool rpm/urpmi/smart
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
%define buildrpmrel     0.%{kpatch}.%{kgit}.%{kbuild}%{rpmtag}
%else
%define buildrpmrel     0.%{kpatch}.%{kbuild}%{rpmtag}
%endif
%else
%define buildrpmrel     %{kbuild}%{rpmtag}
%endif
%define buildrel     	%{kversion}-%{buildrpmrel}

# having different top level names for packges means that you have to remove them by hard :(
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
%define build_debug 		0

# Build desktop i586 / 4GB
%ifarch %{ix86}
%define build_desktop586	1
%endif

# Build desktop (i686 / 4GB) / x86_64
%define build_desktop		1

# Build server (i686 / 64GB)/x86_64
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

%define kmake %make
# there are places where parallel make don't work
%define smake make

# Parallelize xargs invocations on smp machines
%define kxargs xargs %([ -z "$RPM_BUILD_NCPUS" ] \\\
	&& RPM_BUILD_NCPUS="`/usr/bin/getconf _NPROCESSORS_ONLN`"; \\\
	[ "$RPM_BUILD_NCPUS" -gt 1 ] && echo "-P $RPM_BUILD_NCPUS")

#
# SRC RPM description
#
Summary: 	Hardened Linux kernel with RSBAC enhancement
Name:		%{kname}
Version: 	%{kversion}
Release: 	%{rpmrel}
License: 	GPLv2
Group: 	 	System/Kernel and hardware
ExclusiveArch: 	%{ix86} x86_64
ExclusiveOS: 	Linux
URL:		http://www.rsbac.org

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
# This is for disabling mrproper in -devel rpms
Source2: 	disable-mrproper-in-devel-rpms.patch
# This is for disabling the rest of the scripts in -devel rpms
Source3:	disable-prepare-scripts-configs-in-devel-rpms.patch

Source4: 	README.kernel-sources
Source5: 	README.MandrivaLinux

# This is for keeping asm-offsets.h and bounds.h in -devel rpms
Source6: 	kbuild-really-dont-remove-bounds-asm-offsets-headers.patch

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
please do not use this kernel by newbie user. \
Please read more information in RSBAC home page: http://www.rsbac.org \
									\
%{devel_notice}

### Global Requires/Provides
%define requires1 	mkinitrd >= 6.0.92-12mnb
%define requires2 	bootloader-utils >= 1.12-1
%define requires3 	sysfsutils >= 1.3.0-1 module-init-tools >= 3.2-0.pre8.2
%define requires4	kernel-firmware >= 20090604-4mnb2

%define kprovides 	%{kname} = %{kverrel}, kernel = %{tar_ver}, drbd-api = 88

BuildRoot: 		%{_tmppath}/%{kname}-%{kversion}-%{_arch}-build
%define buildroot	%{_tmppath}/%{kname}-%{kversion}-%{_arch}-build
Autoreqprov: 		no
BuildRequires: 		gcc >= 4.0.1-5 module-init-tools >= 3.2-0.pre8.2

%description
%common_description_kernel

%common_description_info


# mkflavour() name flavour processor
# name: the flavour name in the package name
# flavour: first parameter of CreateKernel()
%define mkflavour()					\
%package -n %{kname}-%{1}-%{buildrel}			\
Version:	%{fakever}				\
Release:	%{fakerel}				\
Provides:	%kprovides				\
Provides:	should-restart = system			\
Requires(pre):	%requires1 %requires2 %requires3 %requires4 \
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
%ifarch %{ix86}						\
Conflicts:	arch(x86_64)				\
%endif							\
Summary:	The kernel-devel files for %{kname}-%{1}-%{buildrel} \
Group:		Development/Kernel			\
Provides:	kernel-devel = %{kverrel} 		\
%description -n %{kname}-%{1}-devel-%{buildrel}		\
This package contains the kernel-devel files that should be enough to build \
3rdparty drivers against for use with %{kname}-%{1}-%{buildrel}. \
							\
If you want to build your own kernel, you need to install the full \
%{kname}-source-%{buildrel} rpm.			\
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
%description -n %{kname}-%{1}-devel-latest		\
This package is a virtual rpm that aims to make sure you always have the \
latest %{kname}-%{1}-devel installed...			\
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
%endif


#
# kernel-desktop586: i586, smp-alternatives, 4GB
#
%ifarch %{ix86}
%if %build_desktop586
%define summary_desktop586 Hardened Linux kernel for desktop use with i586 & 4GB RAM and enhanced by RSBAC
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
%ifarch %{ix86}
Conflicts:	arch(x86_64)
%endif

%description -n %{kname}-source-%{buildrel}
The %{kname}-source package contains the source code files for the %{ktag}
series Linux kernel. Theese source files are only needed if you want to
build your own custom kernel that is better tuned to your particular hardware.

If you only want the files needed to build 3rdparty (nVidia, Ati, dkms-*,...)
drivers against, install the *-devel-* rpm that is matching your kernel.

%common_description_info

%post -n %{kname}-source-%{buildrel}
for i in /lib/modules/%{kversion}-%{ktag}-*-%{buildrpmrel}; do
        if [ -d $i ]; then
		if [ ! -L $i/build -a ! -L $i/source ]; then
            		ln -sf /usr/src/%{kversion}-%{ktag}-%{buildrpmrel} $i/build
            		ln -sf /usr/src/%{kversion}-%{ktag}-%{buildrpmrel} $i/source
		fi
        fi
done

%preun -n %{kname}-source-%{buildrel}
for i in /lib/modules/%{kversion}-%{ktag}-*-%{buildrpmrel}/{build,source}; do
	if [ -L $i ]; then
		if [ "$(readlink $i)" = "/usr/src/%{kversion}-%{ktag}-%{buildrpmrel}" ]; then
			rm -f $i
		fi
	fi
done
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
%ifarch %{ix86}
Conflicts:	arch(x86_64)
%endif

%description -n %{kname}-source-latest
This package is a virtual rpm that aims to make sure you always have the
latest %{kname}-source installed...

%common_description_info
%endif

#
# kernel-doc: documentation for the Linux kernel
#
%if %build_doc
%package -n %{kname}-doc
Version: 	%{kversion}
Release: 	%{rpmrel}
Summary: 	Various documentation bits found in the %{kname} source
Group: 		Books/Computer books

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
%if %build_debug
%define debug --debug
%else
%define debug --no-debug
%endif

%{patches_dir}/scripts/create_configs %debug --user_cpu="%{_arch}"

# make sure the kernel has the sublevel we know it has...
LC_ALL=C perl -p -i -e "s/^SUBLEVEL.*/SUBLEVEL = %{sublevel}/" Makefile

# get rid of unwanted files
find . -name '*~' -o -name '*.orig' -o -name '*.append' |%kxargs rm -f


%build
# Common target directories
%define _kerneldir /usr/src/%{kversion}-%{ktag}-%{buildrpmrel}
%define _bootdir /boot
%define _modulesdir /lib/modules

# Directories definition needed for building
%define temp_root %{build_dir}/temp-root
%define temp_source %{temp_root}%{_kerneldir}
%define temp_boot %{temp_root}%{_bootdir}
%define temp_modules %{temp_root}%{_modulesdir}


PrepareKernel() {
	name=$1
	extension=$2
	echo "Make dep for kernel $extension"
	%smake -s mrproper

	if [ -z "$name" ]; then
		cp arch/x86/configs/%{_arch}_defconfig-desktop .config
	else
		cp arch/x86/configs/%{_arch}_defconfig-$name .config
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

	cp -f arch/%{_arch}/boot/bzImage %{temp_boot}/vmlinuz-$KernelVer

	# modules
	install -d %{temp_modules}/$KernelVer
	%smake INSTALL_MOD_PATH=%{temp_root} KERNELRELEASE=$KernelVer modules_install

	# remove /lib/firmware, we use a separate kernel-firmware
	rm -rf %{temp_root}/lib/firmware
}


SaveDevel() {
	devel_flavour=$1

	DevelRoot=/usr/src/%{kversion}-%{ktag}-$devel_flavour-%{buildrpmrel}
	TempDevelRoot=%{temp_root}$DevelRoot

	mkdir -p $TempDevelRoot
	for i in $(find . -name 'Makefile*'); do cp -R --parents $i $TempDevelRoot;done
	for i in $(find . -name 'Kconfig*' -o -name 'Kbuild*' -o -name config.mk); do cp -R --parents $i $TempDevelRoot;done
	cp -fR include $TempDevelRoot
	cp -fR scripts $TempDevelRoot
	%ifarch %{ix86} x86_64
		cp -fR arch/x86/kernel/asm-offsets.{c,s} $TempDevelRoot/arch/x86/kernel/
		cp -fR arch/x86/kernel/asm-offsets_{32,64}.c $TempDevelRoot/arch/x86/kernel/
		cp -fR arch/x86/include $TempDevelRoot/arch/x86/
	%else
		cp -fR arch/%{_arch}/kernel/asm-offsets.{c,s} $TempDevelRoot/arch/%{_arch}/kernel/
		cp -fR arch/%{_arch}/include $TempDevelRoot/arch/%{_arch}/
	%endif
	cp -fR kernel/bounds.c $TempDevelRoot/kernel/
	cp -fR .config Module.symvers $TempDevelRoot
#	cp -fR 3rdparty/mkbuild.pl $TempDevelRoot/3rdparty/

	# Needed for truecrypt build (Danny)
	cp -fR drivers/md/dm.h $TempDevelRoot/drivers/md/

	# Needed for lguest
	cp -fR drivers/lguest/lg.h $TempDevelRoot/drivers/lguest/

	# Needed for lirc_gpio (Anssi Hannula, #39004, #54907)
	cp -fR drivers/media/video/bt8xx/bttv{,p}.h $TempDevelRoot/drivers/media/video/bt8xx/
	cp -fR drivers/media/video/bt8xx/bt848.h $TempDevelRoot/drivers/media/video/bt8xx/
	cp -fR drivers/media/video/btcx-risc.h $TempDevelRoot/drivers/media/video/

	# Needed for external dvb tree (#41418)
	cp -fR drivers/media/dvb/dvb-core/*.h $TempDevelRoot/drivers/media/dvb/dvb-core/
	cp -fR drivers/media/dvb/frontends/lgdt330x.h $TempDevelRoot/drivers/media/dvb/frontends/

	# add acpica header files, needed for fglrx build
	cp -fR drivers/acpi/acpica/*.h $TempDevelRoot/drivers/acpi/acpica/

	for i in alpha arm arm26 avr32 blackfin cris frv h8300 ia64 microblaze mips m32r m68k \
		 m68knommu mn10300 parisc powerpc ppc s390 sh sh64 score sparc v850 xtensa; do
		rm -rf $TempDevelRoot/arch/$i
	done

	%ifnarch %{ix86} x86_64
		rm -rf $TempDevelRoot/arch/x86
	%endif
	# disable removal of asm-offsets.h and bounds.h
	patch -p1 -d $TempDevelRoot -i %{SOURCE6}

	# Clean the scripts tree, and make sure everything is ok (sanity check)
	# running prepare+scripts (tree was already "prepared" in build)
	pushd $TempDevelRoot >/dev/null
		%smake -s prepare scripts clean
	popd >/dev/null

	rm -f $TempDevelRoot/.config.old

	# fix permissions
	chmod -R a+rX $TempDevelRoot

	# disable mrproper in -devel rpms
	patch -p1 -d $TempDevelRoot -i %{SOURCE2}
	# disable the rest of the scripts in -devel rpms
	patch -p1 -d $TempDevelRoot -i %{SOURCE3}

	kernel_devel_files=../kernel_devel_files.$devel_flavour


### Create the kernel_devel_files.*
cat > $kernel_devel_files <<EOF
%defattr(-,root,root)
%dir $DevelRoot
%dir $DevelRoot/arch
%dir $DevelRoot/include
#$DevelRoot/3rdparty
$DevelRoot/Documentation
$DevelRoot/arch/Kconfig
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
$DevelRoot/include/asm-generic
$DevelRoot/include/config
$DevelRoot/include/crypto
$DevelRoot/include/drm
$DevelRoot/include/generated
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
$DevelRoot/virt
$DevelRoot/.config
$DevelRoot/Kbuild
$DevelRoot/Makefile
$DevelRoot/Module.symvers
%doc README.MandrivaLinux
%doc README.kernel-sources
EOF


### Create -devel Post script on the fly
cat > $kernel_devel_files-post <<EOF
if [ -d /lib/modules/%{kversion}-%{ktag}-$devel_flavour-%{buildrpmrel} ]; then
	rm -f /lib/modules/%{kversion}-%{ktag}-$devel_flavour-%{buildrpmrel}/{build,source}
	ln -sf $DevelRoot /lib/modules/%{kversion}-%{ktag}-$devel_flavour-%{buildrpmrel}/build
	ln -sf $DevelRoot /lib/modules/%{kversion}-%{ktag}-$devel_flavour-%{buildrpmrel}/source
fi
EOF


### Create -devel Preun script on the fly
cat > $kernel_devel_files-preun <<EOF
if [ -L /lib/modules/%{kversion}-%{ktag}-$devel_flavour-%{buildrpmrel}/build ]; then
	rm -f /lib/modules/%{kversion}-%{ktag}-$devel_flavour-%{buildrpmrel}/build
fi
if [ -L /lib/modules/%{kversion}-%{ktag}-$devel_flavour-%{buildrpmrel}$devel_cpu/source ]; then
	rm -f /lib/modules/%{kversion}-%{ktag}-$devel_flavour-%{buildrpmrel}/source
fi
exit 0
EOF
}


CreateFiles() {
	kernel_flavour=$1

	kernel_files=../kernel_files.$kernel_flavour


### Create the kernel_files.*
cat > $kernel_files <<EOF
%defattr(-,root,root)
%{_bootdir}/System.map-%{kversion}-%{ktag}-$kernel_flavour-%{buildrpmrel}
%{_bootdir}/config-%{kversion}-%{ktag}-$kernel_flavour-%{buildrpmrel}
%{_bootdir}/vmlinuz-%{kversion}-%{ktag}-$kernel_flavour-%{buildrpmrel}
%dir %{_modulesdir}/%{kversion}-%{ktag}-$kernel_flavour-%{buildrpmrel}/
%{_modulesdir}/%{kversion}-%{ktag}-$kernel_flavour-%{buildrpmrel}/kernel
%{_modulesdir}/%{kversion}-%{ktag}-$kernel_flavour-%{buildrpmrel}/modules.*
%doc README.Mandriva_Linux_%{ktag}
%doc README.kernel-%{ktag}-sources
EOF


### Create kernel Post script
cat > $kernel_files-post <<EOF
/sbin/installkernel -L %{kversion}-%{ktag}-$kernel_flavour-%{buildrpmrel}
pushd /boot > /dev/null
if [ -L vmlinuz-%{ktag}-$kernel_flavour ]; then
	rm -f vmlinuz-%{ktag}-$kernel_flavour
fi
ln -sf vmlinuz-%{kversion}-%{ktag}-$kernel_flavour-%{buildrpmrel} vmlinuz-%{ktag}-$kernel_flavour
if [ -L initrd-%{ktag}-$kernel_flavour.img ]; then
	rm -f initrd-%{ktag}-$kernel_flavour.img
fi
ln -sf initrd-%{kversion}-%{ktag}-$kernel_flavour-%{buildrpmrel}.img initrd-%{ktag}-$kernel_flavour.img
popd > /dev/null
%if %build_devel
# create kernel-devel symlinks if matching -devel- rpm is installed
if [ -d /usr/src/%{kversion}-%{ktag}-$kernel_flavour-%{buildrpmrel} ]; then
	rm -f /lib/modules/%{kversion}-%{ktag}-$kernel_flavour-%{buildrpmrel}/{build,source}
	ln -sf /usr/src/%{kversion}-%{ktag}-$kernel_flavour-%{buildrpmrel} /lib/modules/%{kversion}-%{ktag}-$kernel_flavour-%{buildrpmrel}/build
	ln -sf /usr/src/%{kversion}-%{ktag}-$kernel_flavour-%{buildrpmrel} /lib/modules/%{kversion}-%{ktag}-$kernel_flavour-%{buildrpmrel}/source
fi
%endif
%if %build_source
# create kernel-source symlinks only if matching -devel- rpm is not installed
if [ -d /usr/src/%{kversion}-%{ktag}-%{buildrpmrel} -a ! -d /usr/src/%{kversion}-%{ktag}-$kernel_flavour-%{buildrpmrel} ]; then
	rm -f /lib/modules/%{kversion}-%{ktag}-$kernel_flavour-%{buildrpmrel}/{build,source}
	ln -sf /usr/src/%{kversion}-%{ktag}-%{buildrpmrel} /lib/modules/%{kversion}-%{ktag}-$kernel_flavour-%{buildrpmrel}/build
	ln -sf /usr/src/%{kversion}-%{ktag}-%{buildrpmrel} /lib/modules/%{kversion}-%{ktag}-$kernel_flavour-%{buildrpmrel}/source
fi
%endif
EOF


### Create kernel Preun script on the fly
cat > $kernel_files-preun <<EOF
/sbin/installkernel -R %{kversion}-%{ktag}-$kernel_flavour-%{buildrpmrel}
pushd /boot > /dev/null
if [ -L vmlinuz-%{ktag}-$kernel_flavour ]; then
	if [ "$(readlink vmlinuz-%{ktag}-$kernel_flavour)" = "vmlinuz-%{kversion}-%{ktag}-$kernel_flavour-%{buildrpmrel}" ]; then
		rm -f vmlinuz-%{ktag}-$kernel_flavour
	fi
fi
if [ -L initrd-%{ktag}-$kernel_flavour.img ]; then
	if [ "$(readlink initrd-%{ktag}-$kernel_flavour.img)" = "initrd-%{kversion}-%{ktag}-$kernel_flavour-%{buildrpmrel}.img" ]; then
		rm -f initrd-%{ktag}-$kernel_flavour.img
	fi
fi
popd > /dev/null
%if %build_devel
if [ -L /lib/modules/%{kversion}-%{ktag}-$kernel_flavour-%{buildrpmrel}/build ]; then
	rm -f /lib/modules/%{kversion}-%{ktag}-$kernel_flavour-%{buildrpmrel}/build
fi
if [ -L /lib/modules/%{kversion}-%{ktag}-$kernel_flavour-%{buildrpmrel}/source ]; then
	rm -f /lib/modules/%{kversion}-%{ktag}-$kernel_flavour-%{buildrpmrel}/source
fi
%endif
exit 0
EOF


### Create kernel Postun script on the fly
cat > $kernel_files-postun <<EOF
/sbin/kernel_remove_initrd %{kversion}-%{ktag}-$kernel_flavour-%{buildrpmrel}
EOF
}


CreateKernel() {
	flavour=$1

	PrepareKernel $flavour %{ktag}-$flavour-%{buildrpmrel}

	BuildKernel %{kversion}-%{ktag}-$flavour-%{buildrpmrel}
	%if %build_devel
		SaveDevel $flavour
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


# kernel-source is shipped as a clean source tree, with no preparation
%if %build_source
    PrepareKernel "" %{buildrpmrel}%{ktag}custom
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
for i in alpha arm arm26 avr32 blackfin cris frv h8300 ia64 microblaze mips m32r m68k \
	 m68knommu mn10300 parisc powerpc ppc s390 sh sh64 score sparc v850 xtensa; do
	rm -rf %{target_source}/arch/$i
done

%ifnarch %{ix86} x86_64
	rm -rf %{target_source}/arch/x86
%endif

# other misc files
rm -f %{target_source}/{.config.old,.config.cmd,.mailmap,.missing-syscalls.d,arch/.gitignore}

#endif %build_source
%endif

# We used to have a copy of PrepareKernel here
# Now, we make sure that the thing in the linux dir is what we want it to be
for i in %{target_modules}/*; do
    rm -f $i/build $i/source
done

# Create modules.description
pushd %{target_modules}
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
%{_kerneldir}/samples
%{_kerneldir}/scripts
%{_kerneldir}/security
%{_kerneldir}/sound
%{_kerneldir}/tools
%{_kerneldir}/usr
%{_kerneldir}/virt
%{_kerneldir}/.gitignore
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

