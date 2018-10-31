%{?_javapackages_macros:%_javapackages_macros}
%if 0%{?fedora}
%else
# rpm4 vs rpm5 exclude semantics...
%global _unpackaged_files_terminate_build 0
%endif

%define debug_package %{nil}

%global jruby_vendordir %{_datadir}/%{name}/lib
%global jruby_sitedir %{_prefix}/local/share/%{name}/lib
%global rubygems_dir %{_datadir}/rubygems

Name:           jruby
Version:        9.2.0.0
Release:        2
Summary:        Pure Java implementation of the Ruby interpreter
# (CPL or GPLv2+ or LGPLv2+) - JRuby itself
# BSD - some files under lib/ruby/shared
# (GPLv2 or Ruby) - Ruby 1.8 stdlib
# (BSD or Ruby) - Ruby 1.9 stdlib
License:        (CPL or GPLv2+ or LGPLv2+) and BSD and (GPLv2 or Ruby) and (BSD or Ruby)
URL:            http://jruby.org
Source0:        https://repo1.maven.org/maven2/org/jruby/jruby-dist/%{version}/jruby-dist-%{version}-src.zip

# Adds all the required jars to boot classpath
Patch0:         jruby-add-classpath-to-start-script.patch
# Adds $FEDORA_JAVA_OPTS, that is dynamically replaced by Fedora specific paths from the specfile
# This way we can use macros for the actual locations and not hardcode them in the patch
Patch1:         jruby-executable-add-fedora-java-opts-stub.patch
# We don't want any directories defined by JRuby, everything is taken from Fedora's rubygems
Patch3:         jruby-remove-rubygems-dirs-definition.patch
# Port to latest snakeyaml
# TODO: rebase for JRuby 9000 master and send upstream
#Patch4:         jruby-snakeyaml-1.16.patch

# BRs generated automatically using xmvn-builddep, sanitized manually
BuildRequires:  maven-local
BuildRequires:  mvn(bsf:bsf)
BuildRequires:  mvn(com.github.jnr:jffi)
BuildRequires:  mvn(com.github.jnr:jffi::native:)
BuildRequires:  mvn(com.github.jnr:jnr-constants)
BuildRequires:  mvn(com.github.jnr:jnr-enxio)
BuildRequires:  mvn(com.github.jnr:jnr-ffi)
BuildRequires:  mvn(com.github.jnr:jnr-netdb)
BuildRequires:  mvn(com.github.jnr:jnr-posix)
BuildRequires:  mvn(com.github.jnr:jnr-unixsocket)
BuildRequires:  mvn(com.github.jnr:jnr-x86asm)
BuildRequires:  mvn(com.headius:coro-mock)
BuildRequires:  mvn(com.headius:unsafe-mock)
BuildRequires:  mvn(com.headius:invokebinder)
BuildRequires:  mvn(com.headius:options)
BuildRequires:  mvn(com.jcraft:jzlib)
BuildRequires:  mvn(com.martiansoftware:nailgun-server)
BuildRequires:  mvn(jline:jline)
BuildRequires:  mvn(joda-time:joda-time)
BuildRequires:  mvn(junit:junit)
BuildRequires:  mvn(org.apache.ant:ant)
BuildRequires:  mvn(org.apache.felix:maven-bundle-plugin)
BuildRequires:  mvn(org.apache.felix:org.apache.felix.framework)
BuildRequires:  mvn(org.apache.maven.plugins:maven-clean-plugin)
BuildRequires:  mvn(org.apache.maven.plugins:maven-dependency-plugin)
BuildRequires:  mvn(org.apache.maven.plugins:maven-deploy-plugin)
BuildRequires:  mvn(org.apache.maven.plugins:maven-shade-plugin)
BuildRequires:  mvn(org.apache.maven.plugins:maven-site-plugin)
BuildRequires:  mvn(org.codehaus.mojo:buildnumber-maven-plugin)
BuildRequires:  mvn(org.codehaus.mojo:exec-maven-plugin)
BuildRequires:  mvn(org.codehaus.mojo:properties-maven-plugin)
BuildRequires:  mvn(org.jruby.extras:bytelist)
BuildRequires:  mvn(org.jruby.jcodings:jcodings)
BuildRequires:  mvn(org.jruby.joni:joni)
BuildRequires:  mvn(org.jruby:yecht)
BuildRequires:  mvn(org.osgi:org.osgi.core)
BuildRequires:  mvn(org.ow2.asm:asm)
BuildRequires:  mvn(org.ow2.asm:asm-analysis)
BuildRequires:  mvn(org.ow2.asm:asm-commons)
BuildRequires:  mvn(org.ow2.asm:asm-util)
BuildRequires:  mvn(org.sonatype.oss:oss-parent:pom:)
BuildRequires:  mvn(org.yaml:snakeyaml)
BuildRequires:  git
# unavailable now, see: https://bugzilla.redhat.com/show_bug.cgi?id=1152246
#BuildRequires: joda-timezones

