%global includetests 0
# 0=no, 1=yes
%global cryptlibdir %{_libdir}/%{name}
# The python3 subpackage cannot be build, because DL_EXPORT is missing in Python.h
%global with_python3 0

Name:       cryptlib
Version:    3.4.3  
Release:    6%{?dist}
Summary:    Security library and toolkit for encryption and authentication services    

Group:      System Environment/Libraries         
License:    Sleepycat       
URL:        https://www.cs.auckland.ac.nz/~pgut001/cryptlib      
Source0:    https://crypto-bone.com/fedora/cl343_fedora.zip      
Source1:    https://crypto-bone.com/fedora/cl343_fedora.zip.sig
# for security reasons a public signing key should always be stored in distgit
# and never be used with a URL to make impersonation attacks harder
# (verified: https://senderek.ie/keys/codesigningkey)
Source2:    gpgkey-3274CB29956498038A9C874BFBF6E2C28E9C98DD.asc
Source3:    https://crypto-bone.com/fedora/README-manual
Source4:    https://crypto-bone.com/fedora/cryptlib-tests.tar.gz
Source5:    https://crypto-bone.com/fedora/cryptlib-perlfiles.tar.gz

Patch1:     sonamepatch
# soname is now libcl.so.3
Patch2:     ccflagspatch
Patch3:     sessionpatch
Patch4:     utilspatch
Patch5:     stackprotectorstrongpatch
Patch6:     javapatch
Patch7:     testlibpatch

ExclusiveArch: x86_64 %{ix86} %{arm}

BuildRequires: gcc 
BuildRequires: libbsd-devel   
BuildRequires: gnupg2
BuildRequires: coreutils
BuildRequires: python >= 2.7
BuildRequires: python2-devel >= 2.7
%if %{with_python3}
BuildRequires: python3-devel
%endif
BuildRequires: java-devel
BuildRequires: perl
BuildRequires: perl-devel
%if 0%{?fedora} >= 23
BuildRequires: perl-generators
%endif
BuildRequires: perl-Data-Dumper
BuildRequires: perl-ExtUtils-MakeMaker


# beignet provides a library libcl.so for OpenCL
Conflicts: beignet

%description
Cryptlib is a powerful security toolkit that allows even inexperienced crypto
programmers to easily add encryption and authentication services to their
software. The high-level interface provides anyone with the ability to add
strong security capabilities to an application in as little as half an hour,
without needing to know any of the low-level details that make the encryption
or authentication work.  Because of this, cryptlib dramatically reduces the
cost involved in adding security to new or existing applications.

At the highest level, cryptlib provides implementations of complete security
services such as S/MIME and PGP/OpenPGP secure enveloping, SSL/TLS and
SSH secure sessions, CA services such as CMP, SCEP, RTCS, and OCSP, and other
security operations such as secure time-stamping. Since cryptlib uses
industry-standard X.509, S/MIME, PGP/OpenPGP, and SSH/SSL/TLS data formats,
the resulting encrypted or signed data can be easily transported to other
systems and processed there, and cryptlib itself runs on virtually any
operating system - cryptlib doesn't tie you to a single system.
This allows email, files and EDI transactions to be authenticated with
digital signatures and encrypted in an industry-standard format.


%package devel
Summary:  Cryptlib application development files 
Requires: %{name}%{?_isa} = %{version}-%{release}

%description devel
Header files and code for application development in C (and C++)


%package test
Summary:  Cryptlib test program
Requires: %{name}%{?_isa} = %{version}-%{release}

%description test
Cryptlib test programs for C, Java, Perl and Python


%package java
Summary:  Cryptlib bindings for Java
Requires: %{name}%{?_isa} = %{version}-%{release}
Requires: java-headless

%description java
Cryptlib module for application development in Java


%package javadoc
Summary:  Cryptlib Java documentation
Buildarch : noarch

%description javadoc
Cryptlib Javadoc information


%package python2
Summary:  Cryptlib bindings for python2
Group:    System Environment/Libraries
Requires: %{name}%{?_isa} = %{version}-%{release}
Requires: python >= 2.7

%description python2
Cryptlib module for application development in Python 2


# The python3 subpackage cannot be build, because DL_EXPORT is missing in Python.h
# so python3 setup.py build fails

%if %{with_python3}
     %package python3
     Summary:  Cryptlib bindings for python3
     Group:    System Environment/Libraries
     Requires: %{name}%{?_isa} = %{version}-%{release}
     # specify the python3 version which first provides DL_EXPORT support below
     Requires: python >= 3.x  

     %description python3
     Cryptlib module for application development in Python 3
