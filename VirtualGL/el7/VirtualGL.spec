# This package provides VirtualGL for RHEL7.
# The main (64-bit) package should be built as normal in mock.
# The 32-bit libs package can not be built in mock as there is no 32-bit tree
# The 32-bit package must be built using 'rpmbuild -ba --target=i686 VirtualGL.spec'
# The 32-bit BuildRequires will need to be installed on the build host before building.

%define		debug_package	%{nil}

Summary:        A toolkit for displaying OpenGL applications to thin clients
Name:           VirtualGL
Version:        2.3.3
Release:        4%{?dist}
Group:          Applications/System
License:        wxWidgets
URL:            http://www.virtualgl.org/

BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-build-%(%{__id_u} -n)
ExclusiveArch:	i686 x86_64

Source0:        http://downloads.sourceforge.net/project/virtualgl/VirtualGL/%{version}/VirtualGL-%{version}.tar.gz
Source1:	VirtualGL32.conf
Source2:	VirtualGL64.conf

# Use system fltk
Patch0:		%{name}-fltk.patch
# Use system glx.h
Patch1:         %{name}-glx.patch
# fix for bz923961
Patch2:		%{name}-redhatpathsfix.patch

BuildRequires:	cmake
BuildRequires:	gcc-c++

# The rest of the BRs need to be arch specific
## glib
BuildRequires:	glibc-devel%{?_isa}
BuildRequires:	nss-softokn-freebl%{?_isa}
BuildRequires:	libgcc%{?_isa}
BuildRequires:	libstdc++-devel%{?_isa}
## X11
BuildRequires:	libX11-devel%{?_isa}
BuildRequires:	libXext-devel%{?_isa}
BuildRequires:	mesa-libGL-devel%{?_isa}
BuildRequires:	mesa-libGLU-devel%{?_isa}
BuildRequires:	libXv-devel%{?_isa}
## other libs
BuildRequires:	fltk-devel%{?_isa}
BuildRequires:	openssl-devel%{?_isa}
BuildRequires:	turbojpeg-devel%{?_isa}

Requires:	fltk
Provides:	bumblebee-bridge

%description
VirtualGL is a toolkit that allows most Unix/Linux OpenGL applications to be
remotely displayed with hardware 3D acceleration to thin clients, regardless
of whether the clients have 3D capabilities, and regardless of the size of the
3D data being rendered or the speed of the network.

Using the vglrun script, the VirtualGL "faker" is loaded into an OpenGL
application at run time.  The faker then intercepts a handful of GLX calls,
which it reroutes to the server's X display (the "3D X Server", which
presumably has a 3D accelerator attached.)  The GLX commands are also
dynamically modified such that all rendering is redirected into a Pbuffer
instead of a window.  As each frame is rendered by the application, the faker
reads back the pixels from the 3D accelerator and sends them to the
"2D X Server" for compositing into the appropriate X Window.

VirtualGL can be used to give hardware-accelerated 3D capabilities to VNC or
other X proxies that either lack OpenGL support or provide it through software
rendering.  In a LAN environment, VGL can also be used with its built-in
high-performance image transport, which sends the rendered 3D images to a
remote client (vglclient) for compositing on a remote X server.  VirtualGL
also supports image transport plugins, allowing the rendered 3D images to be
sent or captured using other mechanisms.

VirtualGL is based upon ideas presented in various academic papers on
this topic, including "A Generic Solution for Hardware-Accelerated Remote
Visualization" (Stegmaier, Magallon, Ertl 2002) and "A Framework for
Interactive Hardware Accelerated Remote 3D-Visualization" (Engel, Sommer,
Ertl 2000.)

%ifarch x86_64
%package devel
Summary:	Development headers and libraries for VirtualGL
Requires:	%{name}%{?_isa} = %{version}-%{release}
Requires:	openssl-devel%{?_isa}
Requires:	turbojpeg-devel%{?_isa}
Requires:	mesa-libGLU-devel%{?_isa}
Requires:	libXv-devel%{?_isa}

%description devel
Development headers and libraries for VirtualGL.
%endif

%ifarch i686
%package libs
Summary:	32-Bit libraries for VirtualGL
Requires:	%{name} = %{version}
Requires:	glibc%{?_isa}
Requires:	libX11%{?_isa}
Requires:	libXext%{?_isa}
Requires:	libXv%{?_isa}
Requires:	openssl-libs%{?_isa}
Requires:	libstdc++%{?_isa}
Requires:	turbojpeg%{?_isa}

%description libs
This package contains the 32-bit libraries for VirtualGL.
%endif

%prep
%setup -q
%patch0 -p1 -b .fltk
%patch1 -p1 -b .glx
%patch2 -p1 -b .redhatpathsfix

