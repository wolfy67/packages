# Define the kmod package name here.
%define	 kmod_name rt3070sta

# If kversion isn't defined on the rpmbuild line, define it here.
%{!?kversion: %define kversion 2.6.18-8.el5}

Name:	 %{kmod_name}-kmod
Version: 2.5.0.1
Release: 1%{?dist}
Group:	 System Environment/Kernel
License: GPLv2
Summary: Ralink %{kmod_name} driver module
URL:	 http://www.ralinktech.com.tw/data/drivers/2011_0107_RT3070_RT3370_Linux_STA_v2.5.0.1_DPO.tgz

BuildRequires: redhat-rpm-config
BuildRoot:     %{_tmppath}/%{name}-%{version}-%{release}-build-%(%{__id_u} -n)
ExclusiveArch: i686 x86_64

# Sources.
Source0:  2011_0107_RT3070_RT3370_Linux_STA_v2.5.0.1_DPO.tgz
Source5:  GPL-v2.0.txt
Source10: kmodtool-%{kmod_name}-el5.sh

# Patches.
Patch0: rt3070sta-unspecified-license.patch

# Define the variants for each architecture.
%define basevar ""
%ifarch i686
%define paevar PAE
%endif
%ifarch i686 x86_64
%define xenvar xen
%endif

# If kvariants isn't defined on the rpmbuild line, build all variants for this architecture.
%{!?kvariants: %define kvariants %{?basevar} %{?xenvar} %{?paevar}}

# Magic hidden here.
%{expand:%(sh %{SOURCE10} rpmtemplate_kmp %{kmod_name} %{kversion} %{kvariants})}

# Disable the building of the debug package(s).
%define debug_package %{nil}

# Define the filter.
%define __find_requires sh %{_builddir}/%{buildsubdir}/filter-requires.sh

%description
This package provides the %{kmod_name} kernel module(s) for the
RaLink RT8070/RT3070/RT3370 wireless USB series network adapters.
It is built to depend upon the specific ABI provided by a range of releases
of the same variant of the Linux kernel and not on any one specific build.

%prep
%setup -q -c -T -a 0
%patch0 -p0
pushd 2011_0107_RT3070_RT3370_Linux_STA_v2.5.0.1_DPO
%{__perl} -pi -e 's|(.*tftpboot$)|#$1|g' Makefile
%{__perl} -pi -e 's|HAS_WPA_SUPPLICANT=n|HAS_WPA_SUPPLICANT=y|g;
                  s|HAS_NATIVE_WPA_SUPPLICANT_SUPPORT=n|HAS_NATIVE_WPA_SUPPLICANT_SUPPORT=y|g' \
           os/linux/config.mk
popd
for kvariant in %{kvariants} ; do
    %{__cp} -a 2011_0107_RT3070_RT3370_Linux_STA_v2.5.0.1_DPO _kmod_build_$kvariant
done
%{__cp} -a %{SOURCE5} .
echo "/usr/lib/rpm/redhat/find-requires | %{__sed} -e '/^ksym.*/d'" > filter-requires.sh
echo "override %{kmod_name} * weak-updates/%{kmod_name}" > kmod-%{kmod_name}.conf

%build
for kvariant in %{kvariants} ; do
    pushd _kmod_build_$kvariant
    %{__make} LINUX_SRC=%{_usrsrc}/kernels/%{kversion}${kvariant:+-$kvariant}-%{_target_cpu}
    popd
done

%install
%{__rm} -rf %{buildroot}
for kvariant in %{kvariants} ; do
    pushd _kmod_build_$kvariant
    %{__install} -d %{buildroot}/lib/modules/%{kversion}${kvariant}/extra/%{kmod_name}/
    %{__install} os/linux/rt3070sta.ko %{buildroot}/lib/modules/%{kversion}${kvariant}/extra/%{kmod_name}/
    %{__install} -d %{buildroot}%{_sysconfdir}/Wireless/RT2870STA/
    %{__install} RT2870STA.dat %{buildroot}%{_sysconfdir}/Wireless/RT2870STA/
    %{__install} RT2870STACard.dat %{buildroot}%{_sysconfdir}/Wireless/RT2870STA/
    %{__install} -d %{buildroot}%{_defaultdocdir}/kmod-%{kmod_name}-%{version}/
    # Install docs
    %{__install} *.txt %{buildroot}%{_defaultdocdir}/kmod-%{kmod_name}-%{version}/
    %{__install} README_STA_usb %{buildroot}%{_defaultdocdir}/kmod-%{kmod_name}-%{version}/
    popd
    %{__install} GPL-v2.0.txt %{buildroot}%{_defaultdocdir}/kmod-%{kmod_name}-%{version}/
    %{__install} -d %{buildroot}%{_sysconfdir}/depmod.d/
    %{__install} kmod-%{kmod_name}.conf %{buildroot}%{_sysconfdir}/depmod.d/
done
# Set the module(s) to be executable, so that they will be stripped when packaged.
find %{buildroot} -type f -name \*.ko -exec %{__chmod} u+x \{\} \;

%clean
%{__rm} -rf %{buildroot}

%changelog
* Mon May 02 2011 Philip J Perry <phil@elrepo.org> - 2.5.0.1-1.el5.elrepo
- Update to version 2.5.0.1.
- Fix module license 'unspecified' taints kernel [rt3070sta-unspecified-license.patch]
  [http://elrepo.org/bugs/view.php?id=121]

* Mon Oct 04 2010 Philip J Perry <phil@elrepo.org> - 2.1.1.0-2.el5.elrepo
- Provide missing RT2870STA.dat [elrepo BugID 000032]
- Add dependency for rt2870-firmware
- Add Conflicts for module-init-tools-3.3-0.pre3.1.60.el5 [BugID 0000064]

* Sun Sep 06 2009 Philip J Perry <phil@elrepo.org> - 2.1.1.0-1.el5.elrepo
- Initial build of the kmod package.
- Patch makefile to build against kernel variants. [rt3070-makefile.patch]
- Patch config.mk to build for wpa_supplicant support. [rt3070-config-wpa-supplicant.patch]
