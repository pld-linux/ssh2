%define	base_name	ssh
Summary:	Secure Shell - encrypts network communications with ipv6 support
Summary(pl):	Secure Shell - kodowane po³±czenie sieciowe ze wsparciem dla IPv6
Name:		%{base_name}2
Version:	3.2.3
Release:	0.1
Group:		Applications
License:	non-commercial (see LICENSE)
Source0:	ftp://ftp.ssh.com/pub/ssh/%{base_name}-%{version}.tar.gz
Source1:	sshd.init
Source2:	ssh.pamd
Source3:	sshd.conf
Source4:	ssh.conf
Patch0:		%{name}-acfix.patch
URL:		http://www.cs.hut.fi/ssh/
BuildRequires:	XFree86-devel
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	libwrap-devel
BuildRequires:	ncurses-devel
BuildRequires:	pam-devel
BuildRequires:	xauth
# it uses internal zlib with functions renamed by hacks
#BuildRequires:	zlib-devel
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_sysconfdir	/etc/ssh

%description
Ssh (Secure Shell) a program for logging into a remote machine and for
executing commands in a remote machine. It is intended to replace
rlogin and rsh, and provide secure encrypted communications between
two untrusted hosts over an insecure network. X11 connections and
arbitrary TCP/IP ports can also be forwarded over the secure channel.

This is a base package. You will need to install at least one of
ssh-clients and ssh-server to really use ssh.

%description -l pl
Ssh (Secure Shell) jest programem s³u¿±cym do logowania siê na zdaln±
maszynê i do wykonywania na niej poleceñ. Polecany jest jako zamiennik
dla rlogin i rsh poniewa¿ koduje ca³± transmisjê. Poza tym pozawala na
forwardowanie a przy okazji i kodowanie transmisji X11. Ta wersja ma
wsparcie dla PAM.

Jest to jedynie pakiet podstawowy - je¶li chcesz korzystaæ z ssh
musisz zainstalowaæ tak¿e pakiet ssh-clients oraz ssh-server.

%package clients
Summary:	Clients for connecting to Secure Shell servers
Summary(pl):	Klient pozwalaj±cy na pod³±czenie siê do serwera Secure Shell
Group:		Applications
Requires:	%{name} = %{version}

%description clients
This package includes the clients necessary to make encrypted
connections to SSH servers.

%description clients -l pl
Oprogramowanie klienckie dla ssh.

%package server
Summary:	Secure Shell protocol server (sshd)
Summary(pl):	Serwer (sshd) protoko³u Secure Shell
Group:		Daemons
Requires:	pam >= 0.66
Prereq:		/sbin/chkconfig
Requires:	%{name} = %{version}
Prereq:		rc-scripts

%description server
This package contains the secure shell daemon and its documentation.
The sshd is the server part of the secure shell protocol and allows
ssh clients to connect to your host.

%description server -l pl
Pakiet zawiera daemon Secure Shell oraz dokumentacjê. Sshd jest
serwerem protoko³u Secure Shell umo¿liwiaj±cym pod³±czanie siê
klientów do Twojego hosta.

%package extras
Summary:	Extra commands for the secure shell protocol suite
Summary(pl):	Dodatkowe polecenia dla obs³ugi protoko³u Secure Shell
Group:		Applications
Requires:	%{name} = %{version}

%description extras
This package contains the make_ssh_known_hosts perl script, the
ssh-askpass command and its documentation. They were moved to the
separate package to allow clean install of ssh even on X11-less and
perl-less machines (make_ssh_known_hosts is a perl script and
ssh-askpass uses X11 libraries).

%description extras -l pl
Pakiet zawiera skrypt perlowy make_ssh_known_hosts, ssh-askpass oraz
dokumentacjê. Zosta³y przeniesione do oddzielnego pakietu co
umo¿liwi³o instalowanie ssh nawet na maszynach nie posiadaj±cych X11
oraz perla (make_ssh_known_hosts jest skryptem perlowym a ssh-askpass
u¿ywa bibliotek X11).

%prep
%setup -q -n%{base_name}-%{version}
%patch -p1