sed -i -e 's,"glx.h",<GL/glx.h>,' server/*.[hc]*
# Remove bundled libraries
rm -r client/{putty,x11windows} common/glx* include/FL server/fltk
rm doc/LICENSE-*.txt

%build
%cmake   -DTJPEG_INCLUDE_DIR=%{_includedir} \
         -DTJPEG_LIBRARY=%{_libdir}/libturbojpeg.so \
         -DVGL_USESSL=ON -DVGL_LIBDIR=%{_libdir} \
         -DVGL_DOCDIR=%{_docdir}/%{name}/ \
         -DVGL_LIBDIR=%{_libdir}/VirtualGL/ \
         -DVGL_FAKELIBDIR=%{_libdir}/fakelib/ .
make %{?_smp_mflags}

%install
make install DESTDIR=$RPM_BUILD_ROOT
rm $RPM_BUILD_ROOT%{_bindir}/glxinfo
%ifarch i686
rm $RPM_BUILD_ROOT%{_includedir}/*.h
%endif
ln -sf %{_libdir}/VirtualGL/librrfaker.so $RPM_BUILD_ROOT%{_libdir}/fakelib/libGL.so

# Install the ld.so.conf.d files
%{__mkdir_p} $RPM_BUILD_ROOT%{_sysconfdir}/ld.so.conf.d/
%ifarch i686
%{__install} -p -m 0644 %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/ld.so.conf.d/VirtualGL32.conf
%endif
%ifarch x86_64
%{__install} -p -m 0644 %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/ld.so.conf.d/VirtualGL64.conf
%endif

%clean
%{__rm} -rf $RPM_BUILD_ROOT

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%ifarch i686
%post libs
/sbin/ldconfig

%postun libs
/sbin/ldconfig
%endif

%files
%defattr(-,root,root,-)
%{_docdir}/%{name}/
%{_bindir}/tcbench
%{_bindir}/nettest
%{_bindir}/cpustat
%{_bindir}/vglclient
%{_bindir}/vglconfig
%{_bindir}/vglconnect
%{_bindir}/vglgenkey
%{_bindir}/vgllogin
%{_bindir}/vglserver_config
%{_bindir}/vglrun
%{_bindir}/glreadtest
%{_libdir}/VirtualGL/
%{_libdir}/fakelib/
%ifarch x86_64
%config %{_sysconfdir}/ld.so.conf.d/VirtualGL64.conf
%{_bindir}/glxspheres64
%{_bindir}/.vglrun.vars64
%endif

%ifarch x86_64
%files devel
%{_includedir}/rrtransport.h
%{_includedir}/rr.h
%endif

%ifarch i686
%files libs
%defattr(-,root,root,-)
%config %{_sysconfdir}/ld.so.conf.d/VirtualGL32.conf
%{_bindir}/glxspheres
%{_bindir}/.vglrun.vars32
%{_libdir}/VirtualGL/
%{_libdir}/fakelib/
%endif

%changelog
* Mon Dec 01 2014 Philip J Perry <phil@elrepo.org> - 2.3.3-4
- Build 32-bit libs package for RHEL7
  [http://elrepo.org/bugs/view.php?id=537]

* Tue Jun 10 2014 Rob Mokkink <rob@mokkinksystems.com> - 2.3.3-3
- Rebuild for elrepo el7
- Added build requirement gcc-c++, to prevent cmake errors

* Thu Nov 7 2013 Dan Horák <dan[at]danny.cz> - 2.3.3-2
- fix build on non-x86 arches

* Sat Nov 2 2013 Gary Gatling <gsgatlin@eos.ncsu.edu> - 2.3.3-1
- Update to 2.3.3.

* Tue Aug 6 2013 Gary Gatling <gsgatlin@eos.ncsu.edu> - 2.3.2-7
- Fix (#993894) unversioned docdir change for f20.

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.3.2-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Mon May 6 2013 Gary Gatling <gsgatlin@eos.ncsu.edu> - 2.3.2-5
- Fix (#923961) More path changes to vglrun to really fix issue.

* Sun Mar 24 2013 Gary Gatling <gsgatlin@eos.ncsu.edu> - 2.3.2-4
- Fix (#923961) Change /opt/VirtualGL/bin to /usr/bin in vglconnect.
- Add virtual provides for bumblebee-bridge package.

* Wed Feb 20 2013 Adam Tkac <atkac redhat com> - 2.3.2-3
- rebuild

* Thu Jan 17 2013 Gary Gatling <gsgatlin@eos.ncsu.edu> - 2.3.2-1
- rebuilding.

* Sun Jan 13 2013 Gary Gatling <gsgatlin@eos.ncsu.edu> - 2.3.2-2
- update to 2.3.2.

* Tue Oct 23 2012 Gary Gatling <gsgatlin@eos.ncsu.edu> - 2.3.1-9
- Fix problems with multilib support. Fix created by Andy Kwong.

* Sun Jul 22 2012 Gary Gatling <gsgatlin@eos.ncsu.edu> - 2.3.1-8
- removed BuildRequires:  mxml-devel. see BZ839060. (#839060)

* Sat Jul 14 2012 Gary Gatling <gsgatlin@eos.ncsu.edu> - 2.3.1-7
- added BuildRequires:  mxml-devel for fedora builds only.

* Thu Jul 12 2012 Gary Gatling <gsgatlin@eos.ncsu.edu> - 2.3.1-6
- removed BuildArch: noarch from "devel" subpackage

* Thu Jul 12 2012 Gary Gatling <gsgatlin@eos.ncsu.edu> - 2.3.1-5
- change to cmake macros in the build section of specfile

* Tue Jul 10 2012 Gary Gatling <gsgatlin@eos.ncsu.edu> - 2.3.1-4
- fix vglrun patch to use uname -i to determine platform.
- fix cmake macro problems on rhel 6.
- remove Vendor tag from specfile

* Tue Jul 10 2012 Orion Poplawski <orion@nwra.com> - 2.3.1-3
- Use system glx, fltk
- Don't ship glxinfo

* Fri Jul 6 2012 Gary Gatling <gsgatlin@eos.ncsu.edu> - 2.3.1-2
- Added patch for library paths within the vglrun script.

* Thu Jul 5 2012 Gary Gatling <gsgatlin@eos.ncsu.edu> - 2.3.1-1
- Upgrade to 2.3.1 and made changes to better follow packaging guidelines for fedora project.

* Wed Jun 6 2012 Gary Gatling <gsgatlin@eos.ncsu.edu> - 2.3-2
- Very minor edit for building on RHEL 6 with the same specfile as newer fedora.

* Thu Feb 16 2012 Robin Lee <cheeselee@fedoraproject.org> - 2.3-1
- Specfile based on upstream and Mandriva specfiles
