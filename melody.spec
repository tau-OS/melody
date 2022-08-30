%global common_description %{expand:
An advanced rpm-ostree compose system}
 
Name:           melody
Summary:        An advanced rpm-ostree compose system
Version:        1
Release:        1%{?dist}
 
License:        GPLv3+
 
URL:            https://github.com/tau-OS/melody
Source0:        %{name}-%{version}.tar.gz
 
BuildArch:      noarch
 
BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros
 
BuildRequires:  gcc
BuildRequires:  git-core
BuildRequires:  /usr/bin/python
BuildRequires:  %py3_dist PyYAML
BuildRequires:  %py3_dist anytree
BuildRequires:  %py3_dist click
BuildRequires:  %py3_dist rich
 
Requires:       python3-dnf
 
%description %{common_description}
 
 
%package -n     python3-melody
Summary:        %{summary}
%description -n python3-melody %{common_description}
 
 
%prep
%autosetup -p1 
 
%generate_buildrequires
%pyproject_buildrequires -r
 
 
%build
%pyproject_wheel
 
%install
%pyproject_install
%pyproject_save_files melody
 
 
%files
%{_bindir}/melody
 
 
%files -n python3-melody -f %{pyproject_files}
%license LICENSE
%doc README.md
 
%exclude %dir %{python3_sitelib}/melody
%pycached %exclude %{python3_sitelib}/melody/__init__.py