Provides:       ruby(release) = 1.9.3
Provides:       ruby(release) = 1.8.7
# For rubypick
Provides:       ruby(runtime_executable)

BuildArch:      noarch
# yecht is in a separate package now
Obsoletes:      %{name}-yecht < %{version}-%{release}

%description
JRuby is a 100% Java implementation of the Ruby programming language.
It is Ruby for the JVM. JRuby provides a complete set of core "builtin"
classes and syntax for the Ruby language, as well as most of the Ruby
Standard Libraries.

%package        devel
Summary:        JRuby development environment
Requires:       %{name} = %{version}-%{release}

%description    devel
Macros for building JRuby-specific libraries.

%package        javadoc
Summary:        Javadoc for %{name}

%description    javadoc
Javadoc for %{name}.

%prep
%autosetup -p1

# delete windows specific files
find -name "*.exe" -delete
find -name "*.dll" -delete

# delete all vcs files
find -name ".gitignore" -delete
find -name ".cvsignore" -delete

# remove hidden .document files
find lib/ruby/ -name "*.document" -delete

# lib/ruby scripts shouldn't contain shebangs as they are not executable on their own
find lib/ruby/ -name "*.rb" -exec sed --in-place "s|^#!/usr/local/bin/ruby||" '{}' \;
find lib/ruby/ -name "*.rb" -exec sed --in-place "s|^#!/usr/bin/env ruby||" '{}' \;

# FIXME: remove when joda-timezones pkg is available in Fedora
%pom_remove_dep org.jruby:joda-timezones core

# work around "error: package org.osgi.framework.wiring does not exist"
%pom_add_dep org.apache.felix:org.apache.felix.framework core

# JDK8 should provide these
%pom_remove_dep com.headius:unsafe-mock core
%pom_remove_dep com.headius:jsr292-mock core

# do not bundle jffi-native
%pom_remove_plugin :maven-dependency-plugin core

# we don't have this plugin in fedora
%pom_remove_plugin :tesla-polyglot-maven-plugin lib

# a lot of missing "gem" artifacts, skip them for now
%pom_xpath_remove 'pom:dependencies' lib

# do not bundle other JARs inside jruby.jar
%pom_remove_plugin :maven-shade-plugin core

# generate Requires on jline dependency
%pom_xpath_replace 'pom:dependency[pom:artifactId[text()="jline"]]/pom:scope' '<scope>compile</scope>' ext/readline

# install JARs to %%{_javadir}/%%{name} and symlink them to %%{jruby_vendordir}
%mvn_file :{jruby-core}:jar:: %{name}/@1 %{jruby_vendordir}/%{name}
%mvn_file :{ripper}:jar:: %{name}/@1 %{jruby_vendordir}/ruby/shared/@1
%mvn_file :{readline}:jar:: %{name}/@1 %{jruby_vendordir}/ruby/shared/readline/@1

# TODO: build proper org.jruby:jruby artifact
%mvn_alias org.jruby:jruby-core org.jruby:jruby

%build
%mvn_build

%install
%mvn_install

install -d -m 755 %{buildroot}%{_datadir}
install -p -d -m 755 %{buildroot}%{_datadir}/%{name}/bin