%build
%{__aclocal}
%{__autoconf}
%{__autoheader}
%{__automake}
%configure \
	--with-etcdir=%{_sysconfdir} \
	--with-libwrap \
	--disable-suid-ssh \
	--with-x \
	--with-pam \
	--without-kerberos5 \
	--without-socks5 \
	--without-rsaref
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/{%{_mandir},etc/{ssh,pam.d,rc.d/init.d}}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

touch $RPM_BUILD_ROOT%{_sysconfdir}/ssh_host_key

install %{SOURCE2} $RPM_BUILD_ROOT/etc/pam.d/ssh
install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/sshd
#install %{SOURCE3} $RPM_BUILD_ROOT%{_sysconfdir}/ssh_config
#install %{SOURCE3} $RPM_BUILD_ROOT%{_sysconfdir}/sshd_config

for n in scp ssh-keygen ssh-probe sftp ssh-add ssh-agent ssh ; do
	rm -f $RPM_BUILD_ROOT%{_mandir}/man1/${n}.1
	echo ".so ${n}2.1" > $RPM_BUILD_ROOT%{_mandir}/man1/${n}.1
done
rm -f $RPM_BUILD_ROOT%{_mandir}/man8/sshd.8
echo '.so sshd2.1' > $RPM_BUILD_ROOT%{_mandir}/man8/sshd.8

%clean
rm -rf $RPM_BUILD_ROOT

%pre server
if [ -f /etc/ssh/ssh_config ]; then
	mv -f /etc/ssh/ssh_config /etc/ssh/ssh1_config
fi

%post server
/sbin/chkconfig --add sshd

if [ -f /var/run/sshd.pid ]; then
	/etc/rc.d/init.d/sshd restart >&2
fi

%post
if [ ! -f %{_sysconfdir}/ssh_host_key -o ! -s %{_sysconfdir}/ssh_host_key ]; then
	if [ -f /etc/ssh_host_key -a -s /etc/ssh_host_key ]; then
		mv -f /etc/ssh_host_key /etc/ssh_host_key.pub %{_sysconfdir} || :
		mv -f /etc/ssh_known_hosts %{_sysconfdir} >/dev/null 2>&1 ||:
		mv -f /etc/ssh_random_seed %{_sysconfdir} >/dev/null 2>&1 ||:
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
%doc CHANGES FAQ HOWTO* LICENSE NEWS README* REGEX* RFC.* SSH2.QUICKSTART drafts/*.txt
%attr(755,root,root) %{_bindir}/ssh-keygen*
%attr(755,root,root) %{_bindir}/ssh-probe*
#%attr(4755,root,root) %{_bindir}/ssh-signer2
%attr(755,root,root) %{_bindir}/scp*
%{_mandir}/man1/ssh-keygen*.1*
%{_mandir}/man1/ssh-probe*.1*
%{_mandir}/man1/scp*.1*
%attr(750,root,root) %dir %{_sysconfdir}
%attr(750,root,root) %dir %{_sysconfdir}/subconfig

%files server
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/sftp-server*
%attr(755,root,root) %{_bindir}/ssh-dummy-shell
%attr(755,root,root) %{_sbindir}/sshd*
%{_mandir}/man1/ssh-dummy-shell.1*
%{_mandir}/man5/sshd*.5*
%{_mandir}/man8/*
%attr(754,root,root) %config /etc/rc.d/init.d/sshd
%attr(640,root,root) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/sshd2_config
%attr(640,root,root) %config(noreplace) %verify(not size mtime md5) /etc/pam.d/*

%files extras
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/ssh-askpass*

%files clients
%defattr(644,root,root,755)
%attr(640,root,root) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/ssh2_config
%attr(755,root,root) %{_bindir}/sftp
%attr(755,root,root) %{_bindir}/sftp2
%attr(755,root,root) %{_bindir}/ssh
%attr(755,root,root) %{_bindir}/ssh2
%attr(755,root,root) %{_bindir}/ssh-agent*
%attr(755,root,root) %{_bindir}/ssh-add*
%{_mandir}/man1/sftp.1*
%{_mandir}/man1/sftp2.1*
%{_mandir}/man1/ssh-agent*.1*
%{_mandir}/man1/ssh-add*.1*
%{_mandir}/man1/ssh.1*
%{_mandir}/man1/ssh2.1*
%{_mandir}/man1/sshregex.1*
%{_mandir}/man5/ssh2_config.5*
