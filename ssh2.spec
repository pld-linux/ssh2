%define	base_name	ssh
Summary:	Secure Shell - encrypts network communications with ipv6 support.
Summary(pl):	Secure Shell - kodowane po³±czenie sieciowe ze wsparciem dla IPv6
Name:		%{base_name}2
Version:	2.0.13
Release:	2
Group:		Utilities
Group(pl):	Narzêdzia
Copyright:	Non-commercially distributable
Source0:	ftp://ftp.cs.hut.fi/pub/ssh/%{base_name}-%{version}.tar.gz
Source1:	sshd.init
Source2:	ssh.pamd
Source3:	sshd.conf
Source4:	ssh.conf
Patch0:		ssh2-install-fix.patch
#Patch9:		ssh-pam.patch
#Patch10:	ssh-pam_env+expire.patch
URL:		http://www.cs.hut.fi/ssh/
BuildRequires:	gmp-devel
BuildRequires:	zlib-devel
BuildRequires:	xauth
BuildRoot:	/tmp/%{base_name}-%{version}-root

%define	_prefix	/usr

%description
Ssh (Secure Shell) a program for logging into a remote machine and for
executing commands in a remote machine.  It is intended to replace rlogin
and rsh, and provide secure encrypted communications between two untrusted
hosts over an insecure network.  X11 connections and arbitrary TCP/IP ports
can also be forwarded over the secure channel.

The 'i' form of the package is compiled with internal RSAREF and is
recommended for use outside the USA, the 'us' form is compiled for external
RSAREF and should be used within the USA. The 'us' version does not have the
IDEA encryption compiled in.

This is a base package. You will need to install at least one of ssh-clients
and ssh-server to really use ssh.

%description -l pl
Ssh (Secure Shell) jest programem s³u¿±cym do logowania siê na zdaln±
maszynê i do wykonywania na niej komend. Polecany jest jako zamiennik dla
rlogin i rsh poniewa¿ koduje ca³± transmisjê. Poza tym pozawala na
forwardowanie a przy okazji i kodowanie transmisji X11. Ta wersja ma
wsparcie dla PAM i systemu Kerberos V5.

Jest to jedynie pakiet podstawowy - je¶li chcesz korzystaæ z ssh musisz
zainstalowaæ tak¿e pakiet ssh-clients oraz ssh-server.

%package clients
Summary:	Clients for connecting to Secure Shell servers
Summary(pl):	Klient pozwalaj±cy na pod³±czenie siê do serwera Secure Shell
Group:		Utilities
Group(pl):	Narzêdzia
Requires:	%{name} = %{version} 

%description clients
This package includes the clients necessary to make encrypted connections
to SSH servers.

%description -l pl clients
Oprogramowanie klienckie dla ssh.

%package server
Summary:	Secure Shell protocol server (sshd)
Summary(pl):	Serwer (sshd) protoko³u Secure Shell
Group:		Daemons
Group(pl):	Serwery
Requires:	pam >= 0.66
Prereq:		/sbin/chkconfig
Requires:	%{name} = %{version} 

%description server
This package contains the secure shell daemon and its documentation.
The sshd is the server part of the secure shell protocol and allows
ssh clients to connect to your host.

%description -l pl server
Pakiet zawiera daemon Secure Shell oraz dokumentacjê. Sshd jest serwerem 
protoko³u Secure Shell umo¿liwiaj±cym pod³±czanie siê klientów do 
Twojego hosta.

%package extras
Summary:	Extra command for the secure shell protocol suite
Summary(pl):	Dodatkowe komendy dla obs³ugi protoko³u Secure Shell
Group:		Utilities
Group(pl):	Narzêdzia
Requires:	%{name} = %{version}