# stdlib
cp -ar lib/* %{buildroot}%{jruby_vendordir}/

# symlink jffi .so files (this is pretty ugly :/)
install -d -m 755 %{buildroot}%{jruby_vendordir}/jni/{arm-Linux,i386-Linux,x86_64-Linux}
ln -s %{_prefix}/lib/jffi/arm-Linux/libjffi.so %{buildroot}%{jruby_vendordir}/jni/arm-Linux/
ln -s %{_prefix}/lib/jffi/i386-Linux/libjffi.so %{buildroot}%{jruby_vendordir}/jni/i386-Linux/
ln -s %{_prefix}/lib64/jffi/x86_64-Linux/libjffi.so %{buildroot}%{jruby_vendordir}/jni/x86_64-Linux/

# jline in Fedora doesn't bundle jansi, we need to symlink it manually
ln -s `build-classpath jansi/jansi` %{buildroot}%{jruby_vendordir}/ruby/shared/readline/
xmvn-subst %{buildroot}%{jruby_vendordir}/ruby/shared/readline/

# remove what shouldn't be in lib/ dir
rm %{buildroot}%{jruby_vendordir}/pom*

# startup scripts
cp -a bin/{{j,}gem,{j,}irb,jruby} %{buildroot}%{_datadir}/%{name}/bin/

# /usr prefix startup scripts
install -d -m 755 %{buildroot}%{_bindir}
ln -s %{_datadir}/%{name}/bin/jgem  %{buildroot}%{_bindir}/gem-jruby
ln -s %{_datadir}/%{name}/bin/jirb  %{buildroot}%{_bindir}/irb-jruby
ln -s %{_datadir}/%{name}/bin/jruby %{buildroot}%{_bindir}/jruby

# Fedora integration stuff
# modify the JRuby executable to contain Fedora specific paths redefinitons
# we need to modify jruby{,sh,bash} to be sure everything is ok
sed -i 's|$FEDORA_JAVA_OPTS|-Dvendor.dir.general=%{jruby_vendordir}\
                            -Dsite.dir.general=%{jruby_sitedir}\
                            -Dvendor.dir.rubygems=%{rubygems_dir}|' \
    %{buildroot}%{_datadir}/%{name}/bin/jruby*

# install JRuby specific bits into system RubyGems
mkdir -p %{buildroot}%{rubygems_dir}/rubygems/defaults
cp -a lib/ruby/shared/rubygems/defaults/jruby.rb %{buildroot}%{rubygems_dir}/rubygems/defaults/

# Dump the macros into macros.jruby to use them to build other JRuby libraries.
mkdir -p %{buildroot}%{_rpmconfigdir}/macros.d
cat >> %{buildroot}%{_rpmconfigdir}/macros.d/macros.jruby << \EOF
%%jruby_libdir %%{_datadir}/%{name}/lib/ruby/2.0

# This is the general location for libs/archs compatible with all
# or most of the Ruby versions available in the Fedora repositories.
%%jruby_vendordir vendor_ruby
%%jruby_vendorlibdir %%{jruby_libdir}/%%{jruby_vendordir}
%%jruby_vendorarchdir %%{jruby_vendorlibdir}
EOF

%files  -f .mfiles
%doc COPYING LICENSE.RUBY LEGAL
%{_bindir}/%{name}
%{_bindir}/gem-jruby
%{_bindir}/irb-jruby
%{_datadir}/%{name}
# own the JRuby specific files under RubyGems dir
%{rubygems_dir}/rubygems/defaults/jruby.rb
# exclude bundled gems
%exclude %{jruby_vendordir}/ruby/1.9/rake*
# exclude all of the rubygems stuff
%exclude %{jruby_vendordir}/ruby/shared/*ubygems*
%exclude %{jruby_vendordir}/ruby/shared/rbconfig

%files devel
%{_rpmconfigdir}/macros.d/macros.jruby

%files javadoc -f .mfiles-javadoc
%doc COPYING LICENSE.RUBY LEGAL

%changelog
* Mon Oct 05 2015 Michal Srb <msrb@redhat.com> - 1.7.22-1
- Update to 1.7.22
- Fix FTBFS

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.7.20-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Mon May 18 2015 Michal Srb <msrb@redhat.com> - 1.7.20-1
- Update to 1.7.20
- Fix classpath
- Exclude bundled gems

* Fri May 15 2015 Michal Srb <msrb@redhat.com> - 1.7.19-2
- Install startup scripts: gem, irb

* Tue Dec 16 2014 Mo Morsi <mmorsi@redhat.com> - 1.7.19-1
- Update to latest jruby release
- Fix FTBFS (rhbz#1074264)
- Install RPM macros to %%{_rpmconfigdir}/macros.d (rhbz#1106973)

* Sun Jun 08 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.7.2-6.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Thu Aug 22 2013 Vít Ondruch <vondruch@redhat.com> - 1.7.2-5
- Use relative symlinks for compatibility with recent Java packaging macros.
- Fix Ant compatibility.

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.7.2-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Thu Jul 11 2013 Orion Poplawski <orion@cora.nwra.com> - 1.7.2-3
- Install the correct poms correctly

* Mon Jul 08 2013 Orion Poplawski <orion@cora.nwra.com> - 1.7.2-2
- Fix pom install
- Remove shipped bouncycastle jars

* Tue Feb 26 2013 Bohuslav Kabrda <bkabrda@redhat.com> - 1.7.2-1
- Update to JRuby 1.7.2.

* Fri Dec 07 2012 Bohuslav Kabrda <bkabrda@redhat.com> -1.7.1-2
- Included -devel subpackage with macros.jruby.
- Added missing Requires: jpackage-utils.
- Added a patch for sitedir path.

* Tue Dec 04 2012 Bohuslav Kabrda <bkabrda@redhat.com> - 1.7.1-1
- Update to JRuby 1.7.1.
- Update license tags.
- Include licensing files in all independent RPMs generated from this SRPM.
- Exclude the forgotten gems directory from vendordir.

* Fri Nov 30 2012 Bohuslav Kabrda <bkabrda@redhat.com> - 1.7.1-0.1.dev
- Update to JRuby 1.7.1.dev.
- Add missing R: and BR: apache-commons-logging

* Fri Nov 09 2012 Bohuslav Kabrda <bkabrda@redhat.com> - 1.7.0-2
- Don't move stuff from build_lib, the issue with including files is solved by
using non-existing file in jruby.jar.zip.includes in build.xml.
- Add missing Requires: snakeyaml.

* Tue Oct 23 2012 Bohuslav Kabrda <bkabrda@redhat.com> - 1.7.0-1
- Updated to JRuby 1.7.0.

* Thu Oct 11 2012 Bohuslav Kabrda <bkabrda@redhat.com> - 1.7.0-0.3.RC2
- Updated to JRuby 1.7.0.RC2.
- Rename jirb and jgem to irb-jruby and gem-jruby.

* Thu Oct 04 2012 Bohuslav Kabrda <bkabrda@redhat.com> - 1.7.0-0.2.RC1
- Use system RubyGems.
- Add path definition that brings JRuby closer to MRI.

* Mon Oct 01 2012 Bohuslav Kabrda <bkabrda@redhat.com> - 1.7.0-0.1.RC1
- Updated to JRuby 1.7.0.RC1.

* Tue Sep 11 2012 Bohuslav Kabrda <bkabrda@redhat.com> - 1.7.0-0.1.preview2
- Updated to JRuby 1.7.0.preview2.

* Thu May 17 2012 Vít Ondruch <vondruch@redhat.com> - 1.6.7.2-1
- Updated to JRuby 1.6.7.2.

* Fri Jan 13 2012 Mo Morsi <mmorsi@redhat.com> - 1.6.3-3
- rename jaffl dependency to jnr-ffi (BZ#723191)
- change build dep on rspec 1.x to 2.x

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.6.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Tue Aug 02 2011 Mo Morsi <mmorsi@redhat.com> - 1.6.3-1
- update to latest upstream release
- include missing symlink to jruby-yecht

* Wed Jul 06 2011 Mo Morsi <mmorsi@redhat.com> - 1.6.2-2
- install jruby to _datadir not _javadir
- remove windows specific files (exes, dlls, etc)

* Wed May 25 2011 Mo Morsi <mmorsi@redhat.com> - 1.6.2-1
- Updated to latest upstream release

* Tue Dec 07 2010 Mohammed Morsi <mmorsi@redhat.com> - 1.5.6-2
- Remove pre-built gems
- Started to add bits to get test suite in working order
- Added yecht bindings used internally in jruby

* Mon Dec 06 2010 Mohammed Morsi <mmorsi@redhat.com> - 1.5.6-1
- Updated jruby to latest upstream release
- Updates to conform to pkging guidelines

* Thu Dec 02 2010 Mohammed Morsi <mmorsi@redhat.com> - 1.5.5-1
- Updated jruby to latest upstream release

* Mon Oct 25 2010 Mohammed Morsi <mmorsi@redhat.com> - 1.5.3-1
- Updated jruby to latest upstream release

* Thu Jan 28 2010 Mohammed Morsi <mmorsi@redhat.com> - 1.4.0-1
- Unorphaned / updated jruby

* Fri Mar 6 2009 Conrad Meyer <konrad@tylerc.org> - 1.1.6-3
- debug_package nil, as this is a pure-java package (that can't
  be built with gcj).

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.6-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Thu Dec 18 2008 Conrad Meyer <konrad@tylerc.org> - 1.1.6-1
- Bump to 1.1.6.

* Fri Nov 28 2008 Conrad Meyer <konrad@tylerc.org> - 1.1.5-1
- Bump to 1.1.5.

* Mon Sep 8 2008 Conrad Meyer <konrad@tylerc.org> - 1.1.4-1
- Bump to 1.1.4.

* Tue Jul 29 2008 Conrad Meyer <konrad@tylerc.org> - 1.1.3-2
- Update jruby-fix-jruby-start-script.patch to work with faster
  class-loading mechanism introduced in JRuby 1.1.2.

* Sat Jul 19 2008 Conrad Meyer <konrad@tylerc.org> - 1.1.3-1
- Bump to 1.1.3.

* Wed May 21 2008 Conrad Meyer <konrad@tylerc.org> - 1.1.1-7
- Require joni and jline.

* Thu Apr 24 2008 Conrad Meyer <konrad@tylerc.org> - 1.1.1-6
- Bump because F-9 bumped.

* Thu Apr 24 2008 Conrad Meyer <konrad@tylerc.org> - 1.1.1-5
- BR and Requires openjdk.

* Tue Apr 22 2008 Conrad Meyer <konrad@tylerc.org> - 1.1.1-4
- Add check section.
- Removed patches 0 and 4 because they got incorporated in upstream.

* Mon Apr 7 2008 Conrad Meyer <konrad@tylerc.org> - 1.1-3
- Install all jruby to the prefix libdir/jruby, linking from /usr
  where needed.

* Sun Apr 6 2008 Conrad Meyer <konrad@tylerc.org> - 1.1-2
- Add a few missing Requires.
- Add some things that were missing from CP in the start script.

* Sun Mar 30 2008 Conrad Meyer <konrad@tylerc.org> - 1.1-1
- Bump to 1.1.
- Remove binary .jars.
- Minor cleanups in the specfile.
- Don't include jruby stdlib (for now).

* Sun Feb 24 2008 Conrad Meyer <konrad@tylerc.org> - 1.1-0.4.20080216svn
- Bump for 1.1rc2.

* Tue Jan 8 2008 Conrad Meyer <konrad@tylerc.org> - 1.1-0.3.20080108svn
- Bump for 1.1rc1.

* Sun Dec 9 2007 Conrad Meyer <konrad@tylerc.org> - 1.1-0.2.20071209svn
- SVN version bump.

* Mon Dec 3 2007 Conrad Meyer <konrad@tylerc.org> - 1.1-0.1.20071203svn
- Initial package created from ancient jpackage package