%endif

%package perl
Summary:  Cryptlib bindings for perl
Group:    System Environment/Libraries
Requires: %{name}%{?_isa} = %{version}-%{release}
Requires: man

%description perl
Cryptlib module for application development in Perl



%prep
# source code signature check with GnuPG
KEYRING=$(echo %{SOURCE2})
KEYRING=${KEYRING%%.asc}.gpg
mkdir -p .gnupg
gpg2 --homedir .gnupg --no-default-keyring --quiet --yes --output $KEYRING --dearmor  %{SOURCE2}
gpg2 --homedir .gnupg --no-default-keyring --keyring $KEYRING --verify %{SOURCE1} %{SOURCE0}

rm -rf %{name}-%{version}
mkdir %{name}-%{version}
cd %{name}-%{version}
/usr/bin/unzip -a %{SOURCE0}
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch6 -p1
%patch7 -p1
# remove pre-build jar file
rm %{_builddir}/%{name}-%{version}/bindings/cryptlib.jar
# adapt perl files in bindings
cd %{_builddir}/%{name}-%{version}/bindings
/usr/bin/tar xpzf %{SOURCE5}


%build
cd %{name}-%{version}
# build java bindings
chmod +x tools/mkhdr.sh
tools/mkhdr.sh
cp /etc/alternatives/java_sdk/include/jni.h .
cp /etc/alternatives/java_sdk/include/linux/jni_md.h .

make clean
make shared %{?_smp_mflags} ADDFLAGS="%{optflags}"
make stestlib %{?_smp_mflags} ADDFLAGS="%{optflags}"

# build python modules
ln -s libcl.so.3.4.3 libcl.so
cd bindings
python2 setup.py build

# DL_EXPORT is missing in Python.h, so the following build fails.
# We need to disable the python3 subpackage until this problem is resolved.
%if %{with_python3}
     python3 setup.py build
%endif

# build javadoc
mkdir javadoc
cd javadoc
jar -xf ../cryptlib.jar
javadoc cryptlib


%install
mkdir -p %{buildroot}%{_libdir}
mkdir -p %{buildroot}%{_datadir}/licenses/%{name}
mkdir -p %{buildroot}%{_docdir}/%{name}
cp %{_builddir}/%{name}-%{version}/libcl.so.3.4.3 %{buildroot}%{_libdir}
cd %{buildroot}%{_libdir}
ln -s libcl.so.3.4.3 libcl.so.3
ln -s libcl.so.3 libcl.so

# install header files
mkdir -p %{buildroot}/%{_includedir}/%{name}
cp %{_builddir}/%{name}-%{version}/crypt.h %{buildroot}%{_includedir}/%{name}
cp %{_builddir}/%{name}-%{version}/cryptkrn.h %{buildroot}%{_includedir}/%{name}
cp %{_builddir}/%{name}-%{version}/cryptlib.h %{buildroot}%{_includedir}/%{name}

# add Java bindings
mkdir -p %{buildroot}/%{cryptlibdir}/java
mkdir -p %{buildroot}/%{_jnidir}
cp %{_builddir}/%{name}-%{version}/bindings/cryptlib.jar %{buildroot}%{_jnidir}

# install docs
cp %{_builddir}/%{name}-%{version}/COPYING %{buildroot}%{_datadir}/licenses/%{name}
cp %{_builddir}/%{name}-%{version}/README %{buildroot}%{_docdir}/%{name}/README
echo "No tests performed." > %{_builddir}/%{name}-%{version}/stestlib.log
cp %{_builddir}/%{name}-%{version}/stestlib.log %{buildroot}%{_docdir}/%{name}/stestlib.log
cp %{SOURCE3} %{buildroot}%{_docdir}/%{name}