%description extras
This package contains the make_ssh_known_hosts perl script,
the ssh-askpass command and its documentation. They were moved
to the separate package to allow clean install of ssh even
on X11-less and perl-less machines (make_ssh_known_hosts is a perl script
and ssh-askpass uses X11 libraries.

%description -l pl extras
Pakiet zawiera skrypt perlowy make_ssh_known_hosts, ssh-askpass oraz 
dokumentacjê. Zosta³y przeniesione do oddzielnego pakietu co umo¿liwi³o 
instalowanie ssh nawet na maszynach nie posiadaj±cych X11 oraz perl'a 
(make_ssh_known_hosts jest skryptem perlowym a ssh-askpass u¿ywa 
bibliotek X11).

%define _sysconfdir /etc/ssh

%prep
%setup -q -n%{base_name}-%{version}

%patch -p0

%build
aclocal
autoconf

LDFLAGS="-s"; export LDFLAGS 
%configure \
	--with-etcdir=%{_sysconfdir} \
	--with-libwrap \
	--disable-suid-ssh \
	--with-x \
	--with-pam \
	--without-kerberos5 \
	--without-socks5 \
	--without-rsaref  
make

%install

rm -rf $RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT/{%{_mandir},etc/{ssh,pam.d,rc.d/init.d}}

make \
	DESTDIR=$RPM_BUILD_ROOT \
	install

touch $RPM_BUILD_ROOT%{_sysconfdir}/ssh_host_key

install %{SOURCE2} $RPM_BUILD_ROOT/etc/pam.d/ssh
install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/sshd
install %{SOURCE3} $RPM_BUILD_ROOT%{_sysconfdir}/ssh_config
install %{SOURCE3} $RPM_BUILD_ROOT%{_sysconfdir}/sshd_config

rm $RPM_BUILD_ROOT%{_mandir}/man8/sshd.8
cp $RPM_BUILD_ROOT%{_mandir}/man8/sshd2.8 $RPM_BUILD_ROOT%{_mandir}/man8/sshd.8

gzip -9fn $RPM_BUILD_ROOT%{_mandir}/man[18]/* \
	CHANGES BUG.REPORT SSH2.QUICKSTART README* FAQ

%clean
rm -rf $RPM_BUILD_ROOT

%pre server
if [ -f /etc/ssh/ssh_config ]; then
   mv /etc/ssh/ssh_config /etc/ssh/ssh1_config
fi

%post server
/sbin/chkconfig --add sshd

if [ -f /var/run/sshd.pid ]; then
    /etc/rc.d/init.d/sshd restart >&2
fi

%post
if [ ! -f %{_sysconfdir}/ssh_host_key -o ! -s %{_sysconfdir}/ssh_host_key ]; then
	if [ -f /etc/ssh_host_key -a -s /etc/ssh_host_key ]; then
		mv /etc/ssh_host_key /etc/ssh_host_key.pub %{_sysconfdir} || :
		mv /etc/ssh_known_hosts %{_sysconfdir} >/dev/null 2>&1 ||:
		mv /etc/ssh_random_seed %{_sysconfdir} >/dev/null 2>&1 ||:
	else
		%{_bindir}/ssh-keygen -b 1024 -f %{_sysconfdir}/ssh_host_key -N '' >&2
	fi
fi  

%preun server
if [ "$1" = 0 ]; then
	/etc/rc.d/init.d/sshd stop >&2
	/sbin/chkconfig --del sshd
fi

%files
%defattr(644,root,root,755)
%doc CHANGES.gz READM* FAQ.gz 

%attr(755,root,root) %{_bindir}/ssh-keygen*
#%attr(4755,root,root) %{_bindir}/ssh-singer2
%attr(755,root,root) %{_bindir}/scp*

%{_mandir}/man1/ssh-keygen.1*
%{_mandir}/man1/scp.1*

%attr(750,root,root) %dir %{_sysconfdir}

%files server
%defattr(644,root,root,755)
%attr(755,root,root) %{_sbindir}/sshd*
%{_mandir}/man8/*

%attr(750,root,root) %config /etc/rc.d/init.d/sshd

%attr(640,root,root) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/sshd_config
%attr(640,root,root) %config %verify(not size mtime md5) /etc/pam.d/*

%files extras
%defattr(644,root,root,755)

%attr(755,root,root) %{_bindir}/ssh-askpass*

%files clients
%defattr(644,root,root,755)

%attr(640,root,root) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/ssh_config

%attr(755,root,root) %{_bindir}/ssh
%attr(755,root,root) %{_bindir}/ssh2

%attr(755,root,root) %{_bindir}/ssh-agent*
%attr(755,root,root) %{_bindir}/ssh-add*

%{_mandir}/man1/ssh-agent.1*
%{_mandir}/man1/ssh-add.1*
%{_mandir}/man1/ssh.1*