# install javadoc
mkdir -p %{buildroot}%{_javadocdir}/%{name}
rm -rf %{_builddir}/%{name}-%{version}/bindings/javadoc/META-INF
cp -r %{_builddir}/%{name}-%{version}/bindings/javadoc/* %{buildroot}%{_javadocdir}/%{name}

# install python2 module
mkdir -p %{buildroot}%{python2_sitelib}
cp %{_builddir}/%{name}-%{version}/bindings/build/lib.linux-*%{python2_version}/cryptlib_py.so %{buildroot}%{python2_sitelib}

# install python3 module
# add python3 installation code, when setup.py works in python3

# install Perl module
mkdir -p %{buildroot}/usr/local/lib64
mkdir -p %{buildroot}%{_libdir}/perl5
mkdir -p %{buildroot}%{_mandir}/man3
cd %{_builddir}/%{name}-%{version}/bindings
mkdir -p %{_builddir}/include
cp ../cryptlib.h %{_builddir}/include
export PERL_CRYPT_LIB_HEADER=%{_builddir}/include/cryptlib.h
/usr/bin/perl Makefile.PL
sed -i '/LDLOADLIBS = /s/thread/thread -L.. -lcl/' Makefile
make
make pure_install DESTDIR=%{buildroot}
# clean the install
rm $(find %{buildroot}/usr/local/lib*/perl5 -name ".packlist")
chmod 0755 %{buildroot}/usr/local/lib*/perl5/auto/PerlCryptLib/PerlCryptLib.so
mv %{buildroot}/usr/local/lib*/perl5/* %{buildroot}%{_libdir}/perl5
mv %{buildroot}/usr/local/share/man/man3/* %{buildroot}%{_mandir}/man3

# install test programs
cp %{_builddir}/%{name}-%{version}/stestlib %{buildroot}%{cryptlibdir}
cp -r %{_builddir}/%{name}-%{version}/test %{buildroot}%{cryptlibdir}/test
# remove all c code from the test directory
rm -rf $(find %{buildroot}%{cryptlibdir}/test -name "*.c")

## remove all header files from the test directory
# these header files are needed by the test program stestlib to find test files!
#rm -rf $(find %%{buildroot}%%{cryptlibdir}/test -name "*.h")

cd %{buildroot}%{cryptlibdir}
tar xpzf %{SOURCE4} 

%check
# checks are performed after install
# in KOJI tests must be disabled as there is no networking
%if %{includetests}
     cd %{_builddir}/%{name}-%{version}
     ln -s libcl.so.3.4.3 ./libcl.so.3
     export LD_LIBRARY_PATH=.
     echo "Running tests on the cryptlib library. This will take a few minutes."
     echo "Network access is necessary to complete all tests!"
     ./stestlib > %{_builddir}/%{name}-%{version}/stestlib.log
     cp %{_builddir}/%{name}-%{version}/stestlib.log %{buildroot}%{_docdir}/%{name}/stestlib.log
%endif


%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig


%files
%{_libdir}/libcl.so.3.4.3
%{_libdir}/libcl.so.3

%license   %{_datadir}/licenses/%{name}/COPYING
%doc       %{_docdir}/%{name}/README
%doc       %{_docdir}/%{name}/stestlib.log
%doc       %{_docdir}/%{name}/README-manual


%files devel
%{_libdir}/libcl.so
%{_includedir}/%{name}/crypt.h
%{_includedir}/%{name}/cryptkrn.h
%{_includedir}/%{name}/cryptlib.h

%files java
%{_jnidir}/cryptlib.jar

%files javadoc
%{_javadocdir}/%{name}

%files python2
%{python2_sitelib}/cryptlib_py.so

# at the moment the python3 subpackage cannot be build
%if %{with_python3}
    %files python3
%endif

%files perl
%{_libdir}/perl5
%{_mandir}/man3/PerlCryptLib.3pm.gz

%files test
%{cryptlibdir}


%changelog

* Thu Jun 16 2016 Senderek Web Security <innovation@senderek.ie> - 3.4.3-6
- Remove perl-generators for epel7
- Remove python3 script from test subpackage (fixes RHBZ #1347294)

* Tue Jun 14 2016 Senderek Web Security <innovation@senderek.ie> - 3.4.3-5
- Fix source locations
- Clean up perl file installation
- Fix python3 module code in spec file

* Thu Jun 9 2016 Senderek Web Security <innovation@senderek.ie> - 3.4.3-4
- Removed the doc subpackage

* Mon Jun 6 2016 Senderek Web Security <innovation@senderek.ie> - 3.4.3-3
- Fixed Java subpackage dependency
- Made devel arch specific

* Fri Jun 3 2016 Senderek Web Security <innovation@senderek.ie> - 3.4.3-2
- Added javadoc subpackage and made docs noarch
- Added a perl subpackage
- Modified native stestlib program with two tests disabled
  (testSessionSSH and testSessionSSHClientCert)

* Wed Jun 1 2016 Senderek Web Security <innovation@senderek.ie> - 3.4.3-1
- Added python2/python3 subpackage
- Source code signature check with GnuPG enabled

* Sun May 29 2016 Senderek Web Security <innovation@senderek.ie> - 3.4-2
- Added doc and java subpackage

* Fri May 27 2016 Senderek Web Security <innovation@senderek.ie> - 3.4-1
- Initial version of the rpm package build